---
title: "[Security] CanisterSprawl — npm·PyPI·Docker Hub 공급망을 48시간 만에 강타한 자가전파 웜"
date: 2026-04-29 09:00:00 +09:00
categories: [Security]
tag: [supply-chain, npm, PyPI, 악성코드, 자격증명탈취]
---

## 서론

소프트웨어 공급망 공격이 한층 더 진화했다. 2026년 4월 21일부터 22일 사이, 단 48시간 만에 npm, PyPI, Docker Hub 세 개의 패키지 생태계를 동시에 강타한 조직적 공급망 공격이 발생했다.

이 공격들의 중심에 있는 것이 바로 `CanisterSprawl`이다. 보안 업체 Socket과 StepSecurity가 명명한 이 웜은, 개발자 머신이나 CI/CD 파이프라인에 한 번 침투하는 것으로 끝나지 않는다. 피해자가 보유한 npm 퍼블리시 토큰을 탈취해 스스로를 다른 패키지에 심은 뒤 재배포하는, **자가전파(self-propagating)** 특성을 가지고 있다. PyPI 자격증명이 있으면 Python 생태계로도 건너뛴다.

더 눈에 띄는 건 C2(Command & Control) 채널이다. CanisterSprawl은 블록체인 기반 스마트 컨트랙트인 **ICP(Internet Computer Protocol) 캐니스터**를 탈취 데이터 수신 채널로 사용한다. 도메인 테이크다운이나 DNS 싱크홀링으로는 막을 수 없는 검열 저항성 인프라다. 이 선택 하나만으로도 공격자가 단순한 기회주의적 스크립트 키디가 아님을 알 수 있다.

같은 시간대에 Bitwarden CLI npm 패키지가 오염됐고, 334명의 개발자가 악성 버전을 설치했다. Bitwarden은 1,000만 이상 사용자와 5만 개 이상 기업이 쓰는 패스워드 관리 도구다. 자격증명 관리 도구 자체가 자격증명 탈취의 매개체가 된 아이러니한 상황이었다.

백엔드 개발자, 데브섹옵스 팀, 그리고 오픈소스 패키지를 npm 혹은 PyPI에 배포한 경험이 있는 누구든 이 사건을 주의 깊게 볼 필요가 있다.

## 본론

### 공격의 배경: TeamPCP 공급망 캠페인

SANS ISC(Internet Storm Center)는 이번 공격들을 독립적인 사건이 아닌 `TeamPCP`라는 위협 행위자의 지속적 캠페인으로 추적하고 있다. TeamPCP는 올해 초 26일간의 침묵 이후, 4월 21~22일에 Checkmarx KICS, Bitwarden CLI, xinference PyPI 패키지를 동시에 공략하는 방식으로 복귀했다. SANS ISC는 이를 "TeamPCP Supply Chain Campaign Update 008"로 기록했다. Tier 1 미디어의 광범위한 보도가 시작된 시점이기도 하다.

The Register도 4월 27일 "Ongoing supply-chain attack targets security, dev tools"라는 제목으로 이 캠페인을 독립 기사로 다뤘다. 공격의 공통된 목표는 하나다. 개발자와 CI/CD 파이프라인 환경에서 자격증명을 대량 탈취하는 것이다.

### 공격 1: npm — CanisterSprawl 웜의 시작

4월 21일, npm에 등록된 `pgserve` 패키지(Node.js용 PostgreSQL 서버)의 악성 버전이 등장했다. Socket과 StepSecurity가 분석한 공격 메커니즘은 다음과 같다.

`npm install`이 실행되는 순간 `postinstall` 훅이 자동으로 실행된다.

```json
{
  "scripts": {
    "postinstall": "node .malicious/harvest.js"
  }
}
```

악성 스크립트는 개발자 환경에서 약 **40여 개 범주**의 자격증명을 정규식으로 스캔해 수집한다.

- npm 퍼블리시 토큰 (`.npmrc`)
- PyPI API 토큰 (`.pypirc`)
- SSH 개인키 (`~/.ssh/`)
- AWS, GCP, Azure 자격증명 파일
- 환경변수 (`.env`, `~/.bashrc`, `~/.zshrc`)
- 암호화폐 지갑 키

수집된 데이터는 ICP 캐니스터를 통해 외부로 반출된다.

#### 자가전파: 웜이 웜을 만든다

