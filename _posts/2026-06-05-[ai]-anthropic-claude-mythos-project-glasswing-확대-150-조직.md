---
title: "[AI] Anthropic Claude Mythos, Project Glasswing 확대 — 150개 조직·15개국에 배포"
date: 2026-06-05 07:30:00 +09:00
categories: [AI]
tag: [Claude, Anthropic, Mythos, ProjectGlasswing, 사이버보안]
---

## 서론

2026년 6월 2일과 3일, Anthropic이 **Project Glasswing**의 두 번째 확대를 공식 발표했다. 4월 7일 처음 출범했을 당시 약 50개 파트너 조직으로 시작했던 이 프로그램이, 이번에는 15개국 이상에 걸친 **150개 신규 조직**으로 확대된 것이다. 이에 따라 Anthropic의 플래그십 모델 **Claude Mythos Preview**에 접근할 수 있는 파트너 수가 대폭 늘어났다.

Claude Mythos가 주목받는 이유는 단순히 벤치마크 점수가 높아서가 아니다. 이 모델은 **사이버보안** 분야에서 특별히 강력한 역량을 갖춘 것으로 확인됐으며, 이미 수만 건의 고위험 소프트웨어 취약점을 자율적으로 발견했다는 데이터가 공개됐다. Anthropic이 이 모델을 일반 출시하지 않고 "초대 전용 파트너 프로그램"을 통해 통제된 방식으로 배포하는 것도 그 강력한 능력에서 비롯된 안전 정책이다.

이번 글에서는 Claude Mythos가 무엇인지, Project Glasswing이 왜 이례적인 방식으로 운영되는지, 그리고 업계가 이 확대 소식에 어떻게 반응하고 있는지를 정리한다.

## 본론

### Claude Mythos란 무엇인가

Claude Mythos는 Anthropic이 2026년 4월 7일 공개한 **프론티어급 AI 모델**로, Anthropic의 현 라인업에서 가장 강력한 모델 패밀리다. 이전에 공개된 Claude Opus 4.8과는 별개의 계보로, 특히 **사이버보안 태스크**에서 두드러진 성능을 보인다.

Anthropic이 공개한 벤치마크 수치는 다음과 같다.

| 평가 항목 | Claude Mythos Preview 점수 |
|---|---|
| SWE-bench Verified | 93.9% |
| SWE-bench Pro | 77.8% |
| Terminal-Bench 2.0 | 82.0% |
| USAMO 2026 | 97.6% |

SWE-bench Verified 기준으로 93.9%는 현재 공개된 모델 중 최상위권 수치다. 이 벤치마크는 실제 GitHub 이슈를 기반으로 모델이 버그를 직접 수정할 수 있는지를 평가하는데, 이 점수는 단순히 코드 이해 능력이 뛰어나다는 것을 넘어, 실제 소프트웨어 엔지니어링 작업에서 자율적으로 문제를 해결하는 능력을 검증한다.

보안 분야에서의 성능은 특히 주목할 만하다. Anthropic은 Mythos Preview가 자율적으로 **수천 건의 제로데이 취약점**을 발견했다고 밝혔으며, 그 중에는 다음과 같은 사례도 포함된다.

- **27년 된 OpenBSD TCP SACK 원격 코드 실행 버그**: 수십 년간 발견되지 않았던 취약점을 모델이 자율 탐지했다.
- **17년 된 FreeBSD NFS RCE** (CVE-2026-4747로 등록): 마찬가지로 오랫동안 알려지지 않았던 취약점.

이 수치는 AI가 단순한 코딩 보조 도구를 넘어, 대규모 코드베이스를 스캔하고 취약점을 찾아내는 **자율 보안 엔지니어**로 기능할 수 있음을 보여준다. 이것이 동시에 이 모델이 왜 일반 공개가 아닌 통제된 환경에서만 제공되는지의 이유이기도 하다.

### Project Glasswing 1.0: 최초 출범 (4월 7일)

Anthropic은 Claude Mythos를 공개하면서 동시에 **Project Glasswing**을 발표했다. Glasswing은 Mythos Preview에 대한 접근을 관리하기 위한 초대 전용 파트너 프로그램으로, 초기 파운딩 파트너로는 다음과 같은 기업들이 이름을 올렸다.

- Apple, Amazon, Broadcom, CrowdStrike, Microsoft, NVIDIA

이 파트너들은 Mythos Preview를 활용해 자사 코드베이스의 취약점을 탐색하고, 동시에 Anthropic에게 모델 안전성 피드백을 제공하는 쌍방향 협력 구조로 운영된다.

