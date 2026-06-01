---
title: "[BE] Microsoft Build 2026: Windows Agent Framework v1.0 오픈소스 공개와 WSL 3 아키텍처"
date: 2026-06-02 07:10:11 +09:00
categories: [BE]
tag: [Microsoft, WSL, Agent Framework, Backend, Azure]
---

## 서론

Microsoft Build 2026이 오늘(6월 2일) 개최됐다. AI 모델 발표나 전략적 선언만큼 화려하지는 않지만, 백엔드와 풀스택 개발자 입장에서 실질적으로 중요한 발표들이 묻혀서는 안 된다. 이번 Build에서 마이크로소프트가 개발자 도구 측면에서 공개한 핵심은 크게 두 가지다.

첫 번째는 **Windows Agent Framework(WAF) v1.0**을 MIT 라이선스로 오픈소스 공개한 것이다. 2026년 4월에 v1.0이 출시됐지만, Build 2026에서 MIT 라이선스가 공식 확인되면서 오픈소스 생태계로의 문이 열렸다. Python과 .NET 개발자 모두를 대상으로 하는 이 프레임워크는, 에이전트를 로컬에서 Azure 클라우드까지 단일 선언 파일로 관리할 수 있게 해준다.

두 번째는 **WSL 3(Windows Subsystem for Linux 3)**의 본격적인 아키텍처 개편이다. 리눅스 커널을 경량 VM으로 이동하고 GPU/NPU에 반가상화(paravirtualized) 접근 방식을 채택한 WSL 3는, Windows를 ML 및 AI 워크로드의 진지한 개발 플랫폼으로 전환하는 데 핵심 역할을 한다. PyTorch, JAX, CUDA 기반 스택을 Windows에서 near-native 속도로 실행할 수 있게 됐다는 것은, 듀얼 부팅이나 별도 리눅스 머신에 의존하던 백엔드/ML 개발자들에게 실질적인 변화를 의미한다.

## 본론

### Windows Agent Framework v1.0: 에이전트를 위한 YAML 선언형 프레임워크

Windows Agent Framework는 AI 에이전트를 빌드, 오케스트레이션, 배포하기 위한 마이크로소프트의 오픈소스 프레임워크다. Python과 .NET을 1등 시민으로 지원하며, GitHub 레포지터리(`microsoft/agent-framework`)를 통해 접근할 수 있다.

WAF의 핵심 설계 철학은 **"에이전트를 YAML로 정의하고, 런타임에 독립적이게 만든다"**는 것이다. 에이전트는 `agent.json`이라는 선언적 매니페스트 파일로 정의된다. 이 파일에 에이전트의 캐퍼빌리티(capabilities), 필요한 API 계약, 데이터 처리 방식을 명시해두면, 동일한 에이전트가 다음 세 환경에서 별도의 코드 수정 없이 실행될 수 있다:

1. 개발자 로컬 PC (Windows 프로세스)
2. Windows 365 GPU 클라우드 PC (GPU 집약적 태스크 시 자동 에스컬레이션)
3. Azure 서비스 (퍼블릭 서비스로 배포)

인프라 관점에서 WAF는 네 가지 핵심 컴포넌트로 구성된다:

**1. Agent Registration Service**
에이전트의 생명주기를 관리하는 로컬 데몬이다. 에이전트를 활성 상태로 유지하고, 헬스 모니터링, 버전 관리를 담당한다. 백엔드 서비스의 `systemd` 유닛과 유사한 역할을 에이전트에 적용한 것으로 이해하면 된다.

**2. Declarative Agent Manifest (agent.json)**
에이전트가 무엇을 할 수 있는지, 어떤 API를 사용하는지, 데이터 계약은 어떻게 되는지를 스키마 파일 형태로 명시한다. 이 매니페스트는 런타임 독립성을 보장하는 핵심이다. 하나의 `agent.json`이 로컬, 클라우드, 엣지 환경 모두에서 동일하게 동작하도록 설계됐다.

**3. Cross-Agent Communication Bus**
gRPC 기반의 pub/sub 시스템으로, 에이전트 간 통신을 처리한다. 에이전트끼리 하드 의존성 없이 시그널을 주고받을 수 있다. MSA(마이크로서비스 아키텍처)에서 서비스 간 이벤트 버스의 에이전트 버전이라고 볼 수 있다. gRPC를 기반으로 해서 타입 안전성과 성능이 보장된다.

**4. Memory Service**
AI-네이티브 영속 캐시다. 대화 컨텍스트, 사용자 선호도, 에이전트가 학습한 패턴을 저장하며, 모든 데이터는 암호화되고 사용자가 제어할 수 있다. 세션이 끊겨도 에이전트가 이전 컨텍스트를 기억하는 것을 가능하게 해주는 레이어다.

