---
title: "[AI] DeepSeek V4 출시 — 프론티어와의 격차를 좁힌 오픈소스 거인"
date: 2026-04-26 09:00:00 +09:00
categories: [AI]
tag: [DeepSeek, LLM, OpenSource, MoE, AI인프라]
---

## 서론

중국 AI 스타트업 DeepSeek이 2026년 4월 24일, V4 시리즈를 공개하며 다시 한번 업계의 이목을 집중시켰다. 약 1년 전 V3 모델로 오픈소스 AI 생태계를 뒤흔들었던 DeepSeek이, 이번에는 **V4-Pro**와 **V4-Flash**라는 두 가지 모델을 동시에 출시했다. 두 모델 모두 MIT 라이선스로 공개되어 상업적 활용도 자유롭고, 출시 당일 DeepSeek API와 Hugging Face를 통해 가중치까지 즉시 이용할 수 있게 됐다.

특히 주목할 점은 이번 모델들이 **프론티어 모델과의 격차를 눈에 띄게 좁혔다**는 것이다. 코딩·수학·추론 등 핵심 벤치마크에서 GPT-5.5, Claude Opus 4.7 등 최상위 클로즈드소스 모델들과 경쟁하면서도, API 요금은 이들의 약 1/6 수준에 불과하다. Bloomberg, TechCrunch, Fortune 등 복수의 주요 매체가 이를 집중 보도했으며, 개발자 커뮤니티에서도 즉각적인 반응이 쏟아졌다.

DeepSeek V4가 무엇을 새롭게 가져왔고, 어떤 기술적 기반 위에 서 있으며, 실제로 쓸 만한지 차근차근 살펴보자.

## 본론

### 두 모델의 구성: V4-Pro와 V4-Flash

DeepSeek V4 시리즈는 용도에 따라 두 가지 모델로 나뉜다. 둘 다 Mixture-of-Experts(MoE) 아키텍처를 기반으로 하지만, 규모와 가격·성능 트레이드오프가 다르다.

| 항목 | V4-Pro | V4-Flash |
|---|---|---|
| 총 파라미터 | 1.6조 (1.6T) | 2,840억 (284B) |
| 활성 파라미터 | 490억 (49B) | 130억 (13B) |
| 컨텍스트 윈도우 | 100만 토큰 | 100만 토큰 |
| 입력 요금 ($/M tokens) | $1.74 | $0.14 |
| 출력 요금 ($/M tokens) | $3.48 | $0.28 |
| 라이선스 | MIT | MIT |
| 추론 속도 | - | 약 84 토큰/초 |

V4-Pro는 복잡한 추론·코딩 작업에 최적화된 플래그십 모델이고, V4-Flash는 빠른 응답 속도와 낮은 비용이 필요한 실시간 서비스에 적합하다. 두 모델 모두 컨텍스트 윈도우가 100만 토큰이라는 점이 눈에 띈다. 기존 대부분의 모델이 32K~200K 수준에 머물렀던 것과 비교하면 파격적인 규모다.

MoE 구조를 간단히 설명하면, 모델 전체에 수천억~수조 개의 파라미터가 있지만 각 토큰을 처리할 때는 일부 "전문가(expert)" 레이어만 활성화된다. 따라서 총 파라미터가 1.6T라고 해서 실제 추론 비용이 1.6T짜리 dense 모델과 같지 않다. V4-Pro의 경우 토큰당 49B 활성 파라미터만 사용하므로 실제 연산량은 훨씬 적다.

### 핵심 기술: Hybrid Attention Architecture

V4의 가장 주목할 기술 혁신은 DeepSeek이 독자적으로 명명한 **Hybrid Attention Architecture**다. Compressed Sparse Attention(CSA)과 Heavily Compressed Attention(HCA)을 결합한 새로운 어텐션 메커니즘을 도입했다.

기존 트랜스포머 구조에서 100만 토큰 수준의 긴 컨텍스트를 처리하면 KV 캐시 크기와 어텐션 연산량이 입력 길이의 제곱에 비례해 늘어난다. 실용적으로 1M 토큰 컨텍스트를 지원하려면 메모리와 연산 비용 문제를 어떻게든 해결해야 한다.

