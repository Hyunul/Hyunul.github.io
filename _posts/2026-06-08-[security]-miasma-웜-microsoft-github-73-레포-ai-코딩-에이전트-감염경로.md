---
title: "[Security] Miasma 웜, Microsoft GitHub 73개 레포 침해 — AI 코딩 에이전트가 감염 경로가 됐다"
date: 2026-06-08 07:09:36 +09:00
categories: [Security]
tag: [Miasma, 공급망공격, GitHub, 보안, AI에이전트, AzureFunctions, ClaudeCode]
---

## 서론

2026년 6월 5일, 공급망 보안 생태계를 흔드는 사건이 발생했다. **Miasma 웜**이 Microsoft의 공식 GitHub 조직 4개에 속한 **73개 리포지터리를 동시에 침해**한 것이다. Azure, Azure-Samples, Microsoft, MicrosoftDocs 조직이 포함됐으며, 그 중에는 수많은 CI/CD 파이프라인에서 사용되는 **azure/functions-action**도 포함됐다.

이번 사건에서 가장 눈에 띄는 부분은 공격이 **AI 코딩 에이전트를 감염 경로로 활용**했다는 점이다. 악성 설정 파일이 리포지터리에 심어졌고, 개발자가 해당 리포를 **Claude Code, Gemini CLI, Cursor, VS Code** 같은 AI 코딩 도구로 열기만 해도 자격증명 탈취 페이로드가 자동 실행되는 구조였다.

GitHub는 이 공격을 **105초 만에 자동 탐지**하고 73개 리포지터리를 일괄 비활성화했다. 빠른 대응이었지만, 그 105초 사이에 Azure/functions-action이 비활성화되면서 이 Action을 사용하는 전 세계 수많은 조직의 CI/CD 파이프라인이 순간적으로 멈췄다.

이 사건은 Mini Shai-Hulud에서 시작된 공급망 웜 캠페인의 흐름 중 하나다. 5월 23일의 2차 공격, 6월 1일의 Trapdoor 공격에 이어, 이번엔 공격 대상이 npm/PyPI에서 **GitHub 리포지터리와 AI 코딩 에이전트 생태계로 확장**됐다.

## 본론

### Miasma 웜 개요: Mini Shai-Hulud의 새로운 변종

Miasma는 TeamPCP가 2026년 5월 중순에 오픈소스로 공개한 **Mini Shai-Hulud** 악성 코드의 변종이다. Mini Shai-Hulud 자체가 자기 복제 공급망 웜으로, 감염된 계정의 npm/PyPI 퍼블리시 권한을 이용해 스스로를 다른 패키지에 심는 구조였다.

Miasma는 그리스 신화의 "전염된 공기"에서 이름을 따왔다. 악성 코드 내부에 전파 시 자동 생성되는 GitHub 리포지터리 설명에 "Miasma: The Spreading Blight"라는 문구가 포함돼 있어 이름이 붙었다.

Miasma가 이전 버전과 다른 점은 공격 벡터의 확장이다.

- **Mini Shai-Hulud (5월)**: npm/PyPI 패키지 감염 → preinstall 훅으로 실행
- **Miasma (6월)**: GitHub 리포지터리 설정 파일 감염 → AI 코딩 에이전트 실행 시 자동 트리거

### 공격 타임라인

Miasma의 Microsoft GitHub 공격은 다음과 같은 순서로 진행됐다.

```text
[6월 5일 이전]
├── 공격자, 특정 기여자(contributor) 계정 탈취
│   (같은 계정이 5월 19일 PyPI 공격에도 사용됨)
│
[6월 5일]
├── 탈취 계정으로 azure/durabletask 리포에 악성 커밋 푸시
│   └── AI 에이전트 설정 파일(.claude/settings.json, .gemini 등) 내 페이로드 삽입
│
├── 삽입된 설정 파일: 개발자가 리포를 AI 에이전트로 열 시 4.6MB 난독화 JS 페이로드 실행
│
├── 페이로드 동작:
│   ├── AWS, Azure, GCP, Kubernetes 자격증명 탈취
│   ├── npm 토큰 및 GitHub 토큰 탈취
│   └── 피해자 계정으로 접근 가능한 타 리포에 자기 복제 전파 시도
│
[6월 5일, 105초 후]
└── GitHub 자동 탐지 → 73개 Microsoft 리포 일괄 비활성화
```

단일 기여자 계정 탈취에서 Microsoft 공식 리포 73개 침해까지 이르는 연쇄 과정이 불과 수분 안에 이뤄진 셈이다.

### AI 코딩 에이전트를 공격 벡터로 쓴 이유

이번 공격에서 기술적으로 가장 주목할 부분은 **AI 코딩 에이전트를 활성화 트리거로 활용**한 것이다.

