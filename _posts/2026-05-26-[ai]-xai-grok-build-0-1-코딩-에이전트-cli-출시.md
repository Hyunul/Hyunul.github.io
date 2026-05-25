---
title: "[AI] xAI, 코딩 에이전트 CLI 'Grok Build 0.1' 조기 베타 공개"
date: 2026-05-26 07:10:00 +09:00
categories: [AI]
tag: [xAI, GrokBuild, CodingAgent, LLM, CLI]
---

## 서론

2026년 5월 25일, xAI가 코딩 전문 에이전트 CLI인 **Grok Build 0.1**을 SuperGrok 및 X Premium Plus 구독자를 대상으로 조기 베타 공개했다. Claude Code, OpenAI Codex CLI에 이어 대형 AI 연구소가 직접 터미널 기반 코딩 에이전트 시장에 뛰어드는 세 번째 사례다.

Grok Build 0.1은 단순한 코드 자동완성 도구가 아니다. 8개의 병렬 서브에이전트, Plan Mode, MCP(Model Context Protocol) 호환을 갖춘 풀-스택 에이전트 워크플로 도구를 지향한다. 256K 토큰의 컨텍스트 윈도우와 출력 토큰 제한 없는 구성은 대형 모노레포나 장기 코딩 세션을 염두에 둔 설계다.

SWE-Bench Verified 기준 70.8%로 Claude Code(87.6%)와 Codex CLI(88.7%)에 비해 눈에 띄게 낮은 점수가 화제가 됐다. 그러나 xAI는 "점수 경쟁보다 에이전트 워크플로 설계에서 차별화를 꾀한다"는 입장을 분명히 했고, 커뮤니티에서는 평가 방식에 따라 실제 사용 경험이 다를 수 있다는 반응도 나오고 있다.

코딩 에이전트 CLI 시장이 이제 사실상 3파전 구도로 굳어지면서, 각 도구의 특성과 가격이 개발 조직의 채택 결정에 중요한 변수가 됐다. 이 글에서는 Grok Build 0.1의 기능, 경쟁 구도, 실제 사용 시 고려해야 할 점들을 정리한다.

## 본론

### 출시 배경과 경쟁 구도

xAI는 2025년 말부터 Grok 4.x 시리즈로 코딩 특화 성능을 어필해 왔다. 2026년 4월 17일 Grok 4.3 베타를 거쳐, 5월 14일 Grok Build 모델의 제한 공개를 시작했고, 5월 25일에는 SuperGrok과 X Premium Plus 구독자 전체로 조기 베타를 확장했다.

코딩 에이전트 CLI 시장의 현재 경쟁 구도는 다음과 같다.

| 제품 | SWE-Bench Verified | 컨텍스트 | API 입력 가격 | 제공사 |
|---|---|---|---|---|
| OpenAI Codex CLI | 88.7% | 200K | 미공개 | OpenAI |
| Claude Code | 87.6% | 200K | 미공개 | Anthropic |
| **Grok Build 0.1** | **70.8%** | **256K** | **$1/M** | **xAI** |

Grok Build 0.1이 두 선행 제품보다 약 17~18%p 낮은 점수를 기록한 건 사실이다. 다만 kilo.ai의 분석에 따르면 SWE-Bench는 단일 파일 패치 수준의 작업 비중이 높아, 멀티파일·장기 에이전트 태스크에서는 실제 성능 격차가 수치보다 좁을 수 있다고 지적했다. 물론 아직 독립적인 검증이 이루어지지 않은 주장이다.

### 핵심 기능 상세

**256K 토큰 컨텍스트 윈도우 (출력 토큰 제한 없음)**

Grok Build 0.1의 가장 강한 하드웨어 스펙은 출력 토큰 제한이 없는 256K 컨텍스트다. 대형 레거시 코드베이스를 다룰 때 컨텍스트 창이 부족해 분할 세션을 반복해야 하는 문제를 피할 수 있다. 경쟁 제품들이 100K~200K 수준에서 출력 제한을 두는 것과 대비된다.

