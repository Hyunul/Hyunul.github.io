---
title: "[AI] Anthropic 'When AI Builds Itself': Claude가 코드 80%를 쓰는 시대와 전 세계 멈춤 버튼 논쟁"
date: 2026-06-08 07:09:36 +09:00
categories: [AI]
tag: [Anthropic, Claude, 재귀적자기개선, AI안전성, IPO, ClaudeCode]
---

## 서론

2026년 6월 5일, Anthropic이 조용하지만 업계를 흔드는 보고서 하나를 공개했다. 제목은 **"When AI Builds Itself"** — AI가 스스로를 만든다. 처음 들으면 SF처럼 들리지만, 보고서의 내용은 완전히 현실 이야기다.

보고서의 핵심 주장은 이렇다. 2026년 5월 기준, Anthropic의 프로덕션 코드베이스에 머지된 코드 중 **80% 이상을 Claude가 작성했다**. 불과 2025년 초 Claude Code가 출시됐을 당시만 해도 이 비율은 한 자릿수였다. 불과 1년여 만에 80%를 넘어선 것이다. 게다가 The Decoder의 보도에 따르면 이 수치는 이미 90%를 넘겼다는 최근 업데이트도 있다.

이 숫자가 의미하는 바는 단순히 "AI가 코드를 잘 쓴다"를 넘어선다. Anthropic은 이걸 **재귀적 자기개선(Recursive Self-Improvement)**의 초기 단계로 해석하고 있다. AI가 AI를 개선하는 코드를 쓰면, 그 AI가 더 나은 코드를 쓰고, 그게 또 AI를 개선한다. 이 사이클이 임계점을 넘으면 인간이 개입하기 어려운 속도로 AI가 발전할 수 있다는 것이다.

Anthropic은 이 보고서에서 한 발 더 나아가, **전 세계 프론티어 AI 개발을 일시적으로 멈출 수 있는 옵션이 필요하다**는 주장을 펼쳤다. 이 주장을 꺼낸 타이밍이 절묘하다 — 정확히 **IPO를 위한 S-1 제출 1주 후**다.

## 본론

### "When AI Builds Itself" 보고서 핵심 수치

보고서에서 공개된 데이터들은 꽤나 인상적이다.

**코드 작성 비율 변화**

| 시점 | Claude 작성 코드 비율 |
|---|---|
| 2025년 초 (Claude Code 출시 직후) | 한 자릿수 % |
| 2026년 5월 | 80%+ |

Anthropic 엔지니어들의 생산성 지표도 함께 공개됐다.

- **엔지니어 1인당 분기 코드 머지량**: 2024년 대비 **8배 증가**
- 이건 인원이 줄거나 근무시간이 늘어서가 아니라, Claude Code와의 협업으로 각 엔지니어가 이전보다 훨씬 많은 작업을 처리하게 됐다는 의미다.

더 흥미로운 건 **코드 최적화 성능**의 변화다.

| 시점 | 코드 최적화 성능 배수 |
|---|---|
| 2025년 5월 (Claude Opus 4) | 약 3배 |
| 2026년 4월 (Mythos Preview) | **약 52배** |

1년 만에 17배가 넘는 성능 향상이 일어난 것이다. Anthropic은 이 수치를 통해, AI 시스템이 단순한 "코딩 보조 도구"를 넘어 AI 자신의 발전 속도를 가속시키는 단계에 접어들고 있다는 점을 강조한다.

### 재귀적 자기개선이란 무엇인가

Anthropic은 보고서에서 "재귀적 자기개선(Recursive Self-Improvement, RSI)"을 다음과 같이 설명한다.

> "AI 시스템이 자신의 후속 버전을 설계·개발하는 과정을 완전히 자율적으로 수행할 수 있게 되는 것"

현재 Anthropic의 상황을 RSI의 초기 단계로 볼 수 있다. Claude가 Anthropic의 코드를 대부분 작성하고 있고, 그 코드에는 Claude 자신을 훈련하고 개선하는 코드도 포함될 수 있다. 완전한 RSI는 아직 아니지만, 그 방향으로 향하는 중이라는 것이 Anthropic의 자체 진단이다.

보고서를 쓴 연구자들은 이렇게 덧붙인다: "RSI는 불가피한 것이 아니다. 하지만 대부분의 기관이 준비하는 것보다 훨씬 빨리 올 수 있다."

```text
현재 단계 (2026):
  인간 엔지니어 → (Claude Code 사용) → AI 코드 작성 → AI 시스템 개선

잠재적 미래 단계 (RSI):
  AI 시스템 → (자율적으로) → AI 후속 버전 설계·개발 → 더 강력한 AI → 반복
```

### AI 개발 일시정지 제안: 내용과 조건

보고서의 두 번째 파트는 **AI 안전성 거버넌스**에 관한 제안이다.

Anthropic의 입장은 이렇다: "세계가 프론티어 AI 개발 속도를 늦추거나 일시적으로 멈출 수 있는 **옵션**을 갖추는 것이 좋다."

그런데 이 제안에는 중요한 단서가 붙어 있다. "혼자 멈추는 건 의미 없다." Anthropic은 이 정지 또는 감속이 의미를 가지려면 다음 조건이 필요하다고 밝혔다.

1. **미국과 중국을 포함한 여러 프론티어 AI 국가가 함께** 참여해야 한다.
2. 외부에서 **검증 가능한 규칙** 아래에서 이뤄져야 한다.
3. 일부 국가만 멈추고 나머지가 계속 달리는 구조는 오히려 위험하다.