기존의 npm/PyPI 공급망 공격은 패키지를 `npm install`하거나 `pip install`하는 순간 preinstall/postinstall 훅이 실행되는 방식이었다. 이번 Miasma는 이 방식을 GitHub 리포지터리 수준으로 끌어올렸다.

공격자가 삽입한 설정 파일은 다음과 같은 위치에 숨어 있었다.

```text
리포지터리 루트/
├── .claude/
│   └── settings.json        ← Claude Code 자동 실행 설정
├── .gemini/
│   └── config.json          ← Gemini CLI 자동 실행 설정
├── .cursorrules             ← Cursor 자동 실행 설정
└── .vscode/
    └── tasks.json           ← VS Code 자동 실행 태스크
```

개발자가 이 리포를 Claude Code, Gemini CLI, Cursor, VS Code 중 하나로 열면, 각 도구의 초기화 과정에서 설정 파일이 로드되고, 그 파일이 4.6MB짜리 난독화된 JavaScript 페이로드를 실행한다. 사용자에게 어떤 추가 동작도 요구하지 않는다. 그냥 "리포를 여는 것"만으로 감염이 완료된다.

이 공격 방식이 효과적인 이유가 있다.

**1. AI 에이전트 설정 파일은 신뢰받는다**: 개발자들은 자신이 사용하는 AI 에이전트의 설정 파일이 악성일 수 있다고 거의 의심하지 않는다.

**2. 자동 실행이 기본값이다**: AI 코딩 에이전트들은 리포 열기 시 설정을 자동으로 적용하는 것이 기본 동작이다.

**3. 공식 리포라는 신뢰**: `Azure/durabletask` 같은 Microsoft 공식 리포를 누가 의심하겠는가.

StepSecurity는 이 공격 방식을 "Trust-Chain Hijacking"이라고 명명했다. 개발자 생태계가 신뢰하는 도구(공식 리포, 검증된 기여자, 공식 GitHub Action)를 순차적으로 탈취해 최종 피해자까지 도달하는 방식이다.

### GitHub의 105초 자동 대응과 그 영향

GitHub의 자동 탐지 시스템은 비정상 커밋 패턴을 탐지하고 105초 만에 73개 리포를 일괄 비활성화했다. 보안 측면에서는 인상적인 대응이지만, 이 자동 비활성화는 예상치 못한 부수 효과를 낳았다.

**azure/functions-action**이 비활성화됐다.

이 GitHub Action은 Azure Functions를 GitHub Actions를 통해 배포하는 공식 도구다. 전 세계 수많은 팀이 이 Action을 CI/CD 파이프라인에서 사용하고 있다. 리포가 비활성화되면서 해당 Action을 참조하는 모든 CI/CD 파이프라인이 즉시 실패하기 시작했다.

```yaml
# 다음과 같이 사용하던 파이프라인들이 모두 영향 받음
- uses: Azure/functions-action@v1   # ← 이 Action이 비활성화된 리포를 가리킴
```

GitHub와 Microsoft가 빠르게 복구 작업을 진행했지만, 그 사이 배포 파이프라인이 멈춘 팀들의 경험은 공급망 보안의 취약성을 다시 한번 체감하는 계기가 됐다.

### 자격증명 탈취 범위

실행된 페이로드는 다음 자격증명을 탈취한다.

- AWS IAM 자격증명 및 역할 토큰
- Azure 서비스 주체(Service Principal) 자격증명
- GCP 서비스 계정 키
- Kubernetes 클러스터 설정 파일(`~/.kube/config`)
- npm 인증 토큰 (`~/.npmrc`)
- GitHub 개인 접근 토큰(PAT) 및 OAuth 토큰

이 자격증명들이 탈취되면 공격자는 해당 계정이 접근 가능한 모든 리포지터리에 자기 자신을 복제해 전파한다. 이전 Mini Shai-Hulud 및 Miasma 캠페인에서 이 전파 메커니즘으로 수십~수백 개의 패키지/리포가 오염된 사례가 있다.

이번 사건에서 피해를 입은 개발자가 Azure/durabletask 리포를 AI 에이전트로 열었다면, 해당 개발자의 클라우드 자격증명이 탈취됐을 가능성이 있다. 리포를 클론하거나 열어본 적이 있는 개발자라면 자격증명 교체를 우선 확인해야 한다.

### 기존 캠페인과의 연결고리

이번 사건은 단독 사건이 아니다. 2026년 5월부터 이어지는 연속된 캠페인의 일부다.

