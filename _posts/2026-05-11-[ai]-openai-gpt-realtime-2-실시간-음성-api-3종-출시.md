---
title: "[AI] OpenAI GPT-Realtime-2/Translate/Whisper — 실시간 음성 API 3종 동시 출시"
date: 2026-05-11 07:01:23 +09:00
categories: [AI]
tag: [OpenAI, GPT-Realtime, 음성AI, API, 실시간번역]
---

## 서론

2026년 5월 7~8일, OpenAI가 실시간 음성 처리 API 세 종류를 동시에 공개하면서 AI 개발자 커뮤니티가 다시 한번 들썩였다. **GPT-Realtime-2**, **GPT-Realtime-Translate**, **GPT-Realtime-Whisper** — 이 세 모델은 각각 실시간 대화, 실시간 번역, 실시간 전사(STT)를 담당하며, Realtime API가 베타 딱지를 떼고 정식 GA(General Availability)로 전환하는 시점에 맞춰 함께 발표됐다.

기존 AI 음성 기술은 크게 두 가지 한계를 안고 있었다. 첫째, 사전 녹음된 오디오를 일괄(batch) 처리하는 방식이라 실시간 대화에 적합하지 않았다. 둘째, 번역·전사·대화 기능이 각각 별도 파이프라인으로 분리돼 있어 통합 구축이 복잡하고 레이턴시가 누적됐다. OpenAI의 이번 릴리스는 이 두 가지 제약을 동시에 해결하는 시도로 평가받고 있다.

OpenAI가 2025년 가을 처음 선보인 Realtime API는 WebSocket 및 WebRTC 기반으로 오디오 스트림을 실시간으로 처리할 수 있는 구조였지만, 모델 성능과 언어 지원 폭에서 한계가 있다는 개발자 커뮤니티의 피드백이 꾸준히 있었다. 이번 3종 모델 공개는 그 한계를 상당 부분 극복한 '2세대' 실시간 음성 AI 제품군이라는 점에서 업계의 주목을 받고 있다.

특히 GPT-Realtime-Translate는 70개 이상의 입력 언어를 13개 출력 언어로 실시간 변환하는 동시통역 기능을 API 형태로 제공한다고 밝혔다. 다국어 화상 회의, 콜센터 자동화, 국제 고객 응대처럼 실시간 음성 처리가 핵심인 업무 영역에서 당장 활용 가능성이 높다는 반응이 나왔다. 개발자 포럼과 AI 테크 미디어에서는 "드디어 프로덕션에서 쓸 수 있는 수준의 실시간 음성 API가 나왔다"는 평가가 잇따랐다.

## 본론

### GPT-Realtime-2: GPT-5 추론 능력을 실시간 음성으로

GPT-Realtime-2는 이전 세대(GPT-Realtime-1.5) 대비 추론 능력이 크게 향상된 실시간 음성 대화 모델이다. OpenAI가 공개한 벤치마크 결과에 따르면, 오디오 이해력을 평가하는 **Big Bench Audio** 기준으로 이전 모델 대비 **15.2% 높은 점수**를, 복잡한 오디오 명령 이해를 평가하는 **Audio MultiChallenge**에서는 **13.8% 높은 점수**를 기록했다.

가장 주목할 만한 변화는 대화 도중 도구(tool)를 호출하고 다단계 작업을 실행할 수 있다는 점이다. 기존 Realtime API가 단순한 '묻고 답하기' 구조였다면, GPT-Realtime-2는 복잡한 에이전트 워크플로를 대화 중에 처리할 수 있는 구조로 전환됐다.

예를 들어, 사용자가 음성으로 "오늘 오후 3시에 팀 회의 잡아줘"라고 말하면, 모델이 대화 흐름을 끊지 않고 캘린더 API를 호출해 일정을 등록하고, 그 결과를 자연스러운 음성으로 돌려준다. 코드 측면에서 tool calling 구조는 Chat Completions API의 그것과 유사하지만, 모든 상호작용이 스트리밍 오디오로 이뤄진다는 차이가 있다:

```javascript
// WebSocket 방식으로 GPT-Realtime-2 연결 + 도구 정의 예시
const WebSocket = require('ws');

const ws = new WebSocket('wss://api.openai.com/v1/realtime', {
  headers: {
    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
    'OpenAI-Beta': 'realtime=v1'
  }
});

ws.on('open', () => {
  ws.send(JSON.stringify({
    type: 'session.update',
    session: {
      model: 'gpt-realtime-2',
      modalities: ['text', 'audio'],
      voice: 'alloy',
      input_audio_format: 'pcm16',
      output_audio_format: 'pcm16',
      tools: [
        {
          type: 'function',
          name: 'create_calendar_event',
          description: '지정된 시간에 캘린더 이벤트를 생성합니다',
          parameters: {
            type: 'object',
            properties: {
              title: { type: 'string' },
              start_time: { type: 'string', format: 'date-time' }
            },
            required: ['title', 'start_time']
          }
        }
      ]
    }
  }));
});
```

