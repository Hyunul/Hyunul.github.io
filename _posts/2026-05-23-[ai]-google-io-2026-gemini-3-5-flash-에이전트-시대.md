---
title: "[AI] Google I/O 2026: Gemini 3.5 Flash, 에이전트 시대를 선언하다"
date: 2026-05-23 07:30:00 +09:00
categories: [AI]
tag: [Gemini, GoogleIO, LLM, AI에이전트, Antigravity]
---

## 서론

5월 19일, 구글은 매년 개최하는 개발자 컨퍼런스 Google I/O 2026에서 두 가지 큰 메시지를 던졌다. 하나는 "Gemini 3.5 Flash"라는 새로운 모델의 출시이고, 다른 하나는 AI가 이제 단순히 "답변하는 존재"를 넘어 "직접 행동하는 존재"로 진화했다는 선언이다. 이번 발표는 단순한 모델 업그레이드가 아니라 구글이 LLM 시장에서의 포지셔닝을 근본적으로 재정의하려는 시도라는 점에서 주목할 만하다.

특히 눈길을 끄는 건 모델의 성능 지표다. Gemini 3.5 Flash는 Flash 티어의 속도와 가격을 유지하면서도, 이전 세대 Pro 티어 모델을 여러 에이전트·코딩 벤치마크에서 앞질렀다. 저비용 고성능이라는 조합은 실무에서 LLM API를 사용하는 개발자와 서비스 기획자 모두에게 의미 있는 변화다. 같은 품질을 더 싸게 쓸 수 있다는 건, AI 기능을 제품에 녹이는 비용 구조 자체가 달라진다는 뜻이기도 하다.

이번 발표에서는 모델 하나만 나온 게 아니다. 에이전트 퍼스트 개발 플랫폼 Antigravity 2.0, 자율 코딩 에이전트 Jules, 멀티모달 생성 시리즈 Gemini Omni까지 묶음으로 쏟아졌다. 이번 글에서는 Gemini 3.5 Flash의 핵심 스펙·성능, 그리고 함께 발표된 에이전트 생태계의 변화를 정리해본다.

## 본론

### Gemini 3.5 Flash 핵심 스펙

Gemini 3.5 Flash는 Gemini 3.5 패밀리의 첫 번째 공개 모델이다. 구글은 이 모델을 "프론티어 수준의 지능과 에이전트 능력을 Flash 시리즈의 속도와 비용으로 제공한다"는 콘셉트로 발표했다. 공식 블로그(blog.google)에 명시된 스펙을 정리하면 다음과 같다.

| 항목 | 내용 |
|------|------|
| 공개 일자 | 2026년 5월 19일 (Google I/O 2026) |
| 컨텍스트 윈도우 | 1M 토큰 |
| 출력 속도 | 동급 프론티어 모델 대비 4배 빠름 |
| 입력 가격 | $1.50 / 1M 토큰 |
| 출력 가격 | $9.00 / 1M 토큰 |
| 이전 모델 대비 가격 | Gemini 3.1 Pro 대비 약 25% 저렴 |

가격에서 흥미로운 점은 Gemini 3.5 Flash가 전 세대 Pro 모델보다 실제로 더 저렴하다는 것이다. 성능은 올라가고 비용은 내려갔다는 주장이 마케팅 문구에 그치지 않고 벤치마크 수치로 뒷받침된다는 점이 이번 발표를 돋보이게 만든다.

### 벤치마크 성능: Flash가 Pro를 앞서다

구글이 공개한 벤치마크 결과는 꽤 인상적이다. 특히 에이전트 관련 태스크에서 두드러진다.

- **Terminal-Bench 2.1**: 76.2% — 터미널 기반 자율 에이전트 능력 평가, 이전 세대 Gemini 3.1 Pro 상회
- **GDPval-AA**: 1,656 Elo — 에이전트 평가 기준 업계 최상위권
- **MCP Atlas**: 83.6% — 멀티스텝 에이전트 태스크 벤치마크
- **CharXiv Reasoning**: 84.2% — 멀티모달 이해력·추론 평가

MCP Atlas와 Terminal-Bench 2.1은 에이전트가 실제 환경에서 복잡한 작업을 자율 수행하는 능력을 측정하는 기준이다. 기존에는 Pro 모델만이 이 구간을 주로 겨냥했는데, Flash 티어 모델이 해당 영역을 넘어섰다는 것은 의미 있는 전환점이다.

