---
title: "[AI] everything-claude-code 플러그인 분석"
date: 2026-04-10 21:10:00 +09:00
categories: [Tip]
tag: [AI, Claude Code, Plugin, MCP, Workflow]
---

## 서론

요즘 AI 코딩 도구를 세팅할 때 자주 보게 되는 저장소 중 하나가 [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code)다.  
처음에는 "Claude Code 설정 모음집" 정도로 보이지만, 실제 구조를 보면 단순한 설정 묶음보다는 **에이전트가 일하는 환경 자체를 설계한 하네스 레이어**에 가깝다.

나 역시 현재 Claude 환경에 이 레포의 plugin을 설치한 상태라, 이번에는 단순 사용기를 넘어서 "이 레포가 실제로 무엇을 제공하고, 왜 이렇게까지 큰 구조를 갖게 되었는가"를 기준으로 정리해보려고 한다.

## 이 레포를 플러그인 하나로 보면 놓치는 것

2026년 4월 기준 README는 이 프로젝트를 단순 config collection이 아니라, **AI agent harnesses를 위한 performance optimization system**이라고 설명한다.  
즉, 좋은 프롬프트 몇 개를 주는 저장소가 아니라 다음과 같은 요소를 함께 제공하는 운영 레이어라는 뜻이다.

- agents
- skills
- hooks
- rules
- MCP configurations
- legacy command shims

이 표현이 과장이 아닌 이유는 실제 디렉터리 구조를 보면 드러난다.

- `agents/`
- `skills/`
- `commands/`
- `hooks/`
- `rules/`
- `mcp-configs/`
- `.claude-plugin/`
- `.codex-plugin/`
- `.cursor/`
- `.opencode/`

즉, 특정 Claude 세팅 파일 몇 개만 제공하는 것이 아니라, 여러 AI 코딩 런타임에서 재사용할 수 있는 공통 workflow surface를 만들고 있다.

## 핵심 철학은 command보다 skill이다

이 레포를 이해할 때 가장 중요한 포인트는 **skills-first** 철학이다.  
`the-shortform-guide.md`에서는 skill을 "scoped workflow bundles"로 설명하고, command는 그 위에 얹힌 legacy entry point에 가깝다고 본다.

이 차이는 생각보다 크다.

- command는 호출 이름에 가깝다
- skill은 작업 절차와 보조 자료까지 포함한 실행 단위다

예를 들어 `/tdd`, `/plan`, `/e2e` 같은 슬래시 명령은 진입점일 뿐이고, 실제 지속 가능한 로직은 `skills/`에 남겨두는 방식이다.  
그래서 Everything Claude Code는 "명령어 모음집"이라기보다, **반복 가능한 작업 패턴을 skill로 축적하는 저장소**라고 보는 편이 더 정확하다.

## 현재 내 Claude 세팅 기준으로 보면 어떻게 해석할 수 있을까

내가 현재 설치한 것은 이 레포의 Claude plugin이다.  
여기서 중요한 점은 **plugin 설치만으로 레포 전체가 완성되지는 않는다**는 것이다.

README는 Claude Code plugin 시스템의 한계 때문에 `rules`는 플러그인으로 배포되지 않는다고 분명히 적고 있다.  
즉, plugin 설치만으로는 `commands`, `agents`, `skills`, `hooks`에는 빠르게 접근할 수 있지만, 항상 적용되는 규칙 레이어인 `rules`는 별도 설치가 필요하다.

이걸 구조로 풀어보면 지금 내 세팅은 대략 이렇게 이해할 수 있다.

1. Claude Code 기본 런타임이 있고
2. 그 위에 ECC plugin이 올라가서 skills, agents, hooks, commands를 확장하고
3. 추가로 rules를 수동 설치해야 "항상 따르는 기준"까지 완성된다

즉, 현재 상태를 "Claude를 더 강하게 만든 상태"라고 볼 수는 있지만, rules까지 함께 적용하지 않았다면 아직은 **호출 가능한 워크플로가 풍부한 상태**에 더 가깝다.

## 계층으로 보면 이 레포가 왜 하네스처럼 보이는지 이해된다

Everything Claude Code는 대략 다섯 층으로 나눠서 이해하면 깔끔하다.

### 1. Rules

`rules/README.md`를 보면 rules는 `common/`과 언어별 디렉터리로 나뉜다.

```text
rules/
├── common/
├── typescript/
├── python/
├── golang/
├── web/
├── swift/
└── php/
```

이 구조는 "모든 프로젝트에 공통으로 적용되는 원칙"과 "언어별로 덮어써야 하는 규칙"을 분리하려는 설계다.  
즉, rule은 무엇을 해야 하는지 정하고, skill은 그것을 어떻게 할지 알려주는 방식이다.

### 2. Skills

ECC에서 가장 중요한 레이어는 `skills/`다.  
README와 guide 기준으로 이 레포는 TDD, security review, verification loop, continuous learning, frontend/backend patterns 같은 작업 패턴을 skill로 묶어둔다.

skill 중심 구조의 장점은 명확하다.