Anthropic은 자사가 일방적으로 개발을 멈추겠다고 선언하지 않았다. 그건 전략적으로 불가능하다는 것을 본인들도 알고 있다. 대신 이런 다자간 거버넌스 메커니즘이 필요하다는 주장을 공개적으로 제기한 것이다.

### IPO 타이밍과 업계의 시선

이 보고서가 나온 타이밍을 짚지 않을 수 없다. Anthropic은 2026년 6월 1일, SEC에 **비공개 S-1 제출**을 완료하며 공개 상장 절차를 공식 시작했다. 최신 Series H 라운드에서 확정된 밸류에이션은 약 **9,650억 달러(약 965 billion USD)**. 연간 매출 런레이트는 약 **470억 달러**로 알려졌다.

"When AI Builds Itself"가 공개된 건 그로부터 딱 4일 뒤인 6월 5일이다.

이 타이밍을 두고 업계의 반응은 엇갈렸다.

**긍정적 시각**: AI 안전성 우려를 공개적으로 제기하는 회사라는 이미지 강화. 규제 환경에서 신뢰받는 플레이어로 포지셔닝. 기관투자자들에게 "책임감 있는 AI 기업"이라는 메시지 전달.

**회의적 시각**: WION News는 "멈춤 버튼에 전선이 없다(pause button has no cords)"는 표현으로 비판적 시각을 드러냈다. 공개 상장을 앞두고 수백억 달러의 투자를 받으면서 "개발을 멈춰야 할 수도 있다"고 말하는 것은 표리부동하다는 지적이다. 실제로 Anthropic은 보고서 발표 이후에도 채용을 계속하고 있고, 모델 개발도 가속하고 있다.

Scientific American은 이 보고서를 진지하게 다루면서 "Anthropic이 경고를 발신했다는 사실 자체는 의미가 있다"고 평가했다. 반면 일부 테크 미디어는 "AI 회사들이 규제에 대비한 'AI 안전성 세탁'을 시작했다"는 분석을 내놓기도 했다.

### 백엔드·소프트웨어 엔지니어 입장에서 읽는 이 보고서

이 숫자들이 현장 개발자들에게 어떤 의미인지를 생각해볼 필요가 있다.

Anthropic 같은 최전선 AI 기업에서 엔지니어 1인당 코드 처리량이 8배 증가했다는 건, AI 코딩 도구가 생산성에 주는 영향이 단순한 자동완성 수준을 넘어섰다는 실증 데이터다. 이미 Claude Code, GitHub Copilot, Cursor 같은 도구를 쓰는 개발자들은 이 변화를 체감하고 있다.

하지만 이 보고서가 던지는 더 깊은 질문은 이것이다: 코드를 쓰는 속도가 8배 빨라지면, 코드를 **검토하고 이해하고 유지보수하는** 사람의 역량도 그만큼 증가하는가? 코드 생성 속도와 코드 품질 관리 역량 사이의 간극이 벌어지는 게 더 큰 위험일 수 있다. 보안 취약점, 기술 부채, 시스템 복잡도는 생성 속도에 비례해서 증가한다.

The Next Web은 이 점을 지적하며 "AI가 코드를 더 빨리 쓸수록, 나쁜 코드도 더 빨리 프로덕션에 들어간다"는 우려를 전했다. 엔지니어링 팀의 역할이 "코드 작성자"에서 "AI 생성 코드의 감독자·검증자"로 빠르게 전환되고 있는 셈이다.

## 정리

- Anthropic의 "When AI Builds Itself" 보고서(2026년 6월 5일): Claude가 Anthropic 코드의 **80% 이상**을 작성 중
- 엔지니어 1인당 코드 처리량 **8배** 증가, 코드 최적화 성능은 3배 → 52배로 성장
- **재귀적 자기개선(RSI)** 가능성에 대한 경고: 아직은 아니지만, 대부분의 예상보다 빨리 올 수 있다
- **다자간 AI 개발 일시정지 옵션** 필요성 제기: 미국·중국 등 프론티어 국가가 함께, 검증 가능한 규칙 하에서
- IPO S-1 제출 4일 후 보고서 공개 → 업계의 엇갈린 반응
- 현장 개발자에게: 생성 속도가 8배 올라간다면, 품질 검증 역량도 그에 맞게 준비해야 한다

업계 반응을 한 줄로 요약하면: "Anthropic이 경고를 보낸 건 의미 있다. 그런데 그 경고를 보내는 회사가 동시에 IPO를 준비하고 있다는 사실도 잊지 마라."

## Reference

- [When AI builds itself - Anthropic Institute](https://www.anthropic.com/institute/recursive-self-improvement)
- [Anthropic warns Claude AI is building itself faster than expected, calls for option to halt frontier development - Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/anthropic-says-claude-now-writes-more-than-80-percent-of-its-merged-code)
- [Claude writes 80% of its code, calls for AI pause - The Next Web](https://thenextweb.com/news/anthropic-claude-recursive-self-improvement-code)
- [Anthropic warns AI may soon begin recursive self-improvement - Scientific American](https://www.scientificamerican.com/article/anthropic-warns-ai-may-soon-begin-recursive-self-improvement/)
- [Anthropic says Claude now writes over 90% of its code and wants the world to have an AI pause button - The Decoder](https://the-decoder.com/anthropic-says-claude-now-writes-over-90-of-its-code-and-wants-the-world-to-have-an-ai-pause-button/)
- [Anthropic files to go public - TechCrunch](https://techcrunch.com/2026/06/01/anthropic-files-to-go-public/)
