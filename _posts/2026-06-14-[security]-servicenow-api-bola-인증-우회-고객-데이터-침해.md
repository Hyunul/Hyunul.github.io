---
title: "[Security] ServiceNow API BOLA 취약점 — 인증 없는 엔드포인트가 고객 데이터를 노출시킨 사건"
date: 2026-06-14 10:00:00 +09:00
categories: [Security]
tag: [API보안, BOLA, ServiceNow, 인증우회, 데이터침해, SaaS보안]
---

## 서론

2026년 6월 초, 엔터프라이즈 워크플로우 플랫폼 ServiceNow에서 심각한 보안 사고가 발생했다. `/api/now/related_list_edit/create`라는 API 엔드포인트가 `requires_authentication=false`로 설정된 상태로 운영되고 있었고, 공격자들은 이 사실을 파악해 6월 2~3일에 걸쳐 다수의 고객 인스턴스에서 데이터를 무단으로 조회했다. IT 서비스 티켓, 직원 기록, 내부 문서 같은 민감한 엔터프라이즈 데이터가 노출됐다.

ServiceNow는 6월 5일 패치를 적용했지만, 공개 공시는 6월 9일이 되어서야 이루어졌다 — 그것도 고객 지원 포털 로그인이 필요한 게이티드(gated) 어드바이저리로. 이 4일의 공시 지연과 게이티드 공개 방식이 제2의 논란을 일으켰다.

이번 사건이 더 충격적인 이유는, ServiceNow에서 8개월 안에 발생한 **세 번째 인증 관련 취약점**이라는 점이다. 그리고 이번이 처음으로 공격자가 패치 이전에 실제 고객 데이터에 도달한 사례다. SaaS 플랫폼의 API 보안 관리, 취약점 공시 프로세스, 고객 통보 의무에 대한 업계의 심층적인 문제 제기가 이어지고 있다.

## 본론

### 취약점 기술 분석: BOLA와 requires_authentication=false