InfoQ의 리포트에 따르면, WAF RC(릴리스 캔디데이트) 단계부터 개발자 커뮤니티에서 "에이전트 개발의 보일러플레이트를 크게 줄인다"는 평가가 있었다. 특히 Python 생태계에서 기존의 LangChain, AutoGen 등 에이전트 프레임워크와 비교했을 때, Windows 환경과의 통합 측면에서 WAF가 강점을 보인다는 분석이 나왔다.

### Azure Agent Mesh: 클라우드 에이전트 오케스트레이션

Build 2026에서 새롭게 발표된 **Azure Agent Mesh**는 WAF 에이전트를 클라우드 스케일에서 오케스트레이션하기 위한 컨트롤 플레인이다.

WAF가 에이전트를 정의하고 실행하는 프레임워크라면, Azure Agent Mesh는 수십~수백 개의 에이전트를 클라우드에서 관리, 모니터링, 스케일링하는 인프라 레이어다. 백엔드 서비스 관점으로 비유하면, WAF가 Spring Boot나 FastAPI에 해당하고, Azure Agent Mesh는 Kubernetes + Service Mesh(Istio 등)에 해당하는 역할이다.

현재 공개된 정보에서는 Azure Agent Mesh의 구체적인 프라이싱이나 SLA는 확인되지 않는다. 하지만 Build 기조연설에서 Satya Nadella가 직접 언급할 만큼 마이크로소프트의 에이전트 인프라 전략에서 핵심 위치를 차지하고 있음은 분명하다.

### WSL 3: 완전한 재아키텍처

WSL 3는 단순한 버전 업그레이드가 아니다. WSL 2가 Hyper-V 기반의 완전 가상화 VM 위에서 리눅스 커널을 실행했다면, WSL 3는 **경량 VM(lightweight VM) + 반가상화(paravirtualization)** 접근 방식으로 전환했다.

핵심 변화는 GPU와 NPU에 대한 반가상화 접근이다. WSL 2에서 GPU 접근은 `DirectML`과 `CUDA WSL-Ubuntu` 드라이버를 통해 가능했지만, 실제 ML 워크플로우에서 성능 페널티가 존재했다. WSL 3는 이 구조를 바꿔 GPU/NPU 작업에서 near-native 속도를 목표로 한다.

**DirectML 2.0 + WSL 3** 조합은 특히 AI/ML 백엔드 개발자에게 중요하다:

```bash
# WSL 3에서 PyTorch GPU 사용 예시 (CUDA 호환)
import torch

# WSL 3에서 near-native 속도로 실행
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

PyTorch, JAX, CUDA 기반 스택이 WSL 3 환경에서 near-native 속도로 실행된다는 것은, Windows PC를 주 개발 환경으로 사용하면서 ML 워크로드를 위해 별도의 리눅스 머신이나 듀얼 부팅에 의존하던 개발자들의 워크플로우를 단순화할 수 있다.

**NPU passthrough** 기능도 새로 추가됐다. 현재 지원 하드웨어는:
- Qualcomm Snapdragon X Elite
- Intel Meteor Lake / Lunar Lake

AMD 지원은 향후 업데이트에서 추가될 예정이라고 마이크로소프트가 밝혔다. AMD 사용자 커뮤니티에서는 이 부분에 대한 불만의 목소리가 있었으나, 마이크로소프트는 하드웨어 파트너와의 협업을 통해 드라이버 지원을 확대해나가겠다고 약속했다.

기타 WSL 3의 개선 사항:
- **GUI 앱 ARM64 지원** 개선: 기존 x86-64 에뮬레이션 의존도 감소
- **파일 시스템 접근 성능 향상**: Windows-Linux 파일 시스템 경계 간 I/O 오버헤드 감소
- **네트워킹 개선**: 로컬 개발 환경에서 Docker, Kubernetes 등 컨테이너 툴과의 통합이 더 원활해짐
- **WSL 설치 단순화**: Microsoft Store를 통한 설치 과정 간소화

### Foundry Local GA: 로컬 AI 추론 플랫폼

Build 2026에서 **Foundry Local**이 정식 출시(GA)됐다. Foundry Local은 클라우드 연결 없이 로컬 디바이스에서 AI 모델 추론과 에이전트 실행을 가능하게 하는 플랫폼이다.

지원 플랫폼:
- Windows (x64, ARM)
- macOS (Apple Silicon)
- Linux (x64)

개발자 관점에서 Foundry Local의 가장 큰 장점은 **OpenAI 요청/응답 형식과의 호환성**이다. chat completions, audio transcription API가 동일한 인터페이스를 사용하기 때문에, 클라우드와 로컬 사이를 별도의 코드 수정 없이 전환할 수 있다.

```python
# Foundry Local 예시 — OpenAI 호환 인터페이스
from openai import OpenAI

