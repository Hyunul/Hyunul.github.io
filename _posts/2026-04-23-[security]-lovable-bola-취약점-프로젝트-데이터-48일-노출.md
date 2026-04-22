---
title: "[Security] Lovable 바이브코딩 플랫폼, BOLA 취약점으로 수천 프로젝트 데이터 48일간 노출"
date: 2026-04-23 07:02:00 +09:00
categories: [Security]
tag: [Lovable, BOLA, API보안, 바이브코딩, 데이터유출]
---

## 서론

2026년 4월 20일, 보안 연구자 @weezerOSINT가 AI 기반 바이브코딩(vibe coding) 플랫폼 Lovable에서 심각한 데이터 유출 취약점을 공개적으로 폭로했다. 발표 내용은 충격적이었다. 무료 계정 하나만 만들면 2025년 11월 이전에 생성된 다른 사용자의 프로젝트 소스코드, AI 대화 기록, 데이터베이스 자격증명, 심지어 연결된 외부 DB의 프로덕션 데이터까지 자유롭게 읽을 수 있다는 내용이었다.

사태를 더 심각하게 만드는 건 타이밍이다. 이 취약점은 공개 폭로보다 48일 앞선 2026년 3월 3일에 이미 버그 바운티 플랫폼 HackerOne을 통해 공식 보고되었다. 그러나 HackerOne 측은 이를 "중복 제출"로 분류해 에스컬레이션 없이 종료했고, Lovable은 사실상 48일간 이 취약점을 방치했다.

이 사건은 단순한 보안 결함을 넘어, 빠르게 성장 중인 AI 바이브코딩 플랫폼 시장의 멀티테넌시 보안 설계 실패, 버그 바운티 운영의 구조적 허점, 그리고 AI가 생성한 코드를 무비판적으로 배포하는 트렌드가 내포한 위험을 동시에 드러낸 사례로 주목받고 있다.

## 본론

### BOLA란 무엇인가

이번 사건의 핵심 취약점은 **BOLA(Broken Object Level Authorization)**다. BOLA는 OWASP API Security Top 10에서 1위를 차지하고 있는 취약점 유형으로, API가 특정 리소스에 대한 접근 요청을 처리할 때 요청자가 해당 리소스에 접근할 권한이 있는지를 제대로 검증하지 않는 문제를 말한다.

쉽게 풀면, 사용자 A의 프로젝트에 접근하는 API 엔드포인트가 있을 때, 사용자 B가 URL의 ID 값만 바꿔서 A의 프로젝트에 접근해도 서버가 이를 막지 못하는 상황이다. 개별 객체(object) 수준에서의 인가(authorization) 검증이 빠져 있기 때문에 발생한다.

Lovable의 경우 연구자는 단 **5번의 API 호출**만으로 다른 사용자의 프로필, 공개/비공개 프로젝트 목록, 소스코드 전체를 추출했다. 그리고 해당 소스코드 안에 하드코딩되어 있던 Supabase API 키를 통해 프로덕션 데이터베이스 접근까지 연결했다. 전형적인 BOLA 익스플로잇 패턴이다.

### 타임라인 정리

이번 사건을 이해하려면 48일에 걸친 타임라인을 따라가 봐야 한다.

- **2025년 11월**: Lovable이 백엔드 권한 시스템 통합을 위한 대규모 리팩토링을 진행
- **2026년 2월**: 리팩토링 과정에서 공개 프로젝트의 채팅 기록 접근이 의도치 않게 재활성화되는 회귀(regression) 발생
- **2026년 3월 3일**: 보안 연구자 @weezerOSINT가 HackerOne을 통해 취약점 정식 보고
- **2026년 3월 3일 직후**: HackerOne 파트너 측이 해당 제보를 "다른 제출의 중복"으로 분류하고 에스컬레이션 없이 종료
- **2026년 4월 20일**: @weezerOSINT가 X(트위터)를 통해 공개 폭로. "Lovable에는 2025년 11월 이전 모든 프로젝트를 대상으로 하는 대규모 데이터 침해가 존재한다"고 발표
- **2026년 4월 20일 이후**: The Register, Fast Company, The Next Web, CyberNews 등 주요 매체 일제히 보도

### 노출된 데이터의 범위

