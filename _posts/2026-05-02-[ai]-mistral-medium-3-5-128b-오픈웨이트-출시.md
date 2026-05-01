---
title: "[AI] Mistral Medium 3.5 출시: 128B 오픈웨이트로 Claude Sonnet 4.5를 뛰어넘다"
date: 2026-05-02 09:00:00 +09:00
categories: [AI]
tag: [Mistral, LLM, 오픈소스, 오픈웨이트, 코딩에이전트]
---

## 서론

2026년 4월 29일, 프랑스 AI 스타트업 Mistral AI가 **Mistral Medium 3.5**를 공개했다. 128B(1280억) 파라미터 규모의 덴스(dense) 모델로, 오픈웨이트(open-weights) 형식으로 Hugging Face에 공개됐다. 직접 GPU에 올려 자체 호스팅할 수 있다는 점이 가장 큰 차별점이다.

이번 릴리스가 단순한 "또 하나의 모델 출시"가 아닌 이유는 벤치마크 결과 때문이다. SWE-bench Verified 기준 77.6%를 기록하며, OpenAI의 GPT-4o와 Anthropic의 Claude Sonnet 4.5를 코딩 에이전트 벤치마크에서 앞섰다. 클로즈드 소스 유료 API가 지배하는 최상위권에, 오픈웨이트 모델이 당당하게 이름을 올린 것이다.

AI 패권 경쟁에서 미국(OpenAI, Anthropic, Google)과 중국(DeepSeek, 智谱)이 주도권을 다투는 가운데, 유럽 기반 Mistral이 오픈소스 노선을 고수하며 성능 면에서 최상위권에 진입했다는 점은 업계 전반에 신호를 주고 있다. 데이터 주권이 중요한 금융·의료·공공 분야에서는 자체 호스팅 가능한 고성능 모델이 현실적인 대안이 될 수 있기 때문이다.

Mistral이 이번에 단순히 모델만 내놓은 게 아니라, 코딩 에이전트 서비스 **Mistral Vibe**의 백본으로도 채택했다는 점까지 더하면, 이번 릴리스는 전략적 의도가 꽤 선명하다.

## 본론

### 모델 스펙: 128B 파라미터, 256k 컨텍스트

Mistral Medium 3.5의 주요 스펙을 정리하면 다음과 같다.

| 항목 | 내용 |
|------|------|
| 파라미터 수 | 128B (1280억) |
| 아키텍처 | Dense (MoE 아님) |
| 컨텍스트 윈도우 | 256,000 토큰 |
| 라이선스 | Modified MIT (상업 이용 가능) |
| 배포 방식 | Hugging Face (오픈웨이트) |
| API 입력 가격 | $1.50 / 1M 토큰 |
| API 출력 가격 | $7.50 / 1M 토큰 |

256,000 토큰의 컨텍스트 윈도우는 기술 문서 수백 페이지를 한 세션에 올려놓고 작업하는 것과 맞먹는 크기다. 코드베이스 전체를 컨텍스트에 넣고 리팩토링을 진행하거나, 방대한 API 문서를 기반으로 코드를 생성하는 워크플로에 적합하다.

`dense` 모델이라는 점도 짚을 필요가 있다. DeepSeek V3나 Mixtral처럼 MoE(Mixture of Experts) 방식이 아니라 전통적인 Dense 트랜스포머 구조를 택했다. MoE 대비 추론 시 레이턴시가 다소 높을 수 있지만, 배치 처리 일관성과 예측 가능한 성능이 장점이다.

### 벤치마크 결과: 코딩 에이전트 특화 성능

Mistral이 공개한 벤치마크에서 Medium 3.5의 강점은 코딩과 도메인 특화 작업에 있다.

**SWE-bench Verified: 77.6%**

SWE-bench Verified는 GitHub에 실제 올라온 이슈(버그 리포트, 기능 요청)를 주고, 모델이 그 이슈를 해결하는 코드 패치를 자동으로 만들어낼 수 있는지 평가하는 벤치마크다. 단순한 코드 생성이 아니라 레포지토리 구조 파악, 연관 파일 탐색, 테스트 통과까지 요구하기 때문에 실제 개발 에이전트 성능과 높은 상관관계가 있다는 평가를 받는다.

77.6%라는 수치는 GPT-4o와 Claude Sonnet 4.5를 코딩 에이전트 관점에서 앞선 것이다. 분석 커뮤니티에서는 두 모델이 일반 지식(MMLU)이나 수학 추론에서 Medium 3.5와 비슷하거나 약간 앞서지만, 코딩 에이전트 특화 벤치마크에서는 Medium 3.5가 우위를 점했다는 분석을 내놓고 있다.

**Tau3-Telecom: 91.4%**

Tau3-Telecom은 통신 분야 전문 지식 및 문서 이해력을 평가하는 도메인 특화 벤치마크다. 91.4%는 해당 벤치마크 최상위권에 해당한다. Mistral이 유럽 엔터프라이즈 시장—특히 제조업, 통신, 금융 분야—을 타깃으로 삼고 있다는 전략적 흐름과도 맞닿아 있다.

### 가격 논쟁: "오픈소스면 왜 이렇게 비싸?"

릴리스 직후 AI 개발자 커뮤니티에서는 가격에 대한 비판이 쏟아졌다. API 기준 $1.5/M input, $7.5/M output은 Mistral의 이전 모델들(Mistral Large, Medium 3.1)보다 높은 수준이다. "오픈웨이트로 공개한다면서 API 가격은 왜 비싸냐"는 반응이 Hacker News, Reddit에서 많이 나왔다.