Project Glasswing의 목표는 두 가지다. 첫째, Mythos를 통해 **세계 소프트웨어 보안 수준을 전반적으로 끌어올리는 것**. 둘째, 고도로 강력한 AI 모델을 책임감 있게 배포하기 위한 **업계 관행을 함께 만들어가는 것**. Anthropic은 공식 발표에서 "우리는 AI가 모든 소프트웨어를 더 안전하게 만드는 미래를 원하며, 업계가 AI가 바꿀 사이버보안의 핵심 가정들에 적응할 수 있도록 돕고자 한다"고 밝혔다.

### Project Glasswing 2.0: 15개국 150개 기관으로 확대 (6월 2-3일)

이번 확대의 핵심은 **지리적 범위와 산업 다양성**의 확장이다. CNBC(2026년 6월 2일)와 TechCrunch(2026년 6월 2일), Help Net Security(2026년 6월 3일) 등의 보도에 따르면:

- 기존 초기 코호트에서 충분히 대표되지 않았던 산업 분야 — **전력, 수도, 의료, 통신, 하드웨어** — 가 이번 확대의 핵심 대상이다.
- 미국 외 인도, 유럽 등 **15개국 이상**으로 지리적 범위가 넓어졌다.
- 미국 정부 기관 및 오픈소스 소프트웨어 관리자들과의 협력도 몇 주간 진행됐다.

Anthropic이 이번 확대 대상으로 특히 **인프라 운영자**들을 강조한 데는 이유가 있다. 전력망, 수도 시스템, 병원 네트워크 같은 핵심 인프라는 소프트웨어 취약점이 단순한 데이터 유출을 넘어 **물리적 피해**로 이어질 수 있는 환경이다. Mythos의 자율 취약점 탐지 능력을 이 분야에 활용하는 것이 사회적으로 가장 큰 임팩트를 낼 수 있다는 판단이 깔려 있다.

Anthropic은 또한 Mythos Preview가 출범 이후 **1만 건 이상의 고위험 또는 심각한 소프트웨어 취약점**을 발견했다고 밝혔다. 이 수치는 단순한 PoC 수준의 탐색이 아닌, 실제 운영 환경에서 사용되는 소프트웨어들에서 찾아낸 실질적인 취약점들이다.

### Mythos의 사이버보안 능력 — 자율 취약점 탐지의 의미

Mythos가 자율적으로 취약점을 찾아낸다는 것은 보안 업계의 기존 작업 방식에 상당한 함의를 갖는다.

**전통적인 취약점 발견 과정**은 다음과 같다.

```text
1. 사람 연구자가 코드를 읽으며 수상한 부분을 파악
2. 퍼징(fuzzing) 도구를 실행해 입력 변형을 대량으로 테스트
3. 정적 분석 도구로 알려진 패턴을 탐지
4. 발견된 이슈를 수동으로 검증
```

이 과정은 경험 많은 보안 연구자 1명이 1개 취약점을 찾는 데 수 주~수 개월이 걸릴 수 있다. 코드베이스가 크고 오래될수록 더 그렇다.

Mythos가 OpenBSD의 27년 된 TCP SACK 버그를 자율적으로 발견했다는 사실은, AI가 **수십 년간 사람이 못 본 패턴을 코드에서 읽어낼 수 있다**는 것을 보여준다. FreeBSD NFS RCE(CVE-2026-4747) 역시 마찬가지다. 이 17년 된 버그는 많은 사람이 코드를 봤을 텐데도 발견되지 않았던 것이다.

동시에 이 능력은 공격자의 손에 쥐어질 경우의 위험성을 뜻하기도 한다. Anthropic이 Glasswing을 통해 접근을 엄격히 관리하는 근본적인 이유다.

### Mythos와 Claude Code — 가까운 미래의 통합 가능성

BleepingComputer는 "Anthropic의 제한된 Claude Mythos 모델이 Claude Code에 도입될 수도 있다"는 제목의 기사를 보도했다. Anthropic 측은 공식 발표에서 "Mythos급 모델을 모든 고객에게 제공하기 위한 안전장치 개발을 빠르게 진행 중이며, 몇 주 안에 가능할 것으로 기대한다"고 언급했다.

만약 Mythos가 Claude Code에 통합된다면, 개발자들은 코드를 작성하면서 동시에 Mythos의 취약점 탐지 능력을 활용하는 형태로 이용할 수 있을 것이다. 단순히 "코드가 동작하는지"를 확인하는 게 아니라, "이 코드가 보안적으로 안전한지"를 모델이 실시간으로 점검하는 환경이 가능해진다.