The Register와 Cyber Kendra의 보도에 따르면, 이 취약점을 통해 접근 가능했던 데이터는 다음과 같다.

- 다른 사용자의 **프로젝트 소스코드** 전체
- LLM과의 **AI 대화 기록**: 어떤 프롬프트를 사용했는지, 어떤 시스템 컨텍스트가 주입됐는지 포함
- 소스코드 내 하드코딩된 **데이터베이스 자격증명**: Supabase API 키 등
- 해당 자격증명을 통해 접근 가능한 **연결된 프로덕션 DB의 실제 데이터**: 사용자 이름, 이메일, 생년월일 등

특히 Lovable을 업무에 실제로 사용하는 기업으로 **Uber, Zendesk, Deutsche Telekom** 등이 포함된 것으로 알려지면서, 잠재적 피해 규모에 대한 우려가 더욱 커졌다.

### 혼란스러운 회사 대응

공개 폭로 직후 Lovable의 대응은 업계의 강한 비판을 받았다.

첫 번째 공식 반응은 "이는 의도된 동작이며, 문서화가 불명확했을 뿐"이라는 주장이었다. 공개 프로젝트의 채팅 기록이 외부에서 보이는 것은 설계상 의도한 기능이라는 논리였다. 이 해명은 즉각 강한 반발에 부딪혔다. 사용자들은 "내 Supabase 프로덕션 API 키가 타인에게 노출되는 게 '의도된 기능'이라는 말이냐"며 항의했다.

이후 Lovable은 입장을 번복해 "2026년 2월 백엔드 통합 과정에서 발생한 의도치 않은 회귀"라고 인정했다. 동시에 "우리의 HackerOne 파트너가 이 보고를 제대로 에스컬레이션하지 않았다"며 책임의 일부를 버그 바운티 서비스에 떠넘겼다. CyberNews는 이 일련의 해명 시도를 두고 "vibesplaining(바이브코딩 + gaslighting의 합성어)"이라는 신조어로 풍자했다.

Lovable의 대응이 더 문제가 된 건, 최초 보고부터 공개 폭로까지 48일이라는 시간 동안 아무런 조치도 이루어지지 않았다는 점이다. 버그 바운티 채널이 있다고 해서 보안 취약점이 자동으로 해결되지는 않는다는 점을 다시 한번 확인하는 사례가 됐다.

### 바이브코딩 플랫폼의 구조적 보안 문제

The Next Web은 이번 사건을 단순히 Lovable의 실수가 아닌 "바이브코딩 플랫폼의 구조적 보안 실패"로 분석했다.

바이브코딩 플랫폼은 사용자가 자연어로 요구사항을 설명하면 LLM이 코드를 자동 생성해 배포해주는 방식이다. 이 접근 방식의 본질적인 문제는, LLM이 생성하는 코드가 "동작하는 것"에는 최적화되어 있지만 "안전하게 동작하는 것"에는 최적화되어 있지 않다는 점이다.

특히 멀티테넌시 환경에서의 **테넌트 간 데이터 격리**는 단순한 코드 생성 이상의 보안 아키텍처 설계가 필요하다. 어떤 사용자가 어떤 리소스에 접근할 수 있는지를 모든 API 엔드포인트에서 일관되게 검증하는 것은 LLM이 자동으로 해결해주지 않는 영역이다.

또한, 개발자가 코드를 직접 작성하지 않고 AI에게 위임할수록 코드 리뷰 과정에서 인증/인가 로직의 취약점을 발견하기가 훨씬 어렵다. 바이브코딩의 편리함이 역설적으로 보안 검증을 더 어렵게 만드는 구조다.

보안 전문가들은 이번 사건을 계기로, 바이브코딩 플랫폼을 사용하는 기업은 플랫폼의 보안을 맹신하지 말고 **자체적인 보안 검증 레이어를 반드시 갖춰야 한다**는 점을 강조하고 있다.

### 소스코드에 자격증명을 박는 관행

이번 사건에서 드러난 또 하나의 문제는, Supabase API 키 등 민감한 자격증명이 소스코드에 하드코딩되어 있었다는 점이다. 이 자격증명들은 바이브코딩 플랫폼이 자동 생성한 코드 안에 포함된 것으로 알려졌다.