또한 OpenAI는 이번 모델이 턴(turn) 감지를 더욱 자연스럽게 처리한다고 밝혔다. 사람이 말을 멈추는 타이밍 인식, 중간에 끊기는 발화 처리, 배경 소음 필터링 등이 개선됐으며, 이를 통해 음성 에이전트의 자연스러움이 체감상으로도 크게 향상됐다는 평가가 나오고 있다.

### GPT-Realtime-Translate: API로 구현하는 동시 통역

GPT-Realtime-Translate는 음성을 입력 받아 다른 언어의 음성으로 즉시 출력하는 실시간 통역 모델이다. OpenAI가 공개한 스펙 정보는 다음과 같다:

| 항목 | 스펙 |
|------|------|
| 입력 언어 | 70개 이상 |
| 출력 언어 | 13개 |
| 동작 방식 | 화자 발화 속도에 맞춰 실시간 번역 음성 출력 |
| 연결 방식 | WebSocket / WebRTC |

지원 출력 언어에는 영어, 한국어, 일본어, 중국어(간체/번체), 스페인어, 포르투갈어, 프랑스어, 독일어, 이탈리아어, 아랍어 등이 포함된다.

중요한 점은 단순 텍스트 번역이 아니라 화자의 발화 속도와 어조를 어느 정도 반영하는 **음성 번역**이라는 것이다. 기존 방식은 '음성 → 텍스트 → 번역 → TTS' 순서의 파이프라인으로 각 단계마다 레이턴시가 누적됐지만, GPT-Realtime-Translate는 이 과정을 단일 스트리밍 흐름으로 처리한다.

The Tech Portal, MarkTechPost 등 AI 전문 미디어에 따르면, 이미 글로벌 콜센터 솔루션 업체들이 이 API에 관심을 보이고 있다고 한다. 상담원이 하나의 언어만 구사해도 다국어 고객을 실시간으로 응대할 수 있는 시나리오를 이번 API로 구현할 수 있기 때문이다. 의료, 법률, 금융처럼 정확한 소통이 중요한 전문 분야에서도 적용 가능성이 탐색되고 있다.

### GPT-Realtime-Whisper: 스트리밍 STT의 새 기준

GPT-Realtime-Whisper는 음성을 실시간으로 텍스트로 변환(STT)하는 모델이다. OpenAI의 오리지널 Whisper 모델이 배치 처리 방식으로 파일 단위 전사에 특화됐던 것과 달리, Realtime-Whisper는 스트리밍 방식으로 오디오가 들어오는 즉시 텍스트를 출력한다.

주요 특징:

- **저지연 스트리밍 전사**: 오디오 버퍼가 일정량 이상 쌓이기를 기다리지 않고, 발화 흐름에 맞춰 텍스트를 연속 출력
- **화자 구분(Speaker Diarization)**: 여러 화자가 참여하는 대화에서 발화자를 구분해 레이블 부여
- **소음 강인성(Noise Robustness)**: 콜센터, 공장, 야외처럼 배경 소음이 있는 환경에서도 안정적인 인식률 유지

실무 적용 시나리오로는 회의록 자동 생성, 의료 현장 음성 오더 전사, 법정 기록, 실시간 자막 생성 등이 논의되고 있다. Analytics Drift는 "GPT-Realtime-Whisper의 화자 구분 기능이 기존 Whisper + pyannote 파이프라인의 복잡성을 크게 줄여줄 것"이라고 평가했다.

### Realtime API GA 전환의 의미

이번 3종 모델 출시와 함께 Realtime API가 정식 GA로 전환됐다는 점은 단순한 레이블 변경 이상의 의미를 갖는다. 베타 기간 동안에는 API 레이트 리밋이 낮고, 서비스 안정성이 프로덕션 환경에서 요구되는 수준에 미치지 못한다는 지적이 있었다.

GA 전환으로:
- **SLA(Service Level Agreement)** 적용: 업타임 보장 및 장애 대응 체계 정식화
- **레이트 리밋 상향**: 더 높은 동시 연결 수와 처리량 지원
- **안정된 API 버전 보장**: 하위 호환성이 보장된 v1 엔드포인트로 통합

Realtime API는 기존과 동일하게 **WebSocket**(서버 사이드 통합에 적합)과 **WebRTC**(브라우저·모바일 앱에 적합)의 두 가지 연결 방식을 지원한다. OpenAI Developer Community 포럼에서는 GA 발표 직후 수백 개의 댓글이 달리며 "이제 진짜 프로덕션 투입이 가능해졌다"는 반응이 주를 이뤘다.