- 반복되는 작업 절차를 재사용할 수 있다
- command 이름보다 실제 실행 패턴이 오래 남는다
- 특정 도메인 지식을 프롬프트가 아니라 워크플로로 축적할 수 있다

### 3. Agents

`agents/`는 planner, architect, code-reviewer, security-reviewer 같은 역할 기반 서브에이전트를 제공한다.  
이 레이어는 하나의 거대한 메인 에이전트가 모든 걸 처리하게 두지 않고, 역할을 분리해 컨텍스트를 줄이려는 목적이 강하다.

즉, "똑똑한 하나"보다 **잘 나눠진 여러 역할**을 선호하는 구조다.

### 4. Hooks

이 레포가 단순 설정집을 넘어 하네스처럼 보이게 만드는 핵심은 `hooks/`다.  
`hooks/README.md`에 따르면 hook은 tool 실행 전후와 세션 lifecycle에 개입한다.

예를 들면 이런 것들이다.

- dev server blocker
- tmux reminder
- pre-commit quality check
- quality gate
- TypeScript check
- console.log warning
- session summary
- pattern extraction
- cost tracker

즉, 에이전트가 행동한 뒤에 사용자가 일일이 감시하는 구조가 아니라, **실행 루프 자체에 가드레일을 심는 방식**이다.

### 5. MCP and Cross-Harness Packaging

이 레포는 Claude만 바라보지 않는다.  
README는 Claude Code뿐 아니라 Codex, Cursor, OpenCode, Gemini 등 여러 하네스를 함께 언급하고 있고, 실제로 `.codex-plugin/`도 같이 제공한다.

이 점이 중요하다.  
저자가 지키고 싶은 핵심 자산은 특정 툴 UI가 아니라, 그 위에서 동작하는 workflow, rule, hook, skill 같은 운영 자산이라는 뜻이기 때문이다.

## 이 레포가 강한 이유

Everything Claude Code가 강한 이유는 "프롬프트를 잘 짰다"보다 "운영 기본값을 설계했다"에 있다.

실제 AI 코딩을 오래 쓰다 보면 아래 문제가 반복된다.

- 세션이 길어질수록 산으로 간다
- 테스트를 빼먹는다
- 코드 수정 뒤 품질 확인이 늦어진다
- 컨텍스트가 도구와 MCP로 과하게 오염된다
- 같은 실수를 계속 반복한다

ECC는 이런 문제를 개별 팁으로 해결하지 않는다.  
대신 `rules`, `skills`, `hooks`, `agents`, `MCP`로 나눠서 해결하려고 한다.

이 접근은 전형적인 하네스 엔지니어링과 닮아 있다.  
즉, 모델 자체를 바꾸는 대신 **모델이 일하는 환경을 더 신뢰 가능하게 만드는 방식**이다.

## 한계도 분명하다

물론 이 레포가 만능이라는 뜻은 아니다.

첫째, 규모가 크다.  
README의 최신 설명만 봐도 2026년 4월 v1.10.0 기준 public surface가 38 agents, 156 skills, 72 legacy command shims라고 적혀 있다.  
이 정도면 "편리한 설정 모음"을 넘어서 하나의 플랫폼처럼 느껴질 정도다.

둘째, 많이 넣는다고 항상 좋은 것은 아니다.  
README는 MCP를 너무 많이 켜면 컨텍스트 윈도우가 급격히 줄어들 수 있다고 경고한다.  
즉, 전부 설치하는 것보다 **현재 프로젝트에 맞게 좁혀서 쓰는 능력**이 더 중요하다.

셋째, plugin만 설치하면 끝나는 구조가 아니다.  
특히 rules는 별도 설치가 필요하므로, 설치 방법을 정확히 이해하지 않으면 "왜 기대보다 덜 체계적으로 느껴지지?"라는 상황이 생길 수 있다.

## 내 결론

Everything Claude Code는 단순한 Claude Code 확장팩이라기보다, **AI 코딩 환경을 운영 가능한 시스템으로 바꾸려는 레포**라고 보는 편이 맞다.

내가 현재 plugin을 설치한 상태에서 이 레포를 다시 보면, 나는 단순히 명령 몇 개를 추가한 것이 아니다.  
정확히는 Claude 위에 다음 레이어를 얹은 셈이다.

- 역할 분리용 agents
- 반복 작업용 skills
- 자동 개입용 hooks
- 외부 연결용 MCP surface

여기에 rules까지 맞춰서 설치하면 비로소 "내 Claude 세팅"이 아니라, **내 개발 방식 자체를 반영한 하네스**에 가까워진다.

그래서 이 레포의 핵심 가치는 화려한 기능 수보다, "에이전트를 어떻게 안정적으로 일하게 만들 것인가"에 대한 운영 감각에 있다고 느꼈다.

## Reference

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)
- [README.md](https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/README.md)
- [the-shortform-guide.md](https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/the-shortform-guide.md)
- [hooks/README.md](https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/hooks/README.md)
- [rules/README.md](https://raw.githubusercontent.com/affaan-m/everything-claude-code/main/rules/README.md)
