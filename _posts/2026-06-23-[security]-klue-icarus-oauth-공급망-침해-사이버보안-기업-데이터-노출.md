---
title: "[security] Klue OAuth 공급망 침해 — 사이버보안 기업 Salesforce 데이터 무더기 유출"
date: 2026-06-23 07:30:00 +09:00
categories: [security]
tag: [supply-chain, OAuth, Salesforce, Icarus, CRM, data-breach]
---

## 서론

6월 22일(현지 시간), TechCrunch를 포함한 복수의 보안 매체가 일제히 보도를 쏟아냈다. 피해 당사자가 다름 아닌 Huntress, Recorded Future, Jamf, Tanium 같은 사이버보안 전문 기업들이라는 점에서 업계의 충격은 더 컸다. 칼잡이가 칼에 맞은 격이었다. 보안을 업으로 삼는 회사들의 CRM 데이터가 고스란히 빠져나간 것이다.

이번 사건의 진원지는 마켓 인텔리전스(경쟁 분석) SaaS 플랫폼 **Klue**다. Klue의 통합 인프라를 침해한 공격자들은 Klue가 보관 중이던 고객사의 OAuth 토큰을 통째로 탈취했고, 이를 이용해 Salesforce, Gong 등 CRM 서비스에서 영업 데이터를 빼냈다. 각 피해 기업들은 "자사 제품과 서비스는 영향을 받지 않았다"는 공식 성명을 냈지만, 영업 파이프라인, 고객 연락처, 계약 가격 정보 같은 민감한 비즈니스 데이터는 이미 경쟁 수준의 범죄 조직 손에 넘어간 뒤였다.

이번 사건은 단순한 자격증명 유출이 아니다. SaaS 플랫폼 간 통합(integration)을 통해 공급망이 어떻게 무너질 수 있는지를 생생히 보여주는 케이스다. 특히 OAuth 토큰이라는 "신뢰의 열쇠"가 제3자 플랫폼 수준에서 탈취될 수 있다는 점은, API 통합 보안을 재점검해야 할 명확한 이유를 제시한다. SaaS 도구를 수십 개씩 연결해 쓰는 현대 업무 환경에서 이 공격의 구조는 앞으로도 반복될 가능성이 높다.

## 본론

### 공격 타임라인

**6월 12일** — Klue의 보안팀이 통합 인프라 내 비정상 활동을 감지했다. 공격자는 Klue가 수년 전 서드파티 통합 프로토타입을 위해 만들었다가 삭제하지 않고 방치한 레거시 자격증명을 이용해 최초 침투에 성공했다. 사용되지 않지만 삭제되지 않은 오래된 계정, 이른바 "좀비 자격증명"이 공격의 시작점이었다.

공격자는 이 자격증명을 통해 Klue 백엔드 시스템에 코드를 밀어 넣었다. 새로 삽입된 코드는 고객사들이 Klue와 연동할 때 제공한 OAuth 토큰을 수집하는 역할을 했다. Klue의 통합 인프라가 보관하고 있는 토큰들은 Salesforce, Gong, HubSpot, SharePoint, Zoom, Chorus, Clari, Google Drive, Slack 등 여러 서비스에 대한 접근 권한을 담고 있었다.

**6월 19일** — Klue CEO Jason Smith가 공식 성명을 발표했다. 침해 사실을 인정하고, 영향을 받은 OAuth 토큰과 자격증명을 즉시 폐기했으며, CrowdStrike와 함께 인시던트 대응을 진행 중이라고 밝혔다. 동시에 Salesforce는 Klue Battlecards 앱 통합을 전면 비활성화했다.

**6월 20일** — "Icarus"라고 자신을 부르는 갈취 그룹이 Klue 고객사들에게 직접 연락을 취했다. 6월 22일까지 대응하지 않으면 탈취한 데이터를 다크웹 유출 사이트에 공개하겠다는 협박이었다.

**6월 22일** — TechCrunch, SecurityWeek, BleepingComputer 등 복수의 매체에서 피해 기업들의 공식 확인을 담은 기사들이 쏟아졌다. Huntress, Recorded Future, Jamf, Tanium이 각각 피해 사실을 공식 인정했다.

### 공격 벡터 분석: OAuth 통합의 구조적 취약점