# 클라우드 → 로컬 전환 시 base_url만 변경
client = OpenAI(
    base_url="http://localhost:5272/v1",  # Foundry Local 엔드포인트
    api_key="foundry-local"
)

response = client.chat.completions.create(
    model="phi-3.5-mini",
    messages=[{"role": "user", "content": "안녕하세요"}]
)
```

per-token 과금이 없고 네트워크 레이턴시가 없다는 점은 개발/테스트 워크플로우에서 특히 유용하다. 민감한 데이터를 외부 클라우드로 전송하지 않아도 된다는 점은 컴플라이언스가 중요한 엔터프라이즈 환경에서 의미 있는 이점이다.

### Windows Agent Store: 새로운 에이전트 유통 채널

Build 2026에서 발표된 **Windows Agent Store**는 WAF로 만든 에이전트 애플리케이션을 유통하는 새로운 채널이다. 개발자에게 수익의 85%를 배분한다고 발표됐는데, 이는 기존 앱 스토어들의 일반적인 배분율과 비교해 높은 수준이어서 개발자 커뮤니티에서 주목받고 있다.

현재 구체적인 출시 일정은 공개되지 않았지만, 에이전트 생태계를 빠르게 확장하려는 마이크로소프트의 의도가 반영된 것으로 해석된다.

## 정리

Microsoft Build 2026에서 발표된 개발자 도구들은 공통된 방향성을 가리킨다: Windows를 AI 에이전트 개발과 실행을 위한 진지한 플랫폼으로 만들겠다는 것이다.

Windows Agent Framework v1.0의 MIT 오픈소스 공개는 에이전트 프레임워크 생태계에 마이크로소프트가 본격적으로 뛰어들었다는 신호다. InfoQ는 "WAF가 .NET과 Python 개발자에게 에이전트 개발의 진입 장벽을 낮춘다"고 평가했고, Visual Studio Magazine은 "마이크로소프트가 에이전트 인프라의 표준화를 시도하고 있다"고 분석했다.

WSL 3에 대해서는 반응이 엇갈린다. ML/AI 워크로드를 Windows에서 처리하고 싶은 개발자들에게는 반가운 소식이지만, AMD GPU 지원이 빠진 것에 대한 불만도 커뮤니티에서 공유됐다. 마이크로소프트는 커뮤니티 유지 WSL AI 드라이버 GitHub 레포지터리를 별도로 오픈해 하드웨어 파트너와의 협업을 확대하겠다는 입장을 밝혔다.

백엔드 개발자 커뮤니티 전반의 반응은 "지켜봐야 한다"는 기조다. WAF가 LangChain, AutoGen, CrewAI 등 기존 에이전트 프레임워크 대비 실제 개발 경험에서 어떤 차별점을 보여주는지, WSL 3가 체감할 수 있는 성능 개선을 실제로 제공하는지는 곧 커뮤니티에서 검증 결과가 나올 것으로 보인다.

지금 당장 백엔드 개발자라면 챙겨봐야 할 것은 세 가지다: WAF의 GitHub 레포 (`microsoft/agent-framework`) 스타하기, WSL 3 업데이트 일정 추적, 그리고 Foundry Local로 로컬 AI 추론 환경을 빠르게 테스트해보는 것.

## Reference

- [Microsoft Build 2026: Windows Agent Framework, WSL 3, Azure Agent Mesh, and Windows Agent Store Explained — AI Tools Recap](https://aitoolsrecap.com/Blog/microsoft-build-2026-windows-agent-framework-wsl3-azure-mesh)
- [Microsoft Build 2026: Windows becomes the platform for AI agents — Windows News](https://windowsnews.ai/article/microsoft-build-2026-windows-becomes-the-platform-for-ai-developers.420496)
- [GitHub — microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- [Microsoft Ships Production-Ready Agent Framework 1.0 for .NET and Python — Visual Studio Magazine](https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx)
- [Microsoft Agent Framework RC Simplifies Agentic Development in .NET and Python — InfoQ](https://www.infoq.com/news/2026/02/ms-agent-framework-rc/)
- [Microsoft Agent Framework Version 1.0 — Microsoft DevBlogs](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
- [Foundry Local is now Generally Available — Microsoft Foundry Blog](https://devblogs.microsoft.com/foundry/foundry-local-ga/)
- [Microsoft to upgrade Windows Subsystem for Linux with faster file access, better networking — Windows Latest](https://www.windowslatest.com/2026/03/31/microsoft-to-upgrade-windows-subsystem-for-linux-wsl-with-faster-file-access-better-networking-and-easier-setup/)
- [Microsoft Build 2026 Recap: Windows Is Now an Agent Platform — ChatForest](https://chatforest.com/builders-log/microsoft-build-2026-recap-windows-agent-platform-project-polaris-copilot-workspace/)