DeepSeek이 공개한 수치에 따르면, 동일한 100만 토큰 입력 시 V4-Pro는 이전 버전 V3.2 대비:
- 단일 토큰 추론 FLOPs의 **27%** 수준
- KV 캐시 사용량의 **10%** 수준

에 불과하다. 사실상 같은 컨텍스트 처리를 훨씬 적은 자원으로 해낸다는 뜻이다.

이 덕분에 100만 토큰 컨텍스트가 실험실 수치에 그치지 않고 실용적인 영역에 들어왔다. 예를 들어, 대규모 코드베이스 전체를 단일 프롬프트에 넣어 분석하거나, 긴 법률 문서 수십 편을 한꺼번에 처리하는 작업이 현실적인 비용 범위 안으로 들어오게 됐다.

### 벤치마크: 프론티어와의 거리

DeepSeek이 함께 공개한 벤치마크 수치는 인상적이다.

- **MMLU**: 88.4%
- **Humanities-X 추론**: 92.1%
- **Agentic 코딩**: 오픈소스 모델 중 최고 수준

VentureBeat의 보도에 따르면, MMLU와 Humanities-X에서 기록한 수치는 이번 분기에 출시된 GPT-5.5, Claude Opus 4.7과 대등하거나 소폭 앞서는 결과다.

다만, **세계 지식(World Knowledge)** 부문에서는 Google Gemini 3.1 Pro에 소폭 뒤처지는 모습이 확인됐다. The Next Web은 전반적인 평가로 "현재 최상위 프론티어 모델들보다 약 3~6개월 뒤처진 개발 궤적"이라는 표현을 사용했다.

그럼에도 가격 대비 성능 측면에서는 뚜렷한 우위가 있다.

| 모델 | 입력 요금 ($/M) | 출력 요금 ($/M) |
|---|---|---|
| DeepSeek V4-Pro | $1.74 | $3.48 |
| DeepSeek V4-Flash | $0.14 | $0.28 |
| GPT-5.5 (추정) | ~$15 | ~$60 |
| Claude Opus 4.7 (추정) | ~$15 | ~$75 |

동급 수준의 추론 품질을 제공하면서 가격은 1/6 이하라는 사실은, API 호출 비용에 민감한 서비스를 운영하는 팀에게 실질적인 대안을 제시한다.

### 하드웨어: Huawei Ascend 칩과의 통합

Fortune의 보도에 따르면, V4 시리즈는 Huawei Ascend 칩과의 긴밀한 통합을 특징으로 한다. 미국의 AI 반도체 수출 규제로 최신 NVIDIA GPU 접근이 제한된 상황에서, DeepSeek은 중국산 하드웨어 생태계에서도 경쟁력 있는 모델을 학습·배포하는 데 성공했다. 이는 단순한 AI 기술 경쟁을 넘어, 하드웨어 공급망 제약 속에서 소프트웨어 아키텍처로 차별화를 만들어낸 사례로 평가된다.

### Hugging Face와 오픈 소스 접근성

V4-Flash와 V4-Pro 모두 Hugging Face(`deepseek-ai/DeepSeek-V4-Flash`, `deepseek-ai/DeepSeek-V4-Pro`)를 통해 가중치가 공개됐다. MIT 라이선스이므로 상업적 파생 모델 생성, 파인튜닝, 로컬 배포 모두 가능하다.