이번 사건에서 핵심적으로 살펴봐야 할 점은, 공격자가 각 피해 기업의 내부 시스템을 직접 뚫지 않았다는 것이다. 대신 이들이 공통으로 의존하던 **제3자 서비스(Klue)**를 통해 우회 침투했다. 이것이 전형적인 공급망 공격의 패턴이다.

OAuth 통합의 동작 방식을 생각해보면 이 구조적 취약점이 명확해진다. 고객사가 Klue와 Salesforce를 연동할 때, Klue는 고객의 Salesforce 계정에 접근할 수 있는 OAuth 액세스 토큰을 발급받아 자체 서버에 저장한다. 이 토큰을 이용해 Klue 서비스가 고객 데이터를 주기적으로 가져오는 구조다.

```
[고객사 Salesforce]
        |
        | OAuth 토큰 발급 및 저장
        v
[Klue 통합 서버 (중간 노드)]
        |
        | Klue가 침해되면 → 저장된 모든 토큰 노출
        v
[공격자]
        |
        | 탈취한 토큰으로 고객사 Salesforce에 직접 접근
        v
[영업 데이터 무단 조회/탈취]
```

문제는 이 토큰이 Klue 서버에 집중 저장된다는 것이다. Klue의 인프라가 뚫리면, 공격자는 Klue가 보관 중인 모든 고객사의 OAuth 토큰에 한꺼번에 접근할 수 있다. 각 고객사가 아무리 내부 보안을 철저히 갖추고 있어도 소용없다. 신뢰를 위임(delegate)한 제3자가 무너지면, 그 신뢰 전체가 함께 무너진다.

### 위협 행위자: Icarus 그룹

공격 배후로 지목된 Icarus 그룹은 2026년 4월 28일부터 활동이 확인된 비교적 새로운 갈취 조직이다. 보안 기업 Huntress는 자사 침해 조사에서 갈취 이메일과 Icarus의 다크웹 유출 사이트에 남겨진 Session Messenger ID가 동일하다는 점을 발견하고, Icarus의 소행임을 높은 신뢰도로 특정했다.

Icarus의 전략은 전형적인 **이중 갈취(double extortion)** 방식이다. 데이터를 탈취한 뒤 피해 기업에 조용히 연락해 협박 기한을 설정하고, 응하지 않으면 탈취 데이터를 공개하겠다고 위협한다. 이번에는 6월 22일을 기한으로 잡았다.

그룹 이름 "Icarus"는 그리스 신화에서 밀랍 날개로 태양 가까이 날다 추락한 인물을 가리킨다. 사이버보안 기업들까지 침해했다는 점에서, 이름에 걸맞은 대담함이 있다는 평가도 있다.

### 피해 범위와 탈취 데이터

공개적으로 확인된 피해 조직은 다음과 같다:
- **Huntress** — 엔드포인트 보안 솔루션 제공 기업
- **Recorded Future** — 위협 인텔리전스 전문 기업
- **Jamf** — Apple 기기 관리 솔루션 기업
- **Tanium** — 기업용 엔드포인트 관리 플랫폼
- **Gong** — 영업 대화 분석 플랫폼
- **Insurity** — 보험 업계 소프트웨어 솔루션 기업
- **Sprout Social** — 소셜 미디어 관리 플랫폼

이 중 다수가 사이버보안 또는 IT 보안 솔루션을 제공하는 기업이라는 점에서 아이러니가 크다. 보안 기업들이 동시에 피해를 입었다는 사실은, 이 공격이 Klue를 공통 접점으로 삼아 특정 생태계를 겨냥한 것임을 시사한다.

탈취된 데이터는 주로:
- Salesforce CRM에 저장된 영업 파이프라인 및 기회(Opportunity) 정보
- 고객 연락처 및 이메일 커뮤니케이션 이력
- 계약 가격 정보 및 영업 제안서
- Gong에 기록된 영업 통화 녹취 및 AI 생성 요약

각 기업은 "자사 제품 및 서비스는 영향을 받지 않았다"고 발표했다. 즉, 보안 솔루션 자체가 침해된 것은 아니지만, 영업 데이터가 경쟁 수준의 조직에게 노출됐다는 것은 사업적 피해로 이어질 수 있다. 특히 가격 정보나 영업 전략이 담긴 데이터는 경쟁사 혹은 범죄 조직에 활용될 여지가 있다.

### Klue의 인시던트 대응