| 날짜 | 사건 | 플랫폼 |
|---|---|---|
| 2026-05-12 | TeamPCP가 Mini Shai-Hulud 소스 공개 | - |
| 2026-05-19 | Mini Shai-Hulud 2차 공격 | npm, PyPI |
| 2026-06-01 | Trapdoor 공격 (AWS 자격증명 탈취) | npm, PyPI |
| 2026-06-01 | Miasma, Red Hat npm 32개 패키지 침해 | npm |
| 2026-06-05 | **Miasma, Microsoft GitHub 73개 리포 침해** | GitHub |

같은 탈취 계정이 5월 19일 PyPI 공격과 6월 5일 GitHub 공격에 연결된다는 점에서, 이 캠페인을 운영하는 공격자가 오랜 기간 해당 계정을 관리하며 전략적으로 활용해왔을 가능성이 높다.

### 개발자 및 보안 엔지니어 대응 체크리스트

이번 사건 이후 보안 커뮤니티에서 권장하는 대응 조치는 다음과 같다.

**즉각 대응이 필요한 경우**

6월 5일 이후 다음 리포지터리를 AI 코딩 에이전트로 열거나 클론한 적이 있다면 자격증명 교체가 필요하다.
- `Azure/durabletask` 및 관련 Azure GitHub 조직 리포

**일반 예방 조치**

```bash
# GitHub Actions에서 특정 커밋 해시로 고정하는 방법
- uses: Azure/functions-action@<full-commit-sha>  # v1 대신 특정 SHA 사용

# 예시
- uses: Azure/functions-action@a1b2c3d4e5f6...  # 알려진 안전한 커밋 SHA
```

GitHub Actions에서 `@v1` 같은 태그 대신 특정 커밋 SHA를 참조하면, 리포에 악성 커밋이 추가돼도 이전 버전을 계속 사용할 수 있다.

**AI 에이전트 설정 파일 검토**

외부 리포를 클론해서 AI 에이전트로 열기 전에 다음 파일들을 먼저 검토하는 습관이 필요하다.
- `.claude/settings.json`, `.claude/commands/`
- `.gemini/` 디렉터리
- `.cursorrules`
- `.vscode/tasks.json`, `.vscode/settings.json`

의심스러운 URL 참조, 외부 스크립트 실행, 대용량 인코딩된 문자열이 포함돼 있다면 즉시 의심해야 한다.

## 정리

- **6월 5일**: Miasma 웜이 Microsoft GitHub 4개 조직, 73개 리포 침해
- **공격 경로**: 탈취된 기여자 계정 → 악성 AI 에이전트 설정 파일 삽입 → 개발자가 리포를 AI 에이전트로 열 때 자동 실행
- **탈취 대상**: AWS, Azure, GCP, Kubernetes, npm, GitHub 자격증명
- **GitHub 대응**: 105초 자동 탐지 후 73개 리포 일괄 비활성화
- **CI/CD 영향**: `azure/functions-action` 비활성화로 글로벌 배포 파이프라인 중단
- **캠페인 연속성**: Mini Shai-Hulud(5월) → Trapdoor(6월 1일) → Miasma→Microsoft(6월 5일)

보안 커뮤니티의 반응은 명확하다. "AI 코딩 에이전트가 새로운 공격 표면이 됐다." GitHub Actions 보안(태그 대신 커밋 SHA 사용), AI 에이전트 설정 파일 검토, 클라우드 자격증명 접근 모니터링은 이제 선택이 아닌 필수다.

## Reference

- [Miasma Worm Hits Microsoft Again: Azure Functions Action and 72 Other Repositories Disabled After Supply Chain Attack Targeting AI Coding Agents - StepSecurity](https://www.stepsecurity.io/blog/miasma-worm-hits-microsoft-again-azure-functions-action-and-72-other-repositories-disabled-after-supply-chain-attack-targeting-ai-coding-agents)
- [Miasma Worm Hits 73 Microsoft GitHub Repositories in Major Supply Chain Attack - The Hacker News](https://thehackernews.com/2026/06/miasma-worm-hits-73-microsoft-github.html)
- [Self-replicating Miasma worm hits 73 Microsoft GitHub repositories in supply chain attack - The Next Web](https://thenextweb.com/news/miasma-worm-microsoft-github-supply-chain)
- [Miasma Worm Supply Chain Attack: 73 Microsoft GitHub Repositories Compromised via AI Coding Tools - Rescana](https://www.rescana.com/post/miasma-worm-supply-chain-attack-73-microsoft-github-repositories-compromised-via-ai-coding-tools)
- [GitHub disables 73 Microsoft Azure repos after "Miasma" editor/AI workspace attack - Windows Forum](https://windowsforum.com/threads/github-disables-73-microsoft-azure-repos-after-miasma-editor-ai-workspace-attack.423398/)
- [Red Hat npm Packages Compromised to Spread a Credential-Stealing Worm - Aikido](https://www.aikido.dev/blog/red-hat-npm-packages-compromised-credential-stealing-worm)