### 업계 반응

**CyberScoop**은 "Anthropic이 Project Glasswing을 통해 핵심 인프라 운영자들에게 접근을 확대하는 것은, 단순한 AI 제품 출시를 넘어 AI를 국가 사이버방어 체계의 일부로 통합하려는 시도"라고 평가했다.

**Cybersecurity Dive**는 "Glasswing의 확대가 Mythos가 발견한 1만 건 이상의 취약점 데이터를 기반으로 이루어졌다는 점에서, 이것은 단순한 마케팅 발표가 아닌 실질적인 보안 임팩트를 보여주는 결과"라고 분석했다.

**SecurityWeek**은 "150개 신규 조직으로의 확대가 Mythos에 대한 통제된 접근을 유지하면서도 임팩트를 최대화하려는 Anthropic의 전략적 선택"이라고 평가하며, 향후 일반 사용자 접근이 어떤 방식으로 이루어질지에 대한 의문을 제기했다.

한편, AI 안전 연구 커뮤니티에서는 Mythos급 모델의 "통제된 배포"가 실질적인 안전장치가 될 수 있는지에 대한 논쟁도 이어지고 있다. 파트너로 선정된 조직들이 모델을 올바르게 사용하는지를 Anthropic이 어떻게 검증하는지, 모델이 발견한 취약점 정보가 어떻게 관리되는지 등이 주요 쟁점이다.

**India's Inc42**는 "인도가 Glasswing에 포함됐다는 것은 Anthropic이 미국과 유럽 중심의 사이버보안 AI 협력 구조를 아시아-태평양 지역으로 확장하고 있음을 보여준다"고 보도했다.

## 정리

- Anthropic은 2026년 6월 2-3일, Project Glasswing을 15개국 이상의 150개 신규 조직으로 확대했다.
- 이번 확대의 핵심 대상은 초기 코호트에서 충분히 대표되지 않았던 전력·수도·의료·통신·하드웨어 분야 인프라 운영자들이다.
- Claude Mythos Preview는 4월 출범 이후 1만 건 이상의 고위험·심각 소프트웨어 취약점을 자율 탐지했다.
- Mythos는 OpenBSD 27년 된 TCP SACK RCE, FreeBSD 17년 된 NFS RCE(CVE-2026-4747) 같이 오랫동안 발견되지 않은 취약점을 찾아냈다.
- SWE-bench Verified 93.9%, SWE-bench Pro 77.8%, Terminal-Bench 2.0 82.0% — 현재 공개된 모델 중 최상위권 벤치마크를 기록했다.
- Anthropic은 "몇 주 안에 Mythos급 모델을 모든 고객에게 제공할 수 있을 것"이라고 밝혀, Claude Code와의 통합 가능성도 언급됐다.
- 일반 공개 전까지, 보안팀은 Glasswing 파트너 활동과 Anthropic의 공개 보안 발표를 모니터링하는 것이 현실적인 방법이다.

## Reference

- [Anthropic — Expanding Project Glasswing](https://www.anthropic.com/news/expanding-project-glasswing)
- [TechCrunch — Anthropic scales Claude Mythos to critical infrastructure in 15+ countries](https://techcrunch.com/2026/06/02/anthropic-scales-claude-mythos-to-critical-infrastructure-in-15-countries/)
- [CNBC — Anthropic expands Mythos to 150 additional organizations in more than 15 countries](https://www.cnbc.com/2026/06/02/anthropic-mythos-ai-project-glasswing.html)
- [SecurityWeek — Anthropic Expanding Mythos Access to 150 New Organizations](https://www.securityweek.com/anthropic-expanding-mythos-access-to-150-new-organizations/)
- [Help Net Security — Anthropic expands Project Glasswing to 150 organizations in more than 15 countries](https://www.helpnetsecurity.com/2026/06/03/anthropic-project-glasswing-expansion/)
- [CyberScoop — Anthropic expanding access to Project Glasswing](https://cyberscoop.com/anthropic-project-glasswing-expansion-critical-infrastructure-claude-mythos/)
- [BleepingComputer — Anthropic's restricted Claude Mythos model may be coming to Claude Code](https://www.bleepingcomputer.com/news/artificial-intelligence/anthropics-restricted-claude-mythos-model-may-be-coming-to-claude-code/)
- [Cybersecurity Dive — Anthropic shares Mythos with 150 more organizations, including critical infrastructure operators](https://www.cybersecuritydive.com/news/ai-anthropic-claude-mythos-project-glasswing-expand/821714/)