**Plan Mode: 실행 전 계획 검토**

에이전트가 작업 계획을 수립하면, 사용자가 각 단계를 검토하고 수정한 뒤 실행을 승인하는 방식이다. 구체적으로:

- 개별 단계에 댓글을 달아 지시사항을 추가하거나 수정 요청
- 전체 계획을 재작성하거나 일부 단계를 삭제
- 승인 이후 실행된 모든 변경 사항은 clean diff 형태로 확인

이 방식은 완전 자동 실행에 대한 불안감이 있는 팀에게 실용적인 절충점을 제공한다. 코드를 자동으로 수정하기 전에 사람이 개입할 수 있는 지점을 명시적으로 만드는 설계다.

**8개의 병렬 서브에이전트**

대형 태스크를 xAI가 "전문화된 서브에이전트"라고 부르는 8개의 독립 에이전트로 분배해 동시에 처리한다. 각 서브에이전트는 독립적인 git worktree에서 동작하므로, 병렬 작업 중 파일 충돌이 최소화된다.

```text
# Grok Build 병렬 에이전트 예시 흐름
사용자 태스크: "결제 모듈 리팩터링 + 테스트 작성 + 문서 업데이트"
                              ↓
          ┌────────────────────────────────────┐
          │ 서브에이전트 1: 결제 로직 리팩터링    │
          │ 서브에이전트 2: 단위 테스트 작성      │
          │ 서브에이전트 3: API 문서 업데이트     │
          └────────────────────────────────────┘
                              ↓
               Plan 검토 → 승인 → 통합 diff
```

**MCP 호환**

xAI는 Grok Build가 MCP(Model Context Protocol)를 공식 지원한다고 밝혔다. 이미 Claude Code나 Cursor에서 사용 중인 MCP 서버를 재사용할 수 있다. 사내 데이터베이스, Jira, GitHub 등의 MCP 서버가 있다면 별도 설정 없이 Grok Build와 연결할 수 있다.

### 접근성과 가격 구조

현재 Grok Build 0.1의 접근 방법과 가격은 다음과 같다.

- **구독**: SuperGrok Heavy $99/월 (정상가 $299/월 introductory 한시 적용)
- **API**: 입력 $1/백만 토큰, 출력 $2/백만 토큰, 캐시 히트 $0.20/백만 토큰
- **API 모델 ID**: `grok-build-0.1-20260520`
- **대상**: SuperGrok, X Premium Plus 구독자에게만 개방

Claude Code가 Anthropic API 키로 직접 접근할 수 있는 것과 달리, Grok Build는 현재 xAI 구독 생태계에 묶여 있다. API 접근은 xAI API 키를 통해 가능하지만, 더 넓은 독립 접근성을 원하는 개발자들에게는 진입 장벽이 된다는 지적이 있다.

한편 API 가격은 경쟁 제품 대비 합리적이라는 평가다. 아직 OpenAI Codex CLI나 Claude Code의 API 단위 가격이 공식화되지 않은 상황에서, Grok Build의 $1/$2 투명 가격 공개는 기업 도입 검토 과정에서 긍정적으로 작용하고 있다.

### SWE-Bench 점수와 실제 성능 사이의 간극

SWE-Bench Verified는 GitHub의 실제 이슈-PR 쌍을 기반으로, 모델이 코드 수정 패치를 얼마나 잘 생성하는지를 측정한다. 현재 기준으로 Grok Build 0.1은 70.8%를 기록해 상위권에는 들지 못했다.

그러나 커뮤니티에서는 몇 가지 맥락을 함께 고려해야 한다는 목소리가 나온다. SWE-Bench의 문제 대부분이 단일 파일 패치에 집중돼 있어, 멀티 에이전트 협업이나 장기 세션에서는 평가 결과가 달라질 수 있다는 것이다. xAI는 자체 내부 평가 기준으로 "복잡한 엔지니어링 워크플로"에서의 우위를 주장하지만, 아직 독립적인 검증 데이터는 없다.