환경 변수(environment variable)나 시크릿 관리 서비스(AWS Secrets Manager, HashiCorp Vault 등)를 통해 자격증명을 분리하는 것은 보안의 기본 원칙이다. 그러나 빠르게 프로토타입을 만드는 바이브코딩 환경에서는 이 원칙이 종종 무시되거나 자동 생성 코드에 반영되지 않는다.

BOLA 취약점으로 소스코드가 유출되면 하드코딩된 자격증명도 함께 노출된다는 점에서, 이번 사건은 두 가지 보안 실패가 중첩된 사례다.

```python
# 이런 방식은 절대 금지
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 환경변수 또는 시크릿 관리 서비스를 사용해야 한다
import os
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
```

### 버그 바운티의 맹점

이번 사건에서 또 하나의 교훈은 버그 바운티 프로그램의 운영 방식에 관한 것이다. 취약점이 48일 전에 정식 채널을 통해 보고되었음에도 "중복 제출" 처리로 방치된 것은, 버그 바운티 운영에서 트리아지(triage)와 에스컬레이션 프로세스가 얼마나 중요한지를 보여준다.

취약점 보고를 접수하는 채널이 존재한다고 해서 보안 대응이 자동으로 이루어지는 게 아니다. 보고된 취약점이 제대로 분류되고, 실제 리스크를 평가받고, 적절한 팀에 에스컬레이션되는 프로세스 전체가 작동해야 한다. 채널만 있고 프로세스가 없으면 버그 바운티는 사실상 의미가 없다.

## 정리

이번 Lovable 사태는 세 가지 명확한 교훈을 남긴다.

첫째, **API 보안의 기본인 객체 수준 인가(BOLA) 검증은 AI 플랫폼에서도 예외가 없다.** 아무리 혁신적인 AI 기능을 제공하더라도, 멀티테넌시 환경에서 다른 사용자의 리소스에 접근하지 못하도록 막는 기본 보안은 타협 대상이 아니다. OWASP API Top 1위 취약점이 실제 프로덕션에서 이런 형태로 터진다는 사실 자체가 이 원칙이 얼마나 쉽게 무시되는지를 보여준다.

둘째, **버그 바운티 채널의 존재가 보안 대응의 실효성을 보장하지 않는다.** 취약점 접수 창구와 실제 대응 프로세스는 별개다. 48일간의 방치는 두 번째 방어선이 존재하지 않았음을 의미한다.

셋째, **바이브코딩 플랫폼을 사용하는 기업은 플랫폼 보안을 그대로 신뢰해서는 안 된다.** LLM이 생성한 코드는 편리하지만, 보안 관점에서의 검증 책임은 여전히 사용 기업과 서비스 제공자 모두에게 있다. 소스코드에 하드코딩된 자격증명이 타인에게 노출된 이번 사례는, 바이브코딩의 편리함과 보안 관행 사이의 간극이 실제로 어떤 결과를 낳는지를 생생하게 보여준다.

## Reference

- [Vibe coding upstart Lovable denies data leak, cites 'intentional behavior,' then throws HackerOne under the bus - The Register](https://www.theregister.com/2026/04/20/lovable_denies_data_leak/)
- [Lovable Left Thousands of Projects Exposed for 48 Days — And Still Hasn't Fixed It - Cyber Kendra](https://www.cyberkendra.com/2026/04/lovable-left-thousands-of-projects.html)
- [Lovable security crisis: 48 days of exposed projects, closed bug reports, & the structural failure of vibe coding security - The Next Web](https://thenextweb.com/news/lovable-vibe-coding-security-crisis-exposed)
- [Lovable left AI prompts and user data exposed, one researcher found - Fast Company](https://www.fastcompany.com/91530092/lovable-left-ai-prompts-and-user-data-exposed-researcher-found)
- [Lovable vibesplains vulnerability to researcher, says it's actually design - CyberNews](https://cybernews.com/security/lovable-vibe-coding-flaw-apology/)
- [Lovable AI App Builder Reportedly Exposes Thousands of Project Data via API Flaw - Cyberpress](https://cyberpress.org/lovable-ai-app-builder-reportedly-exposes-thousands-of-project-data-via-api-flaw/)
- [Lovable data breach: What Was Exposed & How to Respond - Bastion](https://bastion.tech/blog/lovable-april-2026-data-breach/)
