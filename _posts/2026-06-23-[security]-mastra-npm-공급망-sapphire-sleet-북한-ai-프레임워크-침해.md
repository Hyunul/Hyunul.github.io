---
title: "[security] 북한 Sapphire Sleet, Mastra AI npm 패키지 144개 장악 — 88분 공급망 공격"
date: 2026-06-23 08:00:00 +09:00
categories: [security]
tag: [supply-chain, npm, North-Korea, Sapphire-Sleet, Mastra, backdoor]
---

## 서론

2026년 6월 17일 새벽, JavaScript AI 개발자 생태계를 겨냥한 정교한 공급망 공격이 벌어졌다. 공격자들은 단 88분 만에 Mastra AI 프레임워크의 npm 패키지 140개 이상을 악성 코드로 오염시켰다. `npm install` 한 줄을 실행한 수많은 개발자와 CI/CD 파이프라인이 북한 정보기관과 연계된 그룹의 백도어 설치 대상이 될 수 있었다.

마이크로소프트 위협 인텔리전스팀은 6월 19일 공식 보고서를 통해 이번 공격을 **Sapphire Sleet(BlueNoroff, APT38)**에 "높은 신뢰도"로 귀속했다. 같은 그룹이 올해 3월에도 Axios HTTP 클라이언트를 겨냥한 유사한 npm 공급망 공격을 수행한 바 있어, 이번은 그 후속이자 업그레이드 버전에 해당한다.

Mastra는 빠르게 성장하는 JavaScript AI 에이전트 프레임워크다. `@mastra/core` 패키지 하나만 해도 주간 다운로드가 약 918,000건에 달하며, 생태계 전체로는 주간 110만 건 이상이다. 이번 공격의 잠재적 피해 반경이 얼마나 넓었는지를 짐작하게 해주는 숫자다.

AI 개발 도구 생태계가 국가 지원 위협 행위자의 주요 타깃이 됐다는 사실은, 개발자들이 사용하는 패키지 하나하나에 공급망 보안 시각을 적용해야 한다는 것을 다시금 상기시킨다.

## 본론

### 공격 타임라인: 88분의 속전속결

마이크로소프트의 보고서에 따르면, 이번 공격은 이틀에 걸쳐 단계적으로 진행됐다.

**6월 16일 07:05 UTC** — `easy-day-js@1.11.21`이 npm에 배포됐다. 이 버전은 악성 코드가 없는 클린 패키지였다. 공격자가 미리 "합법적인" 버전을 심어두고, 피해자 시스템에 의존성 캐시나 잠금 파일 없이 자동으로 선택될 다음 버전을 준비하는 단계였다.

**6월 17일 01:01 UTC** — `easy-day-js@1.11.22`가 배포됐다. 이번에는 악성 `postinstall` 훅이 삽입된 무기화된 버전이었다.

**6월 17일 01:20 UTC** — 19분 후, `mastra@1.13.1`을 포함한 140개 이상의 `@mastra` 스코프 패키지가 일제히 업데이트됐다. 이 패키지들은 이제 악성 `easy-day-js@1.11.22`를 의존성으로 포함했다.

이 모든 과정이 01:01부터 01:20, 즉 88분 이내에 자동화된 방식으로 완료됐다. npm 메인테이너 계정 하나를 탈취하고 나면, 나머지는 스크립트가 처리한 것이다.

### SemVer를 역이용한 자동 악성 버전 주입

이번 공격의 교묘함은 npm의 의존성 해석 방식을 정확히 파고들었다는 점에 있다.

대부분의 `package.json`은 캐럿(`^`) 기호로 버전 범위를 지정한다. 예를 들어 `^1.11.21`이라고 쓰면, npm은 메이저 버전(1)이 같은 범위에서 가장 최신 버전을 자동으로 선택한다.

```json
{
  "dependencies": {
    "@mastra/core": "^1.13.0"
  }
}
```

공격자는 이 원칙을 역이용했다. `1.13.1`이라는 패치 버전(마이너 업그레이드)을 악성 코드가 들어간 버전으로 배포했고, `^1.13.0`으로 고정된 수많은 프로젝트가 `npm install` 실행 시 자동으로 `1.13.1`을 선택하게 됐다.