### 경쟁 구도와 업계 반응

이번 릴리스는 Google의 Gemini Live, ElevenLabs의 실시간 음성 변환 기술, Microsoft Azure Speech SDK와 직접 경쟁하는 구도다. 주요 비교 포인트를 정리하면:

| 서비스 | 실시간 번역 | 도구 호출 | 화자 구분 | GA 여부 |
|--------|------------|---------|---------|--------|
| GPT-Realtime-2/Translate/Whisper | ✓ (70개 입력) | ✓ | ✓ | ✓ |
| Google Gemini Live | ✓ (제한적) | ✓ | △ | ✓ |
| Azure Speech SDK | ✓ | ✗ (별도 구성) | ✓ | ✓ |
| ElevenLabs Realtime | ✗ | ✗ | ✗ | ✓ |

AI 개발자 커뮤니티에서는 GPT-Realtime-Translate의 출력 언어가 13개로 Google Translate의 100개 이상에 비해 아직 폭이 좁다는 지적도 있다. 반면 출력 음질과 레이턴시 면에서는 높은 평가를 받고 있으며, "언어 수보다 품질이 중요한 엔터프라이즈 시나리오에 적합하다"는 시각이 많다.

Latent Space, The Tech Portal 등 AI 테크 미디어에서는 "Realtime API GA 전환이 음성 AI 에이전트 개발의 진입 장벽을 크게 낮췄다"고 평가하며, 스타트업 생태계에서 음성 기반 AI 에이전트 제품 출시가 급증할 것이라는 전망을 내놓았다.

## 정리

- OpenAI가 2026년 5월 7~8일 **GPT-Realtime-2**, **GPT-Realtime-Translate**, **GPT-Realtime-Whisper** 세 가지 실시간 음성 모델을 동시 출시했다.
- GPT-Realtime-2는 GPT-5 수준의 추론 능력을 실시간 대화에 탑재하며, 대화 중 도구 호출과 다단계 에이전트 워크플로 실행이 가능하다.
- GPT-Realtime-Translate는 70개 이상 입력 언어, 13개 출력 언어를 지원하는 실시간 음성 번역 모델로, 콜센터·다국어 환경에서 즉각적인 활용이 기대된다.
- GPT-Realtime-Whisper는 스트리밍 STT와 화자 구분 기능을 갖춰 회의록·법정 기록 등 전문 전사 분야에 적합하다.
- Realtime API가 베타를 벗어나 **GA로 전환**되면서 SLA 보장과 높은 레이트 리밋이 적용돼 프로덕션 환경 투입이 본격화될 전망이다.
- 음성 AI 에이전트 개발을 검토하는 팀이라면, 세 모델의 역할을 명확히 구분해 아키텍처에 반영하는 것이 중요하다. 번역이 필요 없는 단순 대화에는 GPT-Realtime-2, 다국어 환경에는 Translate, 전사 전용이라면 Whisper를 선택하는 방식이다.

## Reference

- [OpenAI launches new voice intelligence features in its API — TechCrunch (2026.05.07)](https://techcrunch.com/2026/05/07/openai-launches-new-voice-intelligence-features-in-its-api/)
- [OpenAI Releases Three Realtime Audio Models — MarkTechPost (2026.05.08)](https://www.marktechpost.com/2026/05/08/openai-releases-three-realtime-audio-models-gpt-realtime-2-gpt-realtime-translate-and-gpt-realtime-whisper-in-the-realtime-api/)
- [OpenAI launches three new GPT-Realtime audio models — The Tech Portal (2026.05.08)](https://thetechportal.com/2026/05/08/openai-launches-three-new-gpt-realtime-audio-models-for-speech-translation-and-transcription/)
- [OpenAI has new voice models that reason, translate, and transcribe — 9to5Mac (2026.05.07)](https://9to5mac.com/2026/05/07/openai-has-new-voice-models-that-reason-translate-and-transcribe-as-you-speak/)
- [GPT-Realtime-2 Brings GPT-5 Reasoning to Voice Agents — Analytics Drift](https://analyticsdrift.com/openai-gpt-realtime-2-voice-api/)
- [New Realtime Voice Models in the API — OpenAI Developer Community](https://community.openai.com/t/new-realtime-voice-models-in-the-api/1380471)
- [OpenAI debuts voice tools GPT-Realtime-2/Translate/Whisper — NewsBytesApp (2026.05.08)](https://www.newsbytesapp.com/news/science/openai-debuts-voice-tools-gpt-realtime-2-gpt-realtime-translate-gpt-realtime-whisper-for-its-api/tldr)
