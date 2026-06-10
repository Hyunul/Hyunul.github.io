---
title: "[AI] Anthropic, Claude Fable 5·Mythos 5 출시 — Mythos 클래스가 드디어 일반 공개됐다"
date: 2026-06-11 07:06:07 +09:00
categories: [AI]
tag: [Anthropic, ClaudeFable5, Mythos, LLM, AI안전성]
---

## 서론

2026년 6월 9일, Anthropic이 **Claude Fable 5**와 **Claude Mythos 5**를 동시에 발표했다. 이름만 들으면 단순한 모델 업데이트처럼 보이지만, 이번 발표는 AI 업계에서 꽤 큰 의미를 갖는다.

핵심은 **Mythos 클래스가 일반에 공개됐다는 점**이다. 지금까지 Anthropic의 Mythos 모델은 Project Glasswing을 통해 AWS, Apple, Cisco, Google, JPMorgan Chase, Microsoft 같은 극히 일부 전략 파트너에게만 프리뷰로 제공되던 상태였다. Claude Fable 5는 이 Mythos 클래스 역량을 기반으로 개발된 첫 번째 광범위 공개 모델이다. 즉, 일반 개발자와 기업이 처음으로 Mythos 수준의 성능에 접근할 수 있게 된 셈이다.

타이밍도 주목할 만하다. Anthropic은 불과 며칠 전인 6월 5일, **"When AI Builds Itself"**라는 보고서를 통해 AI가 재귀적 자기개선(Recursive Self-Improvement) 임계점에 가까워지고 있다는 경고를 내놓았다. 2026년 5월 기준으로 Anthropic 내부 코드의 80% 이상을 Claude가 작성하고 있으며, 이 수치가 90%를 넘겼다는 보도도 있었다. 그 직후에 역대 가장 강력한 공개 모델을 출시한다는 게 일견 모순처럼 보이기도 한다. NBC News는 이를 두고 "AI가 너무 위험해지고 있다고 경고한 지 며칠 만에 가장 강력한 모델을 공개했다"고 표현했고, TechCrunch 역시 이 아이러니를 헤드라인으로 끌어올렸다.

이번 포스트에서는 Claude Fable 5의 성능 지표, 가격 구조, 안전 제한, 그리고 경쟁 구도와 업계 반응까지 정리해본다.

## 본론

### Fable 5란 무엇인가: Mythos 클래스의 공개 버전

먼저 네이밍 구조를 이해하는 게 좋다. Anthropic의 현재 최상위 모델 라인은 **Mythos**다. Claude Mythos 5는 이 라인의 최신 버전으로, 6월 9일 발표 기준 Project Glasswing을 통한 제한적 접근만 가능하다. 반면 **Claude Fable 5**는 Mythos와 동일한 기술 기반 위에서 개발됐지만, 범용 공개 API를 통해 누구나 사용할 수 있도록 배포된 모델이다.

Anthropic은 Fable 5에 대해 "지금까지 일반 공개한 모델 중 가장 강력한 것"이라고 설명했다. 소프트웨어 엔지니어링, 지식 집약 업무, 비전(이미지 이해), 과학 연구 등 다양한 영역에서 이전 공개 모델들을 크게 앞선다는 설명이다. VentureBeat는 이를 "Anthropic이 Mythos를 대중화한 순간"이라고 표현했다.

### 주요 벤치마크 성능

기술 지표 측면에서 Fable 5가 공개한 수치는 인상적이다:

- **SWE-bench Verified**: **95%**
- **SWE-bench Pro**: **80%**

SWE-bench는 실제 GitHub 이슈를 자동으로 해결하는 능력을 측정하는 소프트웨어 엔지니어링 벤치마크다. Verified는 상대적으로 검증된 태스크, Pro는 더 어려운 실전 수준의 태스크를 포함한다. 95%와 80%라는 수치는 현재 공개된 모델 중 최상위권이다.