`package-lock.json`을 커밋하지 않거나 `npm ci` 대신 `npm install`을 CI에서 사용하는 프로젝트들은 별도 조작 없이 악성 버전을 당겨받는 상황이었다.

### 3단계 페이로드: 정교한 감염 사슬

마이크로소프트가 분석한 페이로드는 총 3단계로 구성된 정교한 감염 사슬이었다.

**Stage 0 — 드로퍼 실행**

악성 `postinstall` 훅은 패키지 설치 직후 자동 실행되며, 4,572바이트 분량의 난독화된 드로퍼를 실행했다. 이 드로퍼는 세 가지 역할을 수행했다:

```text
1. TLS 인증서 검증 비활성화 (C2 통신 탐지 우회 목적)
2. 추적 마커(tracking marker) 드롭
3. C2(명령 제어) 서버에 접속 → Stage 1 코드 수신
```

**Stage 1 — 영속성 있는 Node.js 임플란트**

C2 서버에서 수신한 코드는 약 41KB 분량의 크로스플랫폼 Node.js 태스킹 클라이언트였다. 이 임플란트는 랜덤하게 명명된 `.js` 파일로 저장된 뒤, 완전히 분리된(detached) 숨겨진 창(window-hidden) Node.js 프로세스로 실행됐다. 사용자 로그아웃 이후에도, 재부팅 이후에도 살아남는 구조였다.

**Stage 2 — 풀 원격 제어**

Stage 1이 C2와 연결을 확립한 시스템에서는 추가 페이로드가 배포됐다:

```text
- 리플렉티브 .NET 어셈블리 인젝션
- PowerShell 백도어 배포
- Microsoft Defender 제외 목록 추가 (탐지 회피)
- 재부팅 이후에도 지속되는 시스템 서비스 등록
- 암호화폐 지갑 탈취 모듈 실행
- 브라우저 히스토리 및 자동완성 데이터 수집
- 호스트 정찰 (네트워크, 프로세스, 파일 시스템)
```

즉, 개발자 노트북에서 `npm install`을 실행하는 것만으로, 백그라운드에서 북한의 원격 제어 백도어가 설치되는 구조였다.

### 귀속 분석: Sapphire Sleet의 일관된 패턴

마이크로소프트가 이번 공격을 Sapphire Sleet에 귀속한 근거는 이전 공격들과의 기술적 연속성이다.

Sapphire Sleet은 북한 정찰총국(RGB)과 연계된 국가 지원 위협 행위자로, BlueNoroff 또는 APT38로도 추적된다. 과거에는 금융 기관, 암호화폐 거래소, 블록체인 기업을 주로 노렸지만, 최근에는 개발자 환경을 통한 공급망 공격으로 전략을 확대하고 있다.

공통 TTPs(전술·기술·절차):
- npm 메인테이너 계정 탈취 후 악성 패키지 배포
- `postinstall` 훅을 이용한 초기 실행 (사용자 개입 없음)
- TLS 검증 비활성화를 통한 C2 통신 난독화
- 암호화폐 지갑 탈취와 함께 영구적 원격 접근 확보

같은 수법이 올해 3월 Axios HTTP 클라이언트를 겨냥한 공격에서도 사용됐다. Axios는 주간 수억 건이 다운로드되는 초대형 패키지다. 당시 공격의 피해 범위가 얼마였는지는 아직 완전히 공개되지 않았다. 이번 Mastra 공격은 패턴과 도구가 거의 동일하다.

### 실제 피해 범위

Mastra 생태계의 주간 다운로드가 110만 건 이상이지만, 실제 시스템 침해로 이어진 건수는 이보다 훨씬 적을 것으로 추정된다. 악성 버전이 배포된 시간 동안 `npm install`을 실행한 프로젝트 중, C2 서버와의 통신이 성공적으로 이루어진 경우에만 백도어가 설치되기 때문이다. 기업 환경에서는 방화벽이나 egress 필터링이 C2 통신을 차단했을 가능성도 있다.

마이크로소프트의 보고서 발표 이후 Mastra 측은 악성 버전을 신속하게 npm에서 제거하고 정상 버전으로 대체했다.