직접 API를 써보고 싶다면 DeepSeek 공식 API 문서에서 엔드포인트를 확인할 수 있다. OpenAI 호환 형식의 API를 제공하므로, 기존에 OpenAI SDK를 사용하는 코드에서 `base_url`과 `api_key`만 바꾸면 거의 바로 연동이 된다.

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key="YOUR_DEEPSEEK_API_KEY",
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "안녕하세요!"}],
)
print(response.choices[0].message.content)
```

기존 OpenAI 연동 코드에서 모델 이름과 엔드포인트만 바꾸면 전환이 가능하다는 점이 개발자 친화적인 부분이다.

### 업계 및 커뮤니티 반응

Bloomberg는 이번 출시를 "V3 출시 1년 만에 다시 실리콘밸리에 경종을 울리는 등장"으로 묘사했다. DeepSeek V3가 출시됐을 때 미국 AI 기업들의 주가가 일제히 흔들렸던 것처럼, 이번 V4 역시 비용 효율성 면에서 기존 클로즈드소스 모델들의 가격 정책에 의문을 던지는 계기가 됐다는 평이다.

Euronews는 "중국의 AI 기술력이 서방 모델들과의 격차를 빠르게 좁히고 있음을 다시 한번 입증했다"고 평가했다. 개발자 커뮤니티에서는 "가격 때문에라도 V4-Flash를 먼저 테스트해볼 만하다"는 반응이 많았다.

반면 비판적인 시각도 있다. The Next Web의 분석에 따르면, 세계 지식 기반 질문에서 Google의 Gemini 3.1 Pro에 미치지 못했고, 전반적으로 3~6개월의 개발 격차가 여전히 존재한다는 평가다. "프론티어에 근접했지만 아직 프론티어는 아니다"라는 표현이 균형 잡힌 평가로 자주 인용된다.

## 정리

- DeepSeek V4-Pro(1.6T 총 파라미터, 49B 활성)와 V4-Flash(284B 총 파라미터, 13B 활성)가 2026년 4월 24일 MIT 라이선스로 공개됐다.
- Hybrid Attention Architecture(CSA+HCA)로 100만 토큰 컨텍스트를 V3.2 대비 27% FLOPs, 10% KV 캐시만으로 처리할 수 있다.
- 주요 벤치마크(MMLU 88.4%, Humanities-X 92.1%)에서 프론티어 클로즈드소스 모델과 대등한 성능을 보이며, 가격은 약 1/6 수준이다.
- 세계 지식 분야에서 Gemini 3.1 Pro에 다소 뒤처지고, 전반적으로 "3~6개월 격차"라는 평가도 병존한다.
- OpenAI 호환 API로 제공되어 기존 코드에서 base_url과 모델명만 바꾸면 바로 전환 가능하다.
- Hugging Face에 MIT 라이선스로 가중치가 공개되어 파인튜닝·로컬 배포까지 자유롭다.
- API 비용에 민감한 서비스라면 V4-Flash를, 최고 품질의 추론이 필요한 작업이라면 V4-Pro를 우선 검토해볼 만하다.

## Reference

- [DeepSeek V4 Preview Release — DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424)
- [DeepSeek previews new AI model that 'closes the gap' with frontier models — TechCrunch](https://techcrunch.com/2026/04/24/deepseek-previews-new-ai-model-that-closes-the-gap-with-frontier-models/)
- [DeepSeek Unveils Newest Flagship AI Model a Year after Upending Silicon Valley — Bloomberg](https://www.bloomberg.com/news/articles/2026-04-24/deepseek-unveils-newest-flagship-a-year-after-ai-breakthrough)
- [DeepSeek V4 arrives with near state-of-the-art intelligence at 1/6th the cost of Opus 4.7, GPT-5.5 — VentureBeat](https://venturebeat.com/technology/deepseek-v4-arrives-with-near-state-of-the-art-intelligence-at-1-6th-the-cost-of-opus-4-7-gpt-5-5)
- [DeepSeek returns with V4-Pro and V4-Flash, a year after its 'Sputnik moment' — The Next Web](https://thenextweb.com/news/deepseek-v4-pro-flash-launch-open-source)
- [DeepSeek unveils V4 model, with rock-bottom prices and close integration with Huawei's chips — Fortune](https://fortune.com/2026/04/24/deepseek-v4-ai-model-price-performance-china-open-source/)
- [China's DeepSeek releases preview of long-awaited V4 model — CNBC](https://www.cnbc.com/2026/04/24/deepseek-v4-llm-preview-open-source-ai-competition-china.html)
