---
title: "[AI] Microsoft Build 2026: Project Polaris로 GitHub Copilot이 OpenAI를 벗어나다"
date: 2026-06-02 07:10:11 +09:00
categories: [AI]
tag: [Microsoft, GitHub Copilot, Project Polaris, AI Agent, MAI]
---

## 서론

2026년 6월 2일, 샌프란시스코 Fort Mason Center에서 Microsoft Build 2026 개발자 컨퍼런스가 개막했다. CEO Satya Nadella의 기조연설부터 업계 이목이 집중됐는데, 그 이유는 단순히 새로운 기능 발표 때문이 아니었다. 이번 Build에서 마이크로소프트는 사실상 "AI 자주 선언"을 한 셈이다.

핵심은 **Project Polaris** — 마이크로소프트가 자체 개발한 AI 코딩 모델이다. 이 모델은 2026년 8월부터 GitHub Copilot의 기본 추론 엔진으로 GPT-4 Turbo를 대체할 예정이다. 수년간 GitHub Copilot의 두뇌 역할을 해온 OpenAI 모델이 마이크로소프트 자체 모델로 교체된다는 것은, AI 업계의 공급망 구도가 변화하는 신호탄으로 읽힌다.

단순한 모델 교체를 넘어, 마이크로소프트는 이번 Build에서 Windows 자체를 AI 에이전트의 네이티브 런타임으로 선언하면서 개발자 플랫폼 전략 전반을 대폭 재편했다. AI가 프롬프트에 응답하는 시대에서 자율적으로 워크플로우 전체를 실행하는 에이전트 시대로 전환됐다는 메시지가 이번 Build의 전체 관통 주제였다.

## 본론

### OpenAI 의존에서 자체 모델로: 배경과 맥락

GitHub Copilot은 2021년 출시 이래 줄곧 OpenAI의 Codex, 그리고 이후 GPT-4 계열 모델에 전적으로 의존해왔다. 마이크로소프트가 OpenAI에 수십억 달러를 투자한 파트너십 구조 덕분에 가능한 일이었지만, 동시에 핵심 제품의 두뇌를 외부 기업에 맡겨두는 전략적 리스크를 내포하고 있었다.

2026년 4월, 양사는 파트너십 조건을 재협상했다. 이 협상의 핵심 중 하나는 마이크로소프트 내부 AI 연구 조직인 **MAI(Microsoft AI)** 팀의 권한 확대였다. Mustafa Suleyman이 이끄는 MAI팀은 기존 파트너십 조건상 최고 수준의 파운데이션 모델을 독자적으로 훈련하는 데 제약이 있었다. 재협상 이후 이 제약이 완화되면서 본격적인 자체 모델 개발이 가속화됐다.

이번 Build 2026은 그 결과물을 대외적으로 공개한 자리였다.

### Project Polaris: Copilot의 새 두뇌

Project Polaris는 마이크로소프트 MAI팀이 개발한 코딩 특화 AI 모델이다. 코드 생성, 버그 수정, 테스트 작성, 리팩터링에 최적화된 추론 엔진으로 설계됐으며, 2026년 8월부터 GitHub Copilot의 기본 모델로 GPT-4 Turbo를 대체할 예정이다.

Copilot CLI는 이미 2026년 3월에 정식 출시(GA)됐으며, 터미널 워크플로우에서 에이전트 기능을 직접 사용할 수 있게 됐다. Build 2026에서 발표된 실제 배포 데이터에 따르면, GitHub Copilot 에이전트는 현재 버그 수정, 테스트 작성, PR 생성을 자율적으로 수행하는 수준까지 성숙했다. 한때 코드 완성 보조 도구에 불과했던 Copilot이 반독립적인 개발 에이전트로 변모한 셈이다.

Copilot Workspace도 이번 Build에서 베타를 졸업해 정식 서비스로 전환됐다. Copilot Workspace는 이슈를 받아 구현 계획을 세우고, 코드를 작성하고, 테스트를 실행하며, PR을 생성하는 전 과정을 에이전트가 처리하는 환경이다.