커뮤니티에서는 "이제 GPT-4o-mini급 저비용 모델 경쟁이 본격화될 것"이라는 반응이 주를 이루고 있다. 다만, 벤치마크는 항상 실제 운영 환경과 차이가 있다. 프롬프트 구성 방식이나 태스크 유형에 따라 체감 성능은 달라질 수 있으므로, 팀 내부에서 실제 워크로드를 기준으로 검증해보는 과정이 필요하다.

### Gemini 3.5 Pro는 6월로

이번 I/O에서 눈에 띄는 부재 중 하나는 Gemini 3.5 Pro다. 구글은 3.5 Pro를 내부적으로는 이미 테스트 중이며, 2026년 6월 출시를 목표로 한다고 밝혔다. 즉, 현재 공개된 3.5 Flash는 곧 나올 Pro 티어의 사전 포석이기도 하다.

같은 날 **Gemini Omni** 시리즈도 발표됐다. Omni는 이미지·오디오·비디오·텍스트를 입력받아 실제 세계 지식에 기반한 비디오를 출력하는 새로운 멀티모달 모델군이다. 텍스트 중심에서 영상 생성까지 LLM의 출력 경계를 확장하는 시도로 볼 수 있다.

### Antigravity 2.0: 에이전트 플랫폼의 진화

Gemini 3.5 Flash와 함께 가장 주목받은 발표가 **Antigravity 2.0**이다. Antigravity는 구글의 에이전트 퍼스트 개발 플랫폼으로, 이번에 2.0으로 업그레이드됐다.

주요 변경 사항:

1. **병렬 서브에이전트 오케스트레이션**: 복잡한 워크플로우를 여러 서브에이전트가 동시에 분담 처리할 수 있게 됐다.
2. **Antigravity CLI**: 커맨드라인에서 에이전트를 구성하고 실행하는 도구. 터미널 샌드박싱과 크리덴셜 마스킹이 기본 내장되어 있다.
3. **강화된 Git 정책**: 에이전트가 저장소를 다룰 때 적용되는 Git 정책이 하드닝됐다.
4. **속도 향상**: Gemini 3.5 Flash를 Antigravity 환경에서 구동하면 최대 12배 빠른 처리가 가능하다.

구글이 공개한 데모 중 인상적인 사례가 있었다. Antigravity + Gemini 3.5 Flash를 활용해 93개의 병렬 서브에이전트, 15,000개 이상의 모델 요청, 26억 토큰을 소비해 약 12시간 만에 동작하는 OS를 구축했다는 것이다. API 비용은 1,000달러 미만이었다고 구글은 밝혔다. 이 데모가 실제 운영 수준의 일반적인 프로젝트에 얼마나 적용 가능할지는 두고 봐야 하겠지만, 에이전트 기반 대형 태스크의 가능성을 보여준다는 점에서 커뮤니티 반응은 뜨거웠다.

개발자 커뮤니티에서는 Antigravity CLI가 기존 로컬 AI 코딩 도구들과 어떻게 차별화될지에 대한 논의도 활발하다. 보안 샌드박싱과 크리덴셜 관리가 기본 내장됐다는 점은 기업 환경에서 에이전트를 안전하게 사용하려는 팀에게 특히 관심을 끌 만한 부분이다.

### Jules: GitHub 자율 코딩 에이전트

이번 I/O에서 개발자에게 중요한 또 다른 발표가 **Jules**다. Jules는 GitHub와 통합되는 자율 코딩 에이전트다. PR 리뷰, 버그 수정, 코드 생성을 GitHub 인터페이스 내에서 직접 처리할 수 있도록 설계됐다. GitHub Copilot과 직접 경쟁 구도를 형성하는 제품이며, 구글의 AI 개발 도구 전략에서 중요한 축을 담당한다.

### AI Mode in Search: 검색에서 에이전트로

**AI Mode in Google Search**는 기존 AI Overviews를 넘어 정보 에이전트화된 검색 경험을 제공한다. 사용자가 설정한 주제를 24시간 7일 내내 모니터링하고, 관련 정보가 새로 등장하면 알림을 주는 기능이 추가됐다. 단순 질의응답 도구에서 지속적 모니터링 에이전트로의 전환이다.

이 기능은 개발자보다는 일반 사용자와 정보 분석가에게 더 즉각적인 임팩트를 줄 수 있다. 하지만 내부적으로 Gemini 3.5 Flash가 이 서비스의 핵심 추론 엔진으로 사용된다는 점에서, 대규모 트래픽을 처리하는 고속 Flash 모델의 실전 투입 사례로도 읽을 수 있다.

### 가용성