반론도 만만치 않다. 자체 호스팅을 하면 API 비용 자체가 발생하지 않는다. GPU 4개(예: H100 또는 A100)로 운영 가능하다고 알려진 만큼, 사용량이 일정 이상인 팀에서는 자체 배포가 장기적으로 더 경제적이다. 특히 월 수억 토큰 이상을 처리하는 서비스 입장에서는 클라우드 API 비용이 주요 인프라 비용이 되기 때문에, 오픈웨이트 자체 호스팅의 경제성은 규모에 따라 달라진다.

```text
예시 비교 (월 10억 토큰 처리 기준, 입력:출력 비율 2:1 가정)
- API 과금: 약 $3,833/월 (입력 $5 + 출력 $2.5K 수준)
- 자체 호스팅: 초기 GPU 구매/임대 비용 (H100 x4 기준)
  -> 초기 투자가 있지만 장기 운영 시 단위 비용 낮음
```

이 논쟁은 결국 "어떤 사용 패턴이냐"의 문제다. 빠르게 프로토타이핑하고 API로 편하게 쓰고 싶다면 유료 API, 데이터 보안이나 비용 통제가 중요하다면 자체 호스팅이 합리적이다.

### Mistral Vibe: 코딩 에이전트의 심장

Medium 3.5는 Mistral의 클라우드 코딩 에이전트 **Mistral Vibe**의 기본 모델이 됐다. Mistral Vibe는 장시간 실행되는 코드 작업—예를 들어 빌드 파이프라인 수정, 대규모 리팩토링, 테스트 자동화—을 클라우드 에이전트가 자율적으로 처리하는 서비스다.

기존 코딩 에이전트(Cursor, GitHub Copilot Workspace 등)는 OpenAI나 Anthropic API를 가져다 쓰는 구조인 반면, Mistral Vibe는 Mistral 자체 모델이 에이전트 로직 전체를 담당한다. 이는 Mistral이 파운데이션 모델에서 에이전트 서비스 레이어까지 수직 통합하겠다는 의지를 보여준다.

AI 비즈니스 분석가들은 이 구조를 두고 "Mistral이 단순한 모델 회사가 아니라 AI 인프라 스택 전체를 노리고 있다"는 평가를 내린다. Le Chat(Mistral의 챗 인터페이스)까지 합치면 Mistral은 모델-에이전트-채팅 인터페이스를 자체적으로 갖추게 된다.

### 오픈웨이트의 의미: 데이터 주권과 규제 적합성

Medium 3.5가 오픈웨이트로 공개된다는 점은 단순한 기술적 결정이 아니다. EU AI Act 시행 이후 유럽 기업들 사이에서는 외부 API에 민감한 데이터를 전송하는 것에 대한 우려가 커지고 있다. 특히 GDPR 관점에서 개인정보가 포함된 데이터를 외부 클라우드로 보내는 것은 법적 리스크가 될 수 있다.

이런 환경에서 자체 데이터센터 혹은 on-premises 환경에 올릴 수 있는 고성능 오픈웨이트 모델은 규제 적합성(compliance)의 대안이 된다. 의료, 금융, 법률 분야 기업들이 이 카드에 특히 주목하는 이유다.

개발자 커뮤니티 전반에서도 "이제 Claude나 GPT 수준의 코딩 성능을 자체 서버에서 낼 수 있는 선택지가 생겼다"는 반응이 이어지고 있다. 이전까지는 오픈소스 모델들이 성능 면에서 클로즈드 모델 대비 뒤처진다는 인식이 강했는데, Medium 3.5가 그 인식을 흔들기 시작했다는 평가다.

## 정리

- **Mistral Medium 3.5**는 2026년 4월 29일 출시된 128B 파라미터 오픈웨이트 모델로, 수정 MIT 라이선스 하에 자체 호스팅이 가능하다.
- SWE-bench Verified 77.6%로 코딩 에이전트 벤치마크에서 Claude Sonnet 4.5, GPT-4o를 앞섰다.
- API 가격($1.5/M input, $7.5/M output)은 비싸다는 비판을 받지만, 자체 호스팅 시 API 과금 자체가 없어진다.
- Mistral Vibe 코딩 에이전트의 코어로 채택돼 단순 모델 출시를 넘어 에이전트 서비스 수직 통합 전략의 일부다.
- 데이터 주권이나 규제 준수가 필요한 환경이라면, 성능 타협 없이 자체 호스팅할 수 있는 현실적인 선택지가 생겼다.

## Reference

- [Mistral AI - Mistral Medium 3.5 공식 모델 카드](https://docs.mistral.ai/models/model-cards/mistral-medium-3-5-26-04)
- [GIGAZINE - Mistral Medium 3.5 출시: Claude Sonnet 4.5 능가 (April 30, 2026)](https://gigazine.net/gsc_news/en/20260430-mistral-medium-3-5/)
- [Heise Online - Mistral AI: New Medium 3.5 Language Model and Cloud Coding Agents](https://www.heise.de/en/news/Mistral-AI-New-Medium-3-5-Language-Model-and-Cloud-Coding-Agents-11278054.html)
- [Decrypt - Mistral AI Drops New Open-Source Model](https://decrypt.co/366275/mistral-ai-open-source-model-agents-internet-not-impressed)
- [Lushbinary - Mistral Medium 3.5 vs Claude Sonnet 4 vs GPT-4o 벤치마크 비교](https://lushbinary.com/blog/mistral-medium-3-5-vs-claude-sonnet-gpt-4o-comparison/)
- [Pulse24.ai - Mistral AI Ships Medium 3.5 Model (April 29, 2026)](https://pulse24.ai/news/2026/4/29/23/mistral-ai-ships-medium-35-model)