### MAI 모델 라인업: Polaris 외에도

Project Polaris 외에도 MAI팀은 여러 자체 모델을 상업 개발자용으로 처음 개방했다:

- **MAI-Image-2.5**: 이미지 이해 및 생성에 특화된 멀티모달 모델. 시각 정보를 처리하는 에이전트 기반 애플리케이션에 활용 가능하다.
- **MAI-Voice-2**: 다국어 음성 처리 모델. 여러 언어를 동시에 처리할 수 있는 실시간 음성 AI 애플리케이션 개발에 쓰인다.
- **MAI-Transcribe-1.5**: 음성-텍스트 변환(STT) 특화 모델. 정확도와 속도 측면에서 이전 세대 대비 개선됐다는 것이 마이크로소프트의 설명이다.

이 모델들은 Azure AI Foundry(구 Azure AI Studio)를 통해 제공되며, OpenAI GPT, Anthropic Claude, Meta Llama, Mistral 등 주요 서드파티 모델과 함께 단일 플랫폼에서 접근할 수 있다. 모든 접근은 Entra ID + Purview 거버넌스 체계 안에서 이루어진다.

### Windows Agent Platform: OS가 에이전트 런타임이 되다

Build 2026에서 마이크로소프트가 발표한 또 다른 대형 테마는 Windows 자체를 AI 에이전트 플랫폼으로 전환하겠다는 선언이다.

**Windows Agent Runtime**은 OS 셸에 에이전트 네이티브 API를 직접 내장한 컴포넌트다. 에이전트가 Windows의 파일 시스템, 앱, UI 자동화, 하드웨어에 접근하기 위해 별도의 서드파티 프레임워크 없이도 표준 API를 통해 상호작용할 수 있다.

**Windows Agent Store**는 에이전트 앱을 유통하는 새로운 스토어 채널이다. 개발자에게 수익의 85%를 배분한다고 발표됐는데, 이는 기존 앱 스토어들의 통상적인 배분율보다 높은 수준이어서 개발자 커뮤니티의 관심을 끌었다.

엔터프라이즈 측면에서는 **Microsoft 365 E7 + Agent 365**가 GA에 도달했다. 이 구성은 E5, Copilot, Entra Suite, Agent 365를 하나의 SKU로 묶은 것으로, Agent 365는 조직 내 AI 에이전트를 거버넌스하는 새로운 제어 플레인 역할을 한다.

### 전략적 의미: AI 업계의 공급망 재편

개발자 커뮤니티에서 이번 Build 2026을 두고 가장 많이 거론하는 키워드는 "탈OpenAI"다. 물론 마이크로소프트와 OpenAI의 파트너십이 완전히 종료된 것은 아니다. Microsoft Foundry에서는 여전히 GPT 모델을 포함한 OpenAI 제품에 접근할 수 있다.

그러나 GitHub Copilot처럼 마이크로소프트의 핵심 개발자 제품에 자체 모델이 탑재된다는 사실은, 공급망 다변화 측면에서 중요한 변곡점이다. 특히 Copilot은 마이크로소프트가 수억 명의 개발자를 대상으로 하는 주력 AI 제품이기 때문에, 여기서 OpenAI 모델을 대체한다는 결정은 단순한 기술적 선택 이상의 의미를 갖는다.

한편 Anthropic의 Claude 역시 Microsoft Foundry를 통해 제공되고 있어, 마이크로소프트가 특정 벤더에 대한 의존을 줄이면서 멀티 모델 생태계를 지향하고 있음을 알 수 있다.

### Foundry Local GA: 클라우드 없는 AI 추론

이번 Build에서 주목받은 또 하나의 발표는 **Foundry Local** 정식 출시다. Foundry Local은 클라우드 연결 없이 로컬 디바이스에서 완전한 AI 추론과 에이전트 실행을 가능하게 하는 플랫폼이다. Windows, macOS(Apple Silicon), Linux x64를 지원하며, OpenAI의 chat completions 및 audio transcription과 호환되는 요청/응답 형식을 채택해 기존 클라우드 기반 코드와의 호환성을 유지한다.