2026년 AI 코딩 에이전트 경쟁에서 SWE-bench 성능은 핵심 지표로 자리잡았다. Fable 5의 80% SWE-bench Pro 달성은 실제 현업 코드베이스 수준의 복잡한 이슈를 높은 정확도로 처리할 수 있다는 신호다. 이는 Claude Code, Copilot 등 코딩 에이전트에 실질적으로 Mythos급 성능을 적용할 수 있게 됐다는 의미이기도 하다.

### 가격과 컨텍스트 창

API 기준 가격 구조는 다음과 같다:

| 항목 | 가격 |
|------|------|
| 입력 토큰 | **$10 / 1M 토큰** |
| 출력 토큰 | **$50 / 1M 토큰** |
| 최대 출력 | **128,000 토큰** |

128k 출력 토큰은 단일 응답에서도 방대한 코드베이스 분석이나 긴 기술 문서 작성이 가능한 수준이다. 이전 공개 모델들의 출력 제한과 비교했을 때 상당히 확장된 수치다.

구독 플랜 측면에서는 **6월 22일까지** Pro, Max, Team, seat-based Enterprise 플랜에서 추가 비용 없이 Fable 5를 사용할 수 있다. 그 이후인 **6월 23일부터**는 사용량 크레딧(usage credits) 방식으로 전환된다.

### 안전 제한: 고위험 영역에서 하드 차단

Fable 5는 강력한 성능과 함께 특정 영역에서 **하드 안전 제한(Hard Safety Limits)**을 적용한다. 구체적으로 차단되는 영역:

- **사이버보안**: 공격 도구, 익스플로잇 개발, 취약점 무기화
- **생물학**: 병원체 설계 등 바이오안보 위험 영역
- **화학**: 독성물질 합성 등 위험 화학 관련
- **증류 공격**: 다른 LLM 모델 모방 또는 지식 추출 시도

이 영역에서는 Fable 5의 응답이 차단되고 Claude Opus 4.8으로 **폴백(fallback)**된다. "When AI Builds Itself" 경고를 발표한 지 며칠 안 된 시점에서 이런 하드 제한을 설계해 내장한 것은, Anthropic이 말하는 "책임감 있는 스케일링(Responsible Scaling)" 정책의 실천으로 읽힌다.

Yahoo Finance와 SD Times의 보도에 따르면, 하드 안전 제한은 Fable 5 출시 결정에서 가장 오래 논의된 부분 중 하나였다고 전해진다.

### Claude Mythos 5: 여전히 제한적 접근

Claude Mythos 5 자체는 이번에 함께 발표됐지만, 일반 공개는 아니다. 계속해서 Project Glasswing 채널을 통해 선별된 기업 파트너에게만 프리뷰로 제공된다. Fable 5가 Mythos를 "대중화"했다면, Mythos 5 자체는 여전히 최첨단 연구와 전략적 파트너십 영역에 머무른다. Glasswing을 통한 파트너 네트워크는 이전 발표 기준으로 AWS, Apple, Cisco, Google, JPMorgan Chase, Microsoft 등 약 150여 개 조직으로 확대됐다.

### 가용성: Claude API와 Amazon Bedrock

Fable 5는 출시일인 6월 9일부터 **Claude API**와 **Amazon Bedrock** 양쪽에서 즉시 사용 가능하다. Amazon은 별도의 공식 발표(aboutamazon.com)를 통해 Bedrock에서의 가용성을 확인했다.

이는 기존에 AWS 기반으로 LLM을 통합한 엔터프라이즈 고객들이 별도의 마이그레이션이나 플랫폼 변경 없이 곧바로 Fable 5로 업그레이드할 수 있다는 의미다. CNBC는 "Anthropic이 Bedrock을 통해 엔터프라이즈 시장 공략에 나선다"고 분석했다.

### 경쟁 구도: GPT-5.5 vs. Gemini 3.5 Pro vs. Fable 5

Fable 5 출시 시점의 주요 경쟁 모델 비교:

| 모델 | 제공사 | 공개 여부 | 비고 |
|------|--------|----------|------|
| Claude Fable 5 | Anthropic | **GA (일반 공개)** | Mythos급 공개 모델 |
| Claude Mythos 5 | Anthropic | 제한 preview | Project Glasswing |
| GPT-5.5 / GPT-5.5 Pro | OpenAI | 공개 | Pro 버전 별도 |
| Gemini 3.5 Pro | Google | 제한 preview | GA 미정 |

Google Gemini 3.5 Pro는 5월 Google I/O에서 발표 후 아직 일반 GA가 이루어지지 않아, 현시점에서 Mythos급 역량을 일반 공개한 것은 Anthropic이 최초다. 이 타이밍 우위가 실제로 개발자 채택에 영향을 줄 수 있다는 것이 업계 분석이다.

### 6월 23일 이후 크레딧 구조의 의미

6월 23일 이후 Pro/Max/Team 플랜에서 Fable 5가 사용량 크레딧 방식으로 전환된다는 점은 주목할 만하다. Anthropic이 구독 플랜 사용자에게 약 2주간의 "맛보기" 기간을 제공하고, 이후 실제 사용량 기반 과금으로 전환하는 전략이다. 이는 API 사용자(기업)와 구독 사용자(개인/팀) 모두에게 Fable 5를 경험시킨 뒤, 실질적인 수요를 기반으로 한 과금 모델로 이행하는 구조다.

## 정리

Claude Fable 5 출시를 두고 업계 반응은 크게 두 축으로 나뉜다. 하나는 "드디어 Mythos 수준 성능이 일반에 풀렸다"는 기대감이고, 다른 하나는 "AI 위험 경고 직후에 이게 맞는 타이밍인가?"라는 물음이다.

VentureBeat는 이번 발표를 "Anthropic이 Mythos를 대중화한 순간"이라고 평가했다. CNBC는 Fable 5가 AWS Bedrock을 통해 엔터프라이즈 시장을 공략한다는 점에 주목했다. 반면 NBC News와 TechCrunch는 "When AI Builds Itself" 경고와의 타이밍 모순을 집중 조명했다. 경고를 발표한 당사자가 며칠 후 그 역량의 공개 버전을 출시하는 것은, 업계에서 이미 예견되던 "말과 행동의 간극"에 관한 논쟁을 다시 점화시켰다.

Anthropic 입장에서 보면, 하드 안전 제한을 내장하면서도 최고 성능 모델을 공개한 것은 "책임감 있는 스케일링"을 실천한다는 메시지로 읽힌다. 6월 23일 크레딧 방식 전환 이후 실제 채택률과 사용 패턴이 어떻게 나올지, 그리고 Gemini 3.5 Pro GA 시점에 경쟁 구도가 어떻게 달라질지가 향후 관전 포인트다.

## Reference

- [Anthropic releases Mythos-like AI model to the public, Claude Fable 5 - CNBC](https://www.cnbc.com/2026/06/09/anthropic-mythos-claude-fable-5.html)
- [Anthropic releases Fable 5 model, built on the same tech that spooked the government - NBC News](https://www.nbcnews.com/tech/security/fable-5-anthropic-release-public-mythos-claude-model-rcna349104)
- [Claude Fable 5 from Anthropic now available on Amazon Bedrock - Amazon](https://www.aboutamazon.com/news/aws/claude-fable-5-anthropic-available-amazon-bedrock)
- [Anthropic's Claude Fable 5 and Mythos 5 Launch: What To Know - Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/anthropic-claude-mythos-launches-today-142844796.html)
- [Anthropic releases Claude Fable 5, Mythos 5 - SD Times](https://sdtimes.com/anthropic-releases-claude-fable-5-claud-mythos-5/)
- [Anthropic brings Mythos to the masses with Claude Fable 5 - VentureBeat](https://venturebeat.com/technology/anthropic-brings-mythos-to-the-masses-with-claude-fable-5-its-most-powerful-generally-available-model-ever)
- [Anthropic releases Claude Fable 5 for Broad Use - Let's Data Science](https://letsdatascience.com/news/anthropic-releases-claude-fable-5-for-broad-use-db880a41)