Gemini 3.5 Flash는 5월 19일부터 아래 경로로 접근 가능하다:

- **Gemini 앱** (웹·모바일)
- **AI Mode in Google Search**
- **Gemini API** — Google AI Studio, Android Studio
- **Antigravity 2.0** — Interactions API 포함
- **Gemini Enterprise Agent Platform**

개발자 입장에서는 Gemini API를 통해 바로 테스트해볼 수 있다. 1M 토큰의 컨텍스트 윈도우는 긴 문서 분석이나 대규모 코드베이스 처리에 유리하다. 기존에 Gemini 3.1 Pro를 사용하고 있던 팀이라면 동일한 API 구조로 3.5 Flash로 전환만 해도 비용 절감과 성능 향상을 동시에 얻을 수 있는 구조다.

### 업계 반응

MarkTechPost, WaveSpeed Blog, Latent Space 등 AI 미디어에서는 이번 발표를 "Flash 티어가 드디어 Pro 티어와 경쟁하는 시대"로 정의하는 반응이 많았다. 특히 Gemini 3.5 Flash가 에이전트 벤치마크에서 높은 점수를 기록했다는 점 때문에, 코딩 에이전트나 자동화 워크플로우를 구축하는 팀에서 빠르게 채택을 검토하고 있다는 분위기가 형성됐다.

한편 경쟁 모델인 Claude Sonnet 4, GPT-4o 대비 실제 품질 비교를 요구하는 목소리도 있다. 현재까지 공개된 수치는 구글이 직접 측정한 벤치마크이기 때문에, 독립 평가 기관들의 검증 결과가 나오면 그때 다시 한번 비교해볼 필요가 있다.

## 정리

- **Gemini 3.5 Flash**는 2026년 5월 19일 Google I/O 2026에서 공개됐으며, Flash 티어임에도 이전 세대 Pro 티어를 주요 에이전트·코딩 벤치마크에서 앞선다.
- 가격은 $1.50/$9.00 per 1M 토큰으로 Gemini 3.1 Pro 대비 약 25% 저렴하고, 동급 프론티어 모델 대비 4배 빠르다.
- **Antigravity 2.0**과 결합 시 최대 12배 속도로 병렬 에이전트 워크플로우 실행이 가능하며, 93개 서브에이전트 동시 운용 데모가 공개됐다.
- **Gemini 3.5 Pro**는 6월 출시 예정, 현재 구글 내부 테스트 중이다.
- **Jules**(GitHub 자율 코딩 에이전트), **Gemini Omni**(멀티모달 비디오 생성 시리즈), **AI Mode in Search**도 함께 발표됐다.
- 커뮤니티에서는 Flash 티어 모델의 성능 급등이 AI 서비스 비용 구조를 낮추는 방향으로 작용하고, 저비용 모델 시장 경쟁이 더욱 치열해질 것이라는 전망이 지배적이다.
- 다만 구글 자체 측정 벤치마크이므로, 독립 평가 기관의 검증 결과를 병행해 확인하는 것이 좋다.

## Reference

- [Gemini 3.5: frontier intelligence with action — Google Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5/)
- [All the news from the Google I/O 2026 Developer keynote — Google Developers Blog](https://developers.googleblog.com/all-the-news-from-the-google-io-2026-developer-keynote/)
- [I/O 2026 developer highlights: Antigravity, Gemini API, AI Studio — Google Blog](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/)
- [Google Introduces Gemini 3.5 Flash at I/O 2026 — MarkTechPost](https://www.marktechpost.com/2026/05/20/google-introduces-gemini-3-5-flash-at-i-o-2026-a-faster-and-cheaper-model-for-ai-agents-and-coding/)
- [With Gemini 3.5 Flash, Google bets its next AI wave on agents, not chatbots — TechCrunch](https://techcrunch.com/2026/05/19/with-gemini-3-5-flash-google-bets-its-next-ai-wave-on-agents-not-chatbots/)
- [Gemini 3.5 Flash Shipped — Flash-Tier Model Leads Agent Benchmarks — WaveSpeed Blog](https://wavespeed.ai/blog/posts/gemini-3-5-flash-shipped-leads-agent-benchmarks/)
- [AINews: Google I/O 2026 — Gemini 3.5 Flash, Omni, Antigravity 2.0 — Latent Space](https://www.latent.space/p/ainews-google-io-2026-gemini-35-flash)
- [Everything Google announced at I/O 2026 — 9to5Google](https://9to5google.com/2026/05/19/google-io-2026-news/)