per-token 과금이 없다는 점과 네트워크 레이턴시가 없다는 점이 개발자 커뮤니티에서 긍정적으로 평가받고 있다. 민감 데이터를 외부 클라우드로 전송하지 않아도 된다는 보안 측면의 이점도 부각되고 있다.

## 정리

Microsoft Build 2026은 마이크로소프트가 AI 전략의 자주성을 공식 선언한 이정표적인 이벤트였다. Project Polaris가 GitHub Copilot의 기본 모델로 채택되는 2026년 8월은 GitHub 사용자 수억 명이 처음으로 마이크로소프트 자체 AI 모델을 일상적으로 사용하게 되는 시점이다.

업계 반응은 복잡하게 갈린다. 개발자 커뮤니티에서는 특히 Copilot의 성능 변화에 촉각을 세우고 있다. ChatForest의 Build 2026 리캡 분석은 "Polaris의 등장은 마이크로소프트가 AI 스택 전체를 통제하려는 의지의 표현"이라고 평가했고, Windows News는 "AI 에이전트 플랫폼 경쟁에서 마이크로소프트가 AWS, Google과 완전한 정면 대결 구도로 나섰다"고 분석했다.

OpenAI 입장에서도 이번 발표는 단순히 파트너사의 기술 발표로 볼 수 없다. GitHub Copilot은 OpenAI 모델이 가장 광범위하게 배포된 대형 채널 중 하나였기 때문에, 이 채널에서 자체 모델로 교체된다는 사실은 OpenAI의 수익 구조에도 일정한 영향을 미칠 수 있다.

한편 Windows Agent Platform 전략은 아직 현실화까지 시간이 필요하다는 시각도 있다. 에이전트 생태계가 플랫폼 단에서 안정적으로 작동하려면 보안, 프라이버시, 에이전트 간 신뢰 관계 설정 등 해결해야 할 과제가 적지 않다. 하지만 이번 Build가 마이크로소프트의 AI 전략 방향성을 명확히 보여준 것만은 분명하다.

## Reference

- [Microsoft Build 2026 Recap: Windows Is Now an Agent Platform, and Project Polaris Cuts the OpenAI Cord — ChatForest](https://chatforest.com/builders-log/microsoft-build-2026-recap-windows-agent-platform-project-polaris-copilot-workspace/)
- [Microsoft Build 2026: Homegrown AI Models to Power GitHub Copilot — Windows Forum](https://windowsforum.com/threads/microsoft-build-2026-homegrown-ai-models-to-power-github-copilot.420887/)
- [Microsoft Build 2026: AI Agents, Copilot, Azure AI Foundry, and Windows Local AI — Windows News](https://windowsnews.ai/article/microsoft-build-2026-ai-agents-copilot-azure-ai-foundry-and-windows-local-ai.420861)
- [Microsoft Build 2026: What to expect from the June 2 keynote — Notebookcheck](https://www.notebookcheck.net/Microsoft-Build-2026-What-to-expect-from-the-June-2-keynote.1311546.0.html)
- [Microsoft readies new MAI voice and image models for Build 2026 — TestingCatalog](https://www.testingcatalog.com/microsoft-readies-new-mai-voice-and-image-models-for-build-2026/)
- [Microsoft Ships Production-Ready Agent Framework 1.0 for .NET and Python — Visual Studio Magazine](https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx)
- [Microsoft set to unveil new coding model at Build — Let's Data Science](https://letsdatascience.com/news/microsoft-set-to-unveil-new-coding-model-at-build-f8155f19)
- [AI News Today — May 31, 2026: 11 Biggest Stories — Build Fast With AI](https://www.buildfastwithai.com/blogs/ai-news-today-may-31-2026)