실제로 Grok Build가 점수 면에서 뒤처진다는 사실을 놓고 볼 때, xAI는 2026년 하반기 안에 점수를 끌어올리거나 아니면 점수 외의 차별화 가치로 시장을 설득해야 하는 과제를 안고 있다.

### 업계 반응

**DevOps.com**은 "Grok Build가 기술적으로는 선발 주자에 뒤처지지만, 병렬 서브에이전트 구조와 plan-before-execute 방식은 대규모 엔지니어링 조직에서 가치 있는 워크플로를 제공할 수 있다"고 평가했다.

**kilo.ai** 분석에서는 "SWE-Bench 70.8%라는 점수가 처음엔 실망스러울 수 있지만, 에이전트 방식의 태스크에서는 단순 모델 점수와 실제 성능 사이의 괴리가 크다. 실사용 테스트가 필요하다"며 신중한 입장을 취했다.

Open Router 상에서 집계된 사용 데이터에 따르면, 조기 베타 공개 직후 Grok Build의 요청 건수가 빠르게 늘고 있으며, SuperGrok 구독자층을 중심으로 채택이 시작되고 있다.

xAI는 `grok-build-0.2`를 준비 중이라고 밝혔으며, GPU 인프라 확장 속도를 감안하면 하반기 내 벤치마크 격차가 좁혀질 것이라는 전망이 우세하다. 다만 이를 뒷받침하는 공식 발표나 구체적인 일정은 아직 없다.

### 개발자가 지금 바로 확인해야 할 것들

Grok Build를 실제 도입 검토 중이라면 현 시점에서 확인해야 할 포인트들이 있다.

1. **MCP 서버 호환성 확인**: 기존 Claude Code와 공유하는 MCP 서버가 있다면 Grok Build에서도 바로 사용 가능한지 테스트해볼 것
2. **구독 구조 검토**: API 키만으로는 접근이 제한적이므로, 팀 단위 접근이 필요하다면 SuperGrok 구독 정책을 검토
3. **워크트리 기반 병렬 작업 적합성**: git worktree 기반 병렬 작업이 실제 팀 워크플로와 맞는지 평가
4. **Plan Mode 활용**: 완전 자동 실행에 대한 리스크가 있는 프로덕션 환경이라면 Plan Mode 필수 활성화 권장

## 정리

- 2026년 5월 25일, xAI가 Grok Build 0.1 CLI를 SuperGrok/X Premium Plus 구독자에게 조기 베타로 공개했다.
- SWE-Bench Verified 기준 70.8%로 Claude Code(87.6%)·Codex CLI(88.7%)에 비해 낮지만, 병렬 서브에이전트·Plan Mode·MCP 호환·256K 컨텍스트를 차별화 포인트로 내세웠다.
- API 단위 가격은 $1/$2(입력/출력, 백만 토큰), 모델 ID는 `grok-build-0.1-20260520`.
- 현재 xAI 구독 생태계에 묶여 있어 독립 API 접근이 제한적이다.
- 코딩 에이전트 CLI 시장은 OpenAI·Anthropic·xAI의 3파전 구도로 굳어졌고, 각 제품의 워크플로 설계 철학이 실질적인 차별화 요인이 됐다.
- `grok-build-0.2`가 준비 중이라고 하며, 하반기 업그레이드 이전에는 벤치마크 점수를 그대로 참고하는 것이 합리적이다.

## Reference

- [Introducing Grok Build | xAI 공식 블로그](https://x.ai/news/grok-build-cli)
- [Grok Build 0.1 벤치마크 및 가격 분석 | kilo.ai](https://kilo.ai/models/xai-grok-build-0-1)
- [xAI Enters the Coding Agent Race With Grok Build | DevOps.com](https://devops.com/xai-enters-the-coding-agent-race-with-grok-build/)
- [Grok Build 0.1 API Docs | xAI Developers](https://docs.x.ai/developers/models/grok-build-0.1)
- [OpenRouter - Grok Build 0.1 성능 지표](https://openrouter.ai/x-ai/grok-build-0.1/performance)