### npm 생태계 보안의 구조적 한계

이번 사건은 npm 생태계가 가진 구조적 취약점을 다시 한번 드러냈다.

**메인테이너 계정 보안**: npm 패키지 배포 권한은 계정 하나만 탈취하면 얻을 수 있다. npm은 2FA를 권장하지만, FIDO2 하드웨어 키 같은 강력한 방식을 의무화하는 조직은 아직 소수다. `ehindero` 계정이 어떻게 탈취됐는지에 대한 구체적인 경위는 아직 공개되지 않았다.

**postinstall 훅의 이중성**: `package.json`의 `scripts.postinstall`은 의존성 설치 직후 자동 실행되는 편리한 기능이다. 그러나 악용 시, 설치 과정 자체가 공격 실행으로 이어진다. `--ignore-scripts` 옵션으로 비활성화할 수 있지만 관행적으로 사용되지 않는다.

**SemVer 자동 해석**: 버전 범위 표기(`^`, `~`)는 편의를 위해 많이 쓰이지만, 예상치 못한 악성 패치 버전의 자동 수락 위험을 내포한다. `package-lock.json`을 항상 커밋하고 CI에서 `npm ci`를 사용하면 특정 버전에 고정되어 이 위험을 크게 낮출 수 있다.

## 정리

- 북한 국가 지원 해킹 그룹 Sapphire Sleet이 Mastra AI 프레임워크 npm 패키지 140개 이상을 88분 만에 오염 (2026년 6월 17일)
- 공격 흐름: npm 메인테이너 계정 탈취 → SemVer 패치 버전 악성 업데이트 → postinstall 훅 자동 실행 → 3단계 페이로드 (드로퍼 → Node.js 임플란트 → PowerShell 백도어 + 암호화폐 탈취)
- 같은 그룹이 2026년 3월 Axios HTTP 클라이언트에도 동일 수법 사용
- 방어 체크리스트:
  - npm 배포 계정에 FIDO2 하드웨어 키 필수화
  - `package-lock.json` 항상 커밋, CI에서 `npm install` 대신 `npm ci` 사용
  - 신뢰하지 않는 패키지 설치 시 `--ignore-scripts` 옵션 적용
  - SBOM(소프트웨어 구성 명세서) 기반 의존성 모니터링 도입
  - postinstall 실행 시 아웃바운드 네트워크 접근 모니터링
  - npm 패키지의 postinstall 스크립트 내용 코드리뷰 절차 추가
- 업계 반응: Orca Security와 CyberPress는 공격 메커니즘을 상세히 분석한 보고서를 공개했다. 마이크로소프트는 공식 블로그에서 유사 공격 방어를 위한 npm 패키지 보안 권장 사항을 업데이트했으며, 이번 사건이 AI 개발 도구 생태계를 겨냥한 국가 차원 공격의 새 패턴을 보여준다고 강조했다.

## Reference

- [From package to postinstall payload: Inside the Mastra npm supply chain compromise by Sapphire Sleet | Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/06/17/postinstall-payload-inside-mastra-npm-supply-chain-compromise/)
- [Microsoft links Mastra AI supply chain attack to North Korean hackers | BleepingComputer](https://www.bleepingcomputer.com/news/security/microsoft-links-mastra-ai-supply-chain-attack-to-north-korean-hackers/)
- [145 Mastra npm Packages Compromised via Hijacked Contributor Account | The Hacker News](https://thehackernews.com/2026/06/144-mastra-npm-packages-compromised-via.html)
- [npm Supply Chain Attack: North Korea Backdoored 144 AI Packages in 88 Minutes | TechTimes](https://www.techtimes.com/articles/318767/20260621/npm-supply-chain-attack-north-korea-backdoored-144-ai-packages-88-minutes.htm)
- [144 Mastra npm Packages Compromised via Supply Chain Attack | Orca Security](https://orca.security/resources/blog/mastra-npm-supply-chain-attack/)
- [Microsoft Attributes Mastra AI Supply Chain Attack to North Korea | Infosecurity Magazine](https://www.infosecurity-magazine.com/news/mastra-ai-supply-chain-attack/)