CanisterSprawl이 단순 정보탈취 악성코드와 다른 결정적 차이는 자가전파 로직이다. npm 퍼블리시 토큰을 탈취하면, 스크립트는 해당 개발자 계정으로 퍼블리시할 수 있는 모든 패키지 목록을 조회한다. 패키지마다 패치 버전을 하나 올린 뒤 악성 코드를 주입해 재배포한다.

```text
피해자 A의 환경에서 npm 토큰 탈취
  → A가 관리하는 패키지 목록 조회
  → 각 패키지에 웜 코드 삽입 후 버전 범프 → 재배포
  → A의 패키지를 설치하는 B, C, D...
    → 각자 환경에서 동일한 과정 반복
```

이 과정이 반복되면 피해자의 패키지를 구독하는 다른 개발자와 프로젝트까지 감염이 전파된다. PyPI 자격증명까지 확보된 경우, `Twine`을 통해 Python 패키지 생태계로도 건너뛰며 크로스-에코시스템 전파가 이루어진다. Socket과 StepSecurity는 이 웜이 연쇄 감염을 통해 Namastex Labs 관련 네임스페이스에서 최소 16개의 악성 버전을 확산시켰음을 확인했다.

#### ICP 캐니스터 C2: 왜 막을 수 없나

공격자는 탈취된 데이터의 수신 채널로 **Internet Computer Protocol(ICP) 캐니스터**를 선택했다. ICP 캐니스터는 블록체인 위에 배포된 변경 불가능한 스마트 컨트랙트다.

- 도메인 레지스트라 테이크다운 불가
- DNS 싱크홀링 불가
- 단일 서버 압수 불가 (분산 노드)

법 집행 기관의 일반적인 악성코드 인프라 차단 방법이 통하지 않는다. 보안 연구자들은 이 전술을 두고 "공격 인프라의 검열 저항성이 공격 페이로드만큼 중요해진 시대"라고 평가했다. CSA Labs는 이 점을 공식 연구 노트에서 특히 강조하며, 기존 인프라 테이크다운 기반 대응이 이 유형의 공격에는 효과적이지 않다고 지적했다.

### 공격 2: PyPI — xinference 패키지 오염

4월 22일, 머신러닝 모델 서빙 프레임워크 `xinference`의 PyPI 패키지에 악성 코드가 삽입된 세 개의 연속 릴리스가 배포됐다. SANS ISC는 이를 TeamPCP에 의한 것으로 귀속시켰다.

공격 페이로드는 2단계 구조였다.

1. **1단계**: 인코딩된 두 번째 단계 수집기를 디코딩
2. **2단계**: SSH 키, 클라우드 자격증명, 환경변수, 암호화폐 지갑을 체계적으로 수집해 외부 전송

xinference는 LLM 및 VLM(비전-언어 모델) 추론 서빙에 활용되는 도구로, ML 엔지니어와 AI 인프라 팀에서 주로 사용한다. AI 인프라 환경의 자격증명을 표적으로 삼은 명확한 의도가 읽힌다. 클라우드 자격증명을 탈취하면 학습 클러스터, S3 버킷, 모델 가중치 스토리지까지 접근할 수 있기 때문이다.

### 공격 3: Docker Hub — Checkmarx KICS 통한 Bitwarden CLI 연쇄 오염

같은 날, GitGuardian의 분석은 Checkmarx KICS(Keeping Infrastructure as Code Secure) 컨테이너 이미지의 오염과 이를 통한 `@bitwarden/cli` npm 패키지 감염 연쇄를 밝혔다.

Checkmarx KICS의 초기 침해는 이미 3월 23일에 시작됐다. 침해된 GitHub 저장소 접근을 발판으로 Dependabot 자동화 봇을 악용해 `@bitwarden/cli` npm 패키지에 악성 버전 배포 채널을 확보했다. 4월 22일에 npm에 게시된 악성 `@bitwarden/cli` 버전은 **334명의 개발자**가 단기간에 설치했다.

Bitwarden CLI는 **1,000만 이상의 사용자**와 5만 개 이상의 기업이 사용하는 패스워드 관리 솔루션의 커맨드라인 도구다. GitGuardian은 이 건에서 GitHub을 C2로 활용하는 새로운 Cloudflare 기반 엑스필트레이션 도메인도 발견했으며, 이를 TeamPCP의 인프라 확장 징후로 분석했다.

### 피해 범위와 대응 현황