이번 사고의 핵심은 **BOLA(Broken Object Level Authorization, OWASP API Security Top 10 #1)** 유형의 취약점이다. ServiceNow의 Scripted REST Resource 기능은 개발자가 커스텀 API 엔드포인트를 정의할 수 있게 해주는데, 이 기능에서 생성된 특정 엔드포인트가 잘못된 인증 설정으로 배포됐다.

문제가 된 엔드포인트:

```
/api/now/related_list_edit/create
```

이 엔드포인트는 내부적으로 `requires_authentication=false`로 설정되어 있었다. 유효한 세션 토큰이나 Bearer 토큰, 심지어 기본 인증(Basic Auth)조차 없이도 HTTP 요청을 받아들이고 처리했다. 이 엔드포인트는 고객 인스턴스의 데이터베이스 테이블에 대한 쿼리를 처리할 수 있는 권한을 가지고 있었고, 이 조합이 무인증 데이터 접근을 가능하게 만들었다.

공격자 입장에서 악용은 매우 간단했다. 정교한 취약점 체이닝이나 복잡한 익스플로잇이 전혀 필요 없었다. 인터넷에 공개된 고객 ServiceNow 인스턴스 URL만 알면 인증 없이 쿼리를 날릴 수 있었다.

```http
GET /api/now/related_list_edit/create?sysparm_query=...
Host: <고객-인스턴스>.service-now.com
```

이는 단순한 스캔 → 요청 → 데이터 수집 흐름으로 완결되는 공격이었다는 뜻이다.

### 사고 타임라인: 인지부터 공시까지

ServiceNow 사고의 전체 타임라인을 정리하면 다음과 같다.

**약 2026년 4월 7일**: Reddit을 통해 한 보안 팀이 이 취약점을 ServiceNow 버그 바운티 프로그램에 제출했다는 주장이 나왔다. 만약 사실이라면 ServiceNow는 실제 침해가 발생하기 약 2개월 전부터 이 취약점을 인지하고 있었다는 의미가 된다. ServiceNow는 이 주장에 대해 공식적인 입장을 밝히지 않았다.

**2026년 6월 2~3일**: 악성 행위자들이 인터넷 스캔을 통해 취약한 엔드포인트를 발견하고, 여러 고객 인스턴스를 대상으로 무인증 데이터 조회 공격을 실행했다. 네트워크 스캔과 의심스러운 활동이 이 기간에 집중됐다.

**2026년 6월 5일**: ServiceNow가 내부적으로 패치를 적용해 해당 엔드포인트의 `requires_authentication` 설정을 수정했다.

**2026년 6월 9일**: ServiceNow가 공식 보안 권고(Security Advisory)를 발행했다. 단, 이 권고는 일반에 공개된 것이 아니라 **고객 지원 포털에 로그인한 고객만 접근할 수 있는 게이티드 방식**이었다.

**2026년 6월 10~11일**: TechTimes, The Hacker News, BleepingComputer, SecurityWeek 등 주요 보안 매체가 게이티드 공시 방식을 비판하는 보도를 내보내면서 해당 사건이 광범위하게 알려졌다.

이 타임라인에서 주목해야 할 문제가 두 가지다.

**첫째, 패치(6월 5일)와 공시(6월 9일) 사이 4일의 공백.** 이 기간 동안 많은 고객사들은 자신의 데이터가 위험에 노출됐는지조차 알지 못했다. 침해가 이미 발생한 상황에서 4일간 고객에게 알리지 않은 것은 사고 대응 절차에 심각한 문제가 있음을 드러낸다.

**둘째, 게이티드 어드바이저리 방식.** 공개 CVE가 없고 포털 로그인이 필요한 구조는 보안 커뮤니티가 신속하게 정보를 공유하고 대응하기 어렵게 만든다. TechTimes는 이를 "고객들이 자신의 위험 노출 여부를 파악하는 것을 방해한 게이티드 어드바이저리"라고 비판했다.

### 노출된 데이터의 성격과 영향 범위

ServiceNow는 Fortune 500 기업 85%를 포함해 전 세계 수천 개 조직에서 사용된다. 이 플랫폼에는 일반적으로 다음과 같은 민감한 정보가 저장된다.

- **IT 서비스 관리 데이터**: 인프라 정보, 서버 목록, 취약점 현황, 보안 사고 기록
- **인사(HR) 데이터**: 직원 정보, 온보딩/오프보딩 기록, 급여 관련 요청
- **법무·컴플라이언스 데이터**: 계약서, 감사 로그, 규제 대응 현황
- **고객 지원 데이터**: 서포트 티켓, 고객 커뮤니케이션 내역

공격자가 IT 서비스 관리 데이터에 접근했을 경우, 해당 조직의 인프라 구조와 보안 취약점 정보를 확보할 수 있어 **후속 공격의 전략 지도**로 활용될 수 있다는 점이 특히 위험하다.

ServiceNow는 현재 어떤 조직의 어떤 데이터가 구체적으로 노출됐는지 공개하지 않았고, CVE 번호도 아직 할당하지 않은 상태 — 평가 중이라는 입장이다.

### 반복된 패턴: 8개월 안에 세 번째 인증 취약점

이번 사건을 더욱 심각하게 보는 이유는, ServiceNow에서 2025년 10월 이후 8개월 안에 발생한 **세 번째 인증 관련 취약점**이라는 점이다.

앞선 두 건은 인증 관련 결함이었으나 패치 전에 공격자가 고객 데이터에 접근한 사례는 없었다. 이번이 처음으로 침해가 패치를 앞선 경우다. 동일한 클래스의 취약점이 반복해서 발견된다는 것은 **근본적인 설계 또는 코드 리뷰 프로세스의 구조적 결함**이 있다는 신호로 받아들여지고 있다.

보안 업계에서는 이에 대해 "SaaS 플랫폼 벤더에게 API 보안 감사의 주기와 깊이를 재검토해야 한다는 신호"라는 의견이 지배적이다. SecurityWeek의 분석은 "패치가 적용됐어도 취약한 구성이 얼마나 오래 운영됐는지, 그 사이 얼마나 많은 고객이 영향받았는지 밝혀지지 않았다"고 지적했다.

### API 보안 관점에서의 구조적 교훈

이번 사고는 API 보안에서 몇 가지 근본적인 교훈을 제공한다.

**기본값(Default)의 위험성**

`requires_authentication=false` 같은 설정이 개발 과정에서 편의를 위해 비활성화된 후 운영 환경으로 그대로 배포되는 문제는 매우 흔하다. OWASP API Security Top 10에서 BOLA가 1위를 차지하는 이유이기도 하다. 모든 새로운 엔드포인트는 기본적으로 인증을 요구해야 하며, 인증 비활성화는 명시적이고 검토된 예외로 처리되어야 한다.

**인증(Authentication)과 인가(Authorization)는 별개다**

이번 취약점은 인증 우회였다. 하지만 인가 체계도 함께 검토되어야 한다. 인증이 통과되더라도 해당 사용자가 요청한 리소스에 접근할 권한이 있는지 객체 수준에서 검증하는 BOLA 방어가 필요하다. 특히 테이블 조회 API는 사용자가 조회 가능한 레코드 범위를 명시적으로 제한해야 한다.

**Scripted REST Resource의 관리 사각지대**

ServiceNow의 Scripted REST Resource 기능은 커스터마이즈 유연성이 높지만, 그만큼 보안 설정 실수가 발생하기 쉬운 영역이다. 특히 시간이 지나면서 목적을 잃은 레거시 엔드포인트나 테스트 목적으로 만들어진 후 방치된 엔드포인트가 취약점이 되는 경우가 많다.

**공시 프로세스의 책임**

벤더가 패치를 먼저 적용하고 공시는 나중에 하는 방식은 공격자에게 패치 분석 기회를 덜 주는 이점이 있다. 하지만 이번처럼 고객 데이터가 이미 침해된 상황에서 게이티드 공시를 택한 것은, 피해 고객들이 자신의 위험 노출 여부를 즉시 파악하고 포렌식 조사를 시작할 권리를 제한한다는 비판이 나온다.

### ServiceNow 고객 조직의 즉각 대응 방안

ServiceNow를 사용 중인 조직이라면 다음 조치를 즉시 취해야 한다.

**Scripted REST Resource 전수 감사:**

```text
1. ServiceNow 관리 콘솔에서
   System Web Services > Scripted REST APIs > Resources 메뉴 접근
2. requires_authentication 컬럼 기준으로 false 설정 항목 필터링
3. 각 항목의 비즈니스 정당성 확인
4. 불필요한 인증 우회 설정 즉시 true로 변경
```

**침해 여부 확인:**

- 2026년 6월 2~3일 기간 API 접근 로그 검토
- `/api/now/related_list_edit/create` 엔드포인트에 대한 접근 이력 중점 확인
- 알려지지 않은 IP에서의 대량 조회 패턴 식별

**ServiceNow 공식 패치 확인:**

ServiceNow 고객 포털에 접속해 6월 5일 이후 패치가 적용됐는지 확인한다. SaaS 플랫폼이라도 패치 적용 타이밍을 확인하는 습관이 필요하다.

**SaaS 보안 태세 점검:**

이번 사건을 계기로 조직이 사용 중인 다른 SaaS 플랫폼의 커스텀 API 및 통합 엔드포인트도 인증 설정을 검토해야 한다. Salesforce, Workday, HubSpot 등 주요 SaaS 플랫폼에서도 유사한 Scripted/Custom API 기능을 제공하며, 동일한 문제가 발생할 수 있다.

## 정리

- ServiceNow의 `/api/now/related_list_edit/create` API 엔드포인트가 `requires_authentication=false`로 설정된 BOLA 결함으로 인해, 6월 2~3일 다수 고객 인스턴스의 IT 티켓, 직원 기록, 내부 문서 등이 무인증 접근으로 노출됐다.
- 패치(6월 5일)와 공시(6월 9일) 사이 4일 공백, 게이티드 어드바이저리 방식이 피해 조직의 신속한 대응을 지연시켰다는 비판을 받고 있다.
- 이번은 ServiceNow에서 8개월 안에 발생한 세 번째 인증 관련 취약점이며, 처음으로 공격자가 패치 이전에 고객 데이터에 도달한 사례다.
- **즉각 조치**: ServiceNow 내 모든 Scripted REST Resource의 `requires_authentication` 설정 전수 감사, 6월 2~3일 API 로그 검토.
- 보안 커뮤니티는 "인증 비활성화는 명시적이고 검토된 예외여야 하며, SaaS 커스텀 API도 내부 API와 동일한 수준의 보안 감사 대상이 되어야 한다"는 공감대를 형성하고 있다.

## Reference

- [ServiceNow Data Breach: Gated Advisory Left Customers Unaware of Exploited Zero-Auth API — TechTimes](https://www.techtimes.com/articles/318166/20260610/servicenow-data-breach-gated-advisory-left-customers-unaware-exploited-zero-auth-api.htm)
- [ServiceNow Flaw Exploited to Gain Unauthorized Access to Customer Instances — The Hacker News](https://thehackernews.com/2026/06/servicenow-flaw-exploited-to-gain.html)
- [ServiceNow discloses security incident exposing customer data — BleepingComputer](https://www.bleepingcomputer.com/news/security/servicenow-discloses-security-incident-exposing-customer-data/)
- [ServiceNow Patches Vulnerability Exploited Against Some Customers — SecurityWeek](https://www.securityweek.com/servicenow-patches-vulnerability-exploited-against-some-customers/)
- [ServiceNow API Security Incident Exposes Customer Data — Rescana](https://www.rescana.com/post/servicenow-api-security-incident-exposes-customer-data-analysis-of-unauthenticated-access-vulnerability-june-2026)
- [ServiceNow Security Incident: Unauthenticated API Access Exposing Customer Data — Triskele Labs](https://www.triskelelabs.com/resources/servicenow-security-incident-unauthenticated-api-access-exposing-customer-data)
- [ServiceNow API Breach: What Customers Need to Know Now — The CyberSec Guru](https://thecybersecguru.com/news/servicenow-api-vulnerability-breach/)
