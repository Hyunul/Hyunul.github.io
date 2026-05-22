---
title: "[Security] Mini Shai-Hulud: TanStack npm 공급망 웜, 2차 공격까지 확산"
date: 2026-05-23 08:00:00 +09:00
categories: [Security]
tag: [공급망공격, npm, GitHubActions, TeamPCP, 오픈소스보안]
---

## 서론

5월 11일 그리고 5월 19일, 오픈소스 생태계에 연이어 경보가 울렸다. **TeamPCP**라는 위협 행위자 그룹이 `@tanstack/react-router`를 포함한 npm 패키지 수백 개를 악성 코드로 오염시키는 데 성공했다. 이 공격은 단순히 한두 개 패키지가 털린 수준이 아니다. TanStack 생태계 전체, Mistral AI SDK, UiPath 자동화 도구, OpenSearch, Guardrails AI 패키지까지 영향을 받았다. 두 번째 파도에서는 단 1시간 만에 323개 패키지에 걸쳐 639개의 악성 버전이 배포됐다.

보안 연구 커뮤니티는 이 공격에 **"Mini Shai-Hulud"**라는 이름을 붙였다. 사막 행성의 거대 벌레처럼 npm 생태계를 파고들며 자기 증식하는 웜의 특성을 빗댄 이름이다. 더 무서운 점은, 이번이 처음이 아니라는 것이다. TeamPCP는 2026년 3월 Aqua Security Trivy, 4월 Bitwarden CLI npm에 이어 5월에 다시 같은 전술로 더 넓은 범위를 공격했다. 단발성 사고가 아닌 지속적인 캠페인으로 봐야 한다.

## 본론

### 1차 공격: TanStack 생태계를 정조준하다 (5월 11일)

5월 11일 19:20~19:26 UTC, 단 6분 사이에 `@tanstack` 네임스페이스의 42개 패키지에서 84개의 악성 아티팩트가 npm에 배포됐다. `@tanstack/react-router` 단일 패키지만으로도 주당 약 1,270만 다운로드를 기록하는 React 생태계의 핵심 라우팅 라이브러리다.

여기서 핵심은 공격자가 자격증명을 훔쳐서 직접 패키지를 배포한 게 아니라는 점이다. 악성 패키지는 TanStack의 **정식 릴리스 파이프라인**을 통해 배포됐다. 즉, TanStack 본인의 신뢰할 수 있는 OIDC 아이덴티티로 서명된 버전이 npm에 올라간 것이다. 이것이 역사상 첫 번째로 유효한 SLSA(Supply chain Levels for Software Artifacts) 출처 증명을 가진 악성 npm 패키지로 기록된 이유다.

#### 공격 메커니즘: 3단계 체인

```text
1단계 — Pwn Request:
  공격자가 TanStack/router 저장소를 포크(fork)
  pull_request_target 워크플로우를 트리거하는 PR 오픈
  워크플로우가 공격자의 포크 코드를 체크아웃하고 실행

2단계 — 캐시 포이즈닝:
  실행된 코드가 pnpm 스토어(GitHub Actions 캐시)를 악성 버전으로 교체
  이후 정식 유지보수자의 PR이 main에 머지되면 릴리스 워크플로우가 오염된 캐시를 복원

3단계 — OIDC 토큰 탈취 + 악성 배포:
  복원된 악성 바이너리가 GitHub Actions 러너의 프로세스 메모리에서 OIDC 토큰 직접 추출
  탈취된 OIDC 토큰으로 정식 npm 배포 파이프라인을 통해 악성 버전 게시
```

공격자는 npm 크리덴셜을 한 번도 손에 넣지 않았다. TanStack의 신뢰를 빌려 공식 채널로 악성 코드를 배포했다. 이 때문에 자동화된 보안 스캐너로는 감지하기 매우 어렵다.

#### 악성 페이로드의 기능

배포된 악성 페이로드는 다음 기능을 수행한다:

- **크리덴셜 수집**: GitHub 토큰, npm 토큰, CI/CD 시크릿, 클라우드 크리덴셜(AWS, Azure, GCP), API 키, 개발 도구 설정값
- **3중 채널 유출**: 타이포스쿼팅 도메인, 분산형 메신저 Session 네트워크, GitHub API 데드 드롭(탈취한 토큰 활용)
- **영속 데몬 설치**: 개발자 머신에 `gh-token-monitor` 데몬 설치 후 60초마다 GitHub API 폴링
- **자기 증식**: 탈취 크리덴셜로 접근 가능한 다른 패키지에 악성 코드 주입 시도
- **러시아어 회피**: 시스템 언어가 러시아어면 동작 종료 — 귀속 추정의 단서가 되는 특징

### 피해 범위

1차 공격에서 피해를 입은 패키지 목록:

| 대상 | 패키지 수 | 비고 |
|------|-----------|------|
| @tanstack/* | 42개 | 84개 악성 아티팩트 |
| @squawk/* | 확인됨 | 동시 피해 |
| @mistralai/* | 확인됨 | npm + PyPI 양쪽 피해 |
| UiPath | 65개 | 자동화 도구 |
| OpenSearch | 1개 | 주당 130만 다운로드 |
| Guardrails AI | 확인됨 | PyPI |

전체적으로 170개 이상의 npm 패키지, 2개의 PyPI 패키지, 총 404개의 악성 버전이 배포됐다. OpenAI도 macOS 제품이 TanStack 의존성 체인을 통해 영향을 받았다고 공식 대응 포스트를 공개했다.

### 2차 공격: 단 1시간에 639개 악성 버전 (5월 19일)

1차 공격으로부터 8일이 지나지 않아 TeamPCP는 다시 움직였다. 5월 19일, npm 유지보수자 계정 **atool**이 탈취됐고, 약 1시간 동안 323개 패키지에 걸쳐 639개의 악성 버전이 배포됐다. Wiz와 Orca Security에 따르면 이는 Shai-Hulud 시리즈 역사상 **단일 시간 기준 가장 많은 패키지 수**다.

같은 날 Microsoft의 공식 Python SDK인 **durabletask**가 PyPI에서 침해됐다. 28KB 크기의 페이로드가 포함된 버전이 배포됐으며, 이 페이로드는 AWS, Azure, GCP, Kubernetes, 패스워드 매니저, 90개 이상의 개발 도구 설정 파일에서 크리덴셜을 수집하고, 접근 가능한 클라우드 인프라 전반으로 측면 이동을 시도했다.

Palo Alto Networks Unit 42는 5월 21일자 업데이트된 npm 위협 환경 보고서에서 이 두 번째 파도를 별도로 다루며 공격자의 전술 진화를 경고했다.

### TeamPCP의 캠페인 패턴

StepSecurity의 귀속 분석에 따르면 TeamPCP는 2026년에만 이미 세 번의 공급망 캠페인을 성공적으로 수행했다:

| 시기 | 대상 | 비고 |
|------|------|------|
| 2026년 3월 | Aqua Security Trivy 스캐너 | 컨테이너 보안 도구 |
| 2026년 4월 | Bitwarden CLI npm 패키지 | 패스워드 매니저 |
| 2026년 5월 11일 | TanStack, Mistral AI, UiPath, OpenSearch 등 160+ 패키지 | GitHub Actions 캐시 포이즈닝 |
| 2026년 5월 19일 | atool 계정 탈취 — 323개 패키지 | 2차 파도 |

전술·기법·절차(TTP)가 일관되다는 점, 그리고 악성 코드 내부의 러시아어 회피 로직이 동일하다는 점에서 귀속이 이루어졌다. CyberScoop, Infosecurity Magazine 등 주요 보안 미디어도 이 귀속 분석을 인용하며 보도했다.

### 지금 당장 해야 할 조치

사용 중인 패키지 중 영향을 받은 것이 있는지 확인하고 대응하는 방법이다.

```bash
# 현재 설치된 @tanstack/* 버전 확인
npm ls @tanstack/react-router

# npm audit으로 알려진 취약점 확인
npm audit

# lock 파일 기반 클린 재설치 (오염 전 버전으로 복원)
npm ci

# GitHub Actions 캐시 무효화 (해당 저장소)
# Repository → Actions → Caches → 의심 캐시 삭제
```

권고사항:
1. **영향 범위 확인**: 5월 11일~19일 사이 배포된 @tanstack/*, @mistralai/*, UiPath, OpenSearch, Guardrails AI 의존 버전 점검
2. **CI/CD 캐시 무효화**: GitHub Actions의 pnpm/npm 캐시 전량 삭제 후 재생성
3. **워크플로우 설정 검토**: `pull_request_target`을 사용하는 워크플로우에서 외부 포크의 코드가 실행되지 않도록 설정 변경
4. **크리덴셜 로테이션**: npm 토큰, GitHub 토큰, 클라우드 IAM 자격증명 즉시 교체
5. **SLSA + Sigstore 검증 강화**: 신뢰할 수 있는 출처 증명이 있어도 무조건 신뢰하지 말 것

### 업계 반응

보안 커뮤니티에서 이번 공격이 특히 주목받는 이유는 두 가지다.

첫 번째는 **SLSA 출처 증명 무력화**다. SLSA는 소프트웨어 공급망 보안의 핵심 프레임워크로 많은 기업이 채택하고 있는데, 정식 파이프라인 자체를 장악하면 SLSA 프로비넌스가 오히려 악성 패키지에 신뢰를 부여하는 역설적인 상황이 생겼다. Snyk, Wiz 등 공급망 보안 기업들은 "프로비넌스 검증만으로는 충분하지 않다"는 경고를 내놓았다.

두 번째는 **자기 증식 메커니즘**이다. 크리덴셜을 탈취하면 해당 크리덴셜로 다른 패키지에도 악성 코드를 주입하는 구조가 전형적인 웜이다. 이 때문에 초기 감염 범위보다 실제 피해 범위가 훨씬 넓어질 수 있다.

## 정리

- **Mini Shai-Hulud**는 TeamPCP가 2026년 5월에 벌인 npm/PyPI 공급망 웜 공격으로, 1차(5월 11일)와 2차(5월 19일) 두 파도에 걸쳐 총 160+ npm 패키지, 400+ 악성 버전이 배포됐다.
- 공격은 GitHub Actions "Pwn Request" + 캐시 포이즈닝 + OIDC 토큰 탈취의 3단계 체인을 사용했으며, 피해자 본인의 정식 릴리스 파이프라인이 무기화됐다.
- 역사상 처음으로 유효한 SLSA 출처 증명을 가진 악성 npm 패키지가 배포된 사례다.
- 영향 범위: TanStack(주당 1,270만 다운로드), Mistral AI, UiPath, OpenSearch, OpenAI macOS 제품 등.
- 2차 파도(5월 19일)는 1시간 만에 323개 패키지·639개 악성 버전 배포 — Shai-Hulud 시리즈 최대 규모.
- TeamPCP는 2026년 3월부터 지속적인 공급망 캠페인 중이며, `pull_request_target` 워크플로우 보안 강화와 CI/CD 캐시 관리가 핵심 대응 포인트다.

## Reference

- [Mini Shai-Hulud Strikes Again: TanStack + more npm Packages Compromised — Wiz Blog](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
- [TanStack npm Packages Hit by Mini Shai-Hulud — Snyk](https://snyk.io/blog/tanstack-npm-packages-compromised/)
- [Mini Shai-Hulud Worm Compromises TanStack, Mistral AI, Guardrails AI & More — The Hacker News](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html)
- [TanStack and 160+ npm/PyPI Packages Compromised in Supply Chain Worm Attack — Orca Security](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/)
- [TeamPCP's Mini Shai-Hulud Is Back — StepSecurity](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem)
- ['Mini Shai-Hulud' malware compromises hundreds of open-source packages — CyberScoop](https://cyberscoop.com/mini-shai-hulud-supply-chain-malware-attack/)
- [The npm Threat Landscape: Attack Surface and Mitigations (Updated May 21) — Palo Alto Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
- [Our response to the TanStack npm supply chain attack — OpenAI](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/)