Klue는 침해 감지 이후 다음 조치를 단계적으로 취했다:
- 영향받은 자격증명 및 OAuth 토큰 즉시 폐기
- Salesforce, Gong, HubSpot, SharePoint, Zoom, Chorus, Clari, Google Drive, Slack App 통합 전면 비활성화
- 악성 코드 제거 및 인프라 격리
- CrowdStrike 인시던트 대응팀 투입
- 법 집행기관 통보
- CEO 명의 공식 성명 발표 (6월 19일)

Salesforce 또한 Klue Battlecards 앱을 플랫폼에서 즉시 비활성화하고 "추가 조사가 완료될 때까지 통합을 복구하지 않을 것"이라고 밝혔다. 이 결정은 Klue에게는 서비스 중단이었지만, 피해 확산을 막기 위한 불가피한 조치였다.

### 레거시 자격증명이라는 만성적 취약점

이번 사건의 직접적 원인이 된 "사용하지 않는 레거시 자격증명" 문제는 생각보다 훨씬 만연하다. 개발 과정에서 임시로 만든 테스트 계정, 퇴사한 직원의 서비스 계정, 더 이상 쓰이지 않는 API 키 등이 조직 전반에 산재해 있는 경우가 많다. 이런 계정들은 대부분 정기 감사 대상에서 누락되고, 자격증명 회전(rotation) 정책에도 포함되지 않는다.

Datadog Security Labs는 이번 사건 이후 Salesforce 감사 로그를 이용해 Klue 공급망 공격 활동을 탐지하는 방법을 상세히 공개했다. 비정상적인 IP에서의 API 접근, 예상치 못한 데이터 내보내기 패턴 등을 Salesforce 이벤트 모니터링으로 조기에 감지할 수 있다는 내용이다.

## 정리

- Klue OAuth 통합 인프라 침해 → 고객사의 Salesforce 등 서비스 OAuth 토큰 탈취 → CRM 데이터 대규모 유출
- 피해 조직: Huntress, Recorded Future, Jamf, Tanium, Gong, Insurity, Sprout Social 등 7곳 이상, 다수가 사이버보안 전문 기업
- 위협 행위자: Icarus 갈취 그룹, 2026년 4월부터 활동, 이중 갈취 전략 구사
- 근본 원인: 방치된 레거시 자격증명 + OAuth 토큰의 제3자 집중 보관 구조
- 방어 체크리스트:
  - 사용하지 않는 자격증명은 즉시 폐기 (서비스 계정 생명주기 관리 필수)
  - SaaS 통합 시 OAuth 권한 범위(scope) 최소화 (least privilege 원칙)
  - 제3자 통합 파트너 보안 자세(security posture)를 공급업체 심사 항목에 포함
  - 정기적인 OAuth 토큰 감사, 필요 없는 통합 즉시 해제
  - Salesforce 등 CRM에서 이상 접근 패턴을 탐지하는 이벤트 모니터링 구성
- 업계 반응: Datadog Security Labs는 Salesforce 로그를 활용한 Klue 공격 탐지 방법을 블로그에 공개했으며, Huntress는 자사 조사 내용을 상세 보고서로 발표해 커뮤니티 공유를 이끌었다. SecurityWeek는 이번 사건이 "통합(integration) 보안이 SaaS 보안 전략의 핵심이 돼야 한다"는 점을 보여주는 사례라 평했다.

## Reference

- [Klue hack results in data breach at several cybersecurity firms | TechCrunch](https://techcrunch.com/2026/06/22/klue-hack-results-in-data-breach-at-several-cybersecurity-firms/)
- [Salesforce Disables Klue App Integration After OAuth Token Abuse Exposes Customer Data | The Hacker News](https://thehackernews.com/2026/06/salesforce-disables-klue-app.html)
- [Klue OAuth breach linked to 'Icarus' Salesforce data theft attacks | BleepingComputer](https://www.bleepingcomputer.com/news/security/klue-oauth-breach-linked-to-icarus-salesforce-data-theft-attacks/)
- [Cybersecurity Firms Impacted by Klue Supply Chain Attack | SecurityWeek](https://www.securityweek.com/cybersecurity-firms-impacted-by-klue-supply-chain-attack/)
- [Klue breach lead to Salesforce data theft, Huntress affected | Help Net Security](https://www.helpnetsecurity.com/2026/06/19/klue-salesforce-data-breach-huntress/)
- [Detecting the Klue supply chain attack in Salesforce instances | Datadog Security Labs](https://securitylabs.datadoghq.com/articles/detecting-the-klue-supply-chain-attack-in-salesforce/)