현재까지 직접 확인된 피해자는 334명의 Bitwarden CLI 설치자다. 다만 자가전파 특성으로 인한 이차 피해는 집계 중이다. npm과 PyPI 양쪽 레지스트리 모두 악성 버전을 제거하고 영향을 받은 계정의 토큰을 무효화하는 조치를 취했다.

Socket은 실시간 패키지 분석 기능으로 CanisterSprawl 패턴을 탐지하고 있으며, StepSecurity는 postinstall 훅 모니터링 솔루션을 통해 유사 공격 감지를 지원하고 있다. SANS ISC는 이번 사건을 기점으로 TeamPCP가 멀티-에코시스템 동시 공격 역량을 갖춘 성숙한 위협 행위자임이 확인됐다고 평가했다.

### 개발자와 팀이 해야 할 일

**즉시 조치:**
- `npm audit` 실행 후 `postinstall` 훅이 있는 의존성 전수 검토
- `.npmrc`, `.pypirc`에 저장된 토큰 즉시 교체 및 재발급
- CI/CD 파이프라인의 시크릿 스토어 전수 점검
- 4월 22일 전후로 Bitwarden CLI를 설치했다면 토큰 교체 필수

**장기 대응:**
- `npm install --ignore-scripts` 플래그 사용 또는 postinstall 훅 실행 정책 도입
- 패키지 버전 고정(lock) 및 integrity hash 검증 (`npm ci` 사용 습관화)
- CI/CD 환경에서 최소 권한 원칙 적용: npm 토큰은 특정 패키지에만 퍼블리시 권한 부여
- Socket, StepSecurity 같은 공급망 보안 스캐너 도입 검토

```bash
# postinstall 훅 없이 설치하는 안전한 방법
npm install --ignore-scripts

# 혹은 .npmrc에 영구 설정
echo "ignore-scripts=true" >> ~/.npmrc
```

## 정리

- 4월 21~22일, npm(pgserve · CanisterSprawl), PyPI(xinference), Docker Hub(Checkmarx KICS → Bitwarden CLI) 세 생태계를 동시에 노린 공급망 공격이 발생했다.
- CanisterSprawl은 단순 정보탈취를 넘어 피해자의 npm 토큰으로 스스로를 다른 패키지에 심어 재배포하는 자가전파 웜이다. 약 40여 개 범주의 자격증명을 수집한다.
- C2로 ICP 블록체인 캐니스터를 사용해 도메인 테이크다운·DNS 싱크홀링이 불가능한 검열 저항 인프라를 구축했다.
- Bitwarden CLI 오염은 334명 설치자로 직접 확인됐고, 패스워드 관리 도구가 자격증명 탈취 매개체가 됐다는 점에서 잠재적 파급력이 크다.
- SANS ISC는 이를 TeamPCP의 조직적 캠페인으로 귀속시키며, 멀티-에코시스템 동시 공격 역량을 갖춘 성숙한 위협 행위자의 부상으로 평가했다.
- postinstall 훅 제한, 토큰 즉시 교체, 공급망 스캐너 도입이 핵심 대응책이다.

## Reference

- [Self-Propagating Supply Chain Worm Hijacks npm Packages to Steal Developer Tokens — The Hacker News](https://thehackernews.com/2026/04/self-propagating-supply-chain-worm.html)
- [No Off Season: Three Supply Chain Campaigns Hit npm, PyPI, and Docker Hub in 48 Hours — GitGuardian Blog](https://blog.gitguardian.com/three-supply-chain-campaigns-hit-npm-pypi-and-docker-hub-in-48-hours/)
- [CanisterSprawl: The Self-Propagating npm Supply Chain Worm — CSA Labs](https://labs.cloudsecurityalliance.org/research/csa-research-note-npm-canistersprawl-supply-chain-worm-20260/)
- [New npm supply-chain attack self-spreads to steal auth tokens — BleepingComputer](https://www.bleepingcomputer.com/news/security/new-npm-supply-chain-attack-self-spreads-to-steal-auth-tokens/)
- [TeamPCP Supply Chain Campaign Update 008 — SANS ISC](https://isc.sans.edu/diary/TeamPCP+Supply+Chain+Campaign+Update+008/32926/)
- [Ongoing supply-chain attack targets security, dev tools — The Register](https://www.theregister.com/2026/04/27/supply_chain_campaign_targets_security/)
