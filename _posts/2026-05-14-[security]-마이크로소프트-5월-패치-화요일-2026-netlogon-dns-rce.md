---
title: "[Security] 마이크로소프트 5월 패치 화요일 — Netlogon 워머블 RCE와 DNS 취약점 긴급 패치"
date: 2026-05-14 09:00:00 +09:00
categories: [Security]
tag: [Patch Tuesday, CVE, Windows, RCE, Netlogon]
---

## 서론

2026년 5월 13일, 마이크로소프트가 정례 보안 업데이트인 패치 화요일(Patch Tuesday)을 공개했다. 이번 달 패치에는 100개가 넘는 취약점에 대한 수정이 담겼으며, 그중 가장 주목을 받은 건 **Windows Netlogon 서비스의 원격 코드 실행 취약점(CVE-2026-41089)**이다. CVSS 점수 9.8의 이 결함은 워머블(wormable), 즉 자기 전파가 가능한 성격으로, 보안 연구기관 Zero Day Initiative(ZDI)가 "패치 우선순위 1위"로 꼽을 정도다.

특이한 점은 이번 릴리스에 제로데이 취약점이 포함되지 않았다는 것이다. SC Media는 이를 "2024년 6월 이후 처음"이라고 보도했다. 하지만 제로데이 부재가 "이번 패치 화요일은 안심해도 된다"는 신호가 될 수는 없다. CVE-2026-41089 하나만으로도 기업 도메인 인프라 전체를 장악할 수 있는 수준이기 때문이다.

Netlogon은 Windows 도메인 환경의 인증 심장부 역할을 한다. 과거 ZeroLogon(CVE-2020-1472)이 도메인 컨트롤러를 순식간에 장악할 수 있게 했던 것처럼, CVE-2026-41089 역시 도메인 컨트롤러를 직접 겨냥한 공격이다. 차이점은 ZeroLogon이 인증 프로토콜 결함이었다면, CVE-2026-41089는 스택 버퍼 오버플로우를 통한 원격 코드 실행이라는 점이다. 공격 난이도는 오히려 더 낮을 수 있다는 분석도 나온다.

이번 포스트에서는 5월 패치 화요일의 전체적인 구성과 핵심 취약점들을 정리하고, 실무에서 어떤 순서로 대응해야 하는지 살펴본다.

---

## 본론

### 2026년 5월 패치 화요일 전체 구성

마이크로소프트는 2026년 5월 13일 기준으로 약 120개 이상의 보안 취약점에 대한 수정 패치를 배포했다. 집계 방식에 따라 소스별로 118개(Tenable)부터 138개(The Hacker News, Vulert)까지 다소 차이가 있는데, 이는 Windows 전용 CVE만 카운트하는지, Microsoft 전 제품 CVE를 포함하는지에 따른 차이다.

중요도별 분류:

| 심각도 | 수량 |
|---|---|
| Critical (심각) | 14~16개 |
| Important (중요) | 100개 이상 |
| 제로데이 (0-day) | **0건** |

보안 분석 기관들은 특히 13개 이상의 CVE가 "실제 익스플로잇 가능성이 높음(Exploitation More Likely)"으로 분류됐다는 점에 주목한다. 제로데이는 없어도 현실적인 위협이 된다는 뜻이다.

---

### CVE-2026-41089: Windows Netlogon 워머블 원격 코드 실행

이번 패치에서 단연 최우선 대응 대상이다.

| 항목 | 상세 |
|---|---|
| CVE ID | CVE-2026-41089 |
| CVSS v3 점수 | **9.8 (Critical)** |
| 취약점 유형 | CWE-121: 스택 기반 버퍼 오버플로우 |
| 영향 대상 | Windows Server 2012 이상 모든 버전 |
| 공격 벡터 | 네트워크 (Network) |
| 인증 요구 | **없음** (Unauthenticated) |
| 사용자 상호작용 | **없음** (None) |
| 공격 복잡도 | **낮음** (Low) |
| 익스플로잇 성공 시 | SYSTEM 권한으로 도메인 컨트롤러 전체 장악 |

**기술적 메커니즘**

Netlogon은 Windows Server 도메인 환경에서 클라이언트-서버 인증을 처리하는 핵심 서비스다. CVE-2026-41089는 이 서비스 내부의 스택 기반 버퍼 오버플로우(CWE-121) 취약점으로, 공격자가 특수하게 조작된 네트워크 요청을 도메인 컨트롤러(DC)로 전송하면 Netlogon 서비스가 해당 요청을 잘못 처리하면서 임의 코드를 실행할 수 있게 된다.

공격에는 사전 인증도, 사용자의 어떤 행동도 필요하지 않다. 네트워크 접근만 있으면 된다. 익스플로잇에 성공하면 SYSTEM 권한으로 코드가 실행되는데, 도메인 컨트롤러에서의 SYSTEM은 곧 해당 도메인 전체를 제어하는 것과 다름없다. 도메인 관리자 계정 탈취, 그룹 정책 변경, 도메인 내 모든 서버 접근이 가능해진다.

**왜 워머블(Wormable)인가?**

ZDI는 CVE-2026-41089를 워머블로 분류했다. 워머블이란 단일 취약점 익스플로잇에서 시작해, 감염된 시스템이 동일 네트워크 내 다른 취약한 시스템을 자동으로 공격해 전파되는 성질을 말한다.

워머블 조건:
- 인증 불필요 → 자동화된 스캔/공격 가능
- 사용자 상호작용 불필요 → 사람이 개입 없이 전파
- 네트워크 공격 벡터 → 같은 네트워크 내 자동 전파 가능
- 낮은 공격 복잡도 → 공격 코드 작성이 상대적으로 쉬움

이 네 가지 조건이 겹치면 EternalBlue(WannaCry)나 ZeroLogon처럼 빠르게 무기화될 수 있다. Rapid7과 Tenable 모두 "모든 도메인 컨트롤러를 같은 유지보수 창 안에서 즉시 패치"할 것을 권고했다.

현재(2026년 5월 14일 기준)까지 실제 익스플로잇은 보고되지 않았지만, 개념 증명 코드(PoC)가 공개되면 악용 시도가 급격히 늘어날 가능성이 높다.

---

### CVE-2026-41096: Windows DNS 클라이언트 원격 코드 실행

두 번째로 주목해야 할 취약점이다.

| 항목 | 상세 |
|---|---|
| CVE ID | CVE-2026-41096 |
| CVSS v3 점수 | **9.8 (Critical)** |
| 취약점 유형 | 힙 기반 버퍼 오버플로우 (Heap Buffer Overflow) |
| 영향 대상 | Windows DNS 클라이언트 탑재 시스템 전반 |
| 공격 벡터 | 네트워크 |

Windows DNS 클라이언트는 사실상 모든 Windows 시스템에 탑재돼 있어 영향 범위가 CVE-2026-41089보다 오히려 더 넓다. 힙 기반 버퍼 오버플로우로, DNS 응답 처리 과정에서 조작된 응답을 통해 코드 실행으로 이어질 수 있다는 분석이 지배적이다.

DNS는 443/80 포트 외에 UDP 53 포트로도 동작하기 때문에, 일반적인 웹 방화벽만으로는 충분한 보호가 되지 않는다. 특히 내부 DNS 서버로 연결되는 사설 네트워크 구간에서도 취약하다. 단순히 "인터넷에서 들어오는 공격"이 아니라, 공격자가 네트워크에 이미 진입한 이후 내부 전파 수단으로 활용할 가능성도 있다.

---

### CVE-2026-41103: Microsoft SSO 플러그인 인증 우회

이번 패치에서 Tenable이 제목에 특별히 언급한 취약점이다.

| 항목 | 상세 |
|---|---|
| CVE ID | CVE-2026-41103 |
| CVSS v3 점수 | **9.1 (Critical)** |
| 영향 대상 | Jira·Confluence용 Microsoft SSO 플러그인 |
| 공격 특성 | 로그인 과정 중 조작된 응답을 통한 신원 위조 |

Atlassian Jira 또는 Confluence를 Microsoft Entra ID(구 Azure AD)와 연동해 SSO로 사용하는 조직이 대상이다. 공격자는 로그인 흐름 중에 특수하게 조작된 응답 메시지를 보내 Entra ID 인증 없이 임의의 신원으로 로그인할 수 있다. 성공 시 해당 Jira 프로젝트나 Confluence 스페이스 내 데이터 조회 및 수정이 가능해진다.

개발 협업 플랫폼에서의 신원 위조는 소스코드, 이슈 트래커, 내부 문서에 대한 비인가 접근으로 이어질 수 있어, 개발 조직에게는 특히 심각한 위협이다.

---

### 대응 우선순위와 패치 방법

**패치 적용 순서 권고**

1. **즉시(1순위)**: 모든 **도메인 컨트롤러** — CVE-2026-41089 패치, 동일한 유지보수 창 내 전수 적용
2. **긴급(2순위)**: 모든 **Windows 서버·클라이언트** — CVE-2026-41096 패치
3. **우선(3순위)**: Jira/Confluence SSO 연동 조직 — Microsoft SSO 플러그인 업데이트 (CVE-2026-41103)

**Windows Update를 통한 패치 배포 확인**

```powershell
# 현재 설치된 보안 업데이트 목록 확인
Get-HotFix | Where-Object {$_.InstalledOn -gt (Get-Date).AddDays(-7)} | Sort-Object InstalledOn -Descending

# Windows Update 강제 확인 (PSWindowsUpdate 모듈 필요)
Install-Module PSWindowsUpdate -Force
Get-WindowsUpdate -AcceptAll -Install

# WSUS 환경: WSUS 관리 콘솔에서 2026년 5월 Cumulative Update 승인 후 배포
```

**임시 완화 방안 (CVE-2026-41089 패치 전)**

마이크로소프트는 공식 워크어라운드를 제시하지 않았다. 하지만 현실적인 완화 조치로:

```text
1. 도메인 컨트롤러로의 불필요한 외부 접근 차단
   - TCP 135 (RPC Endpoint Mapper)
   - 동적 RPC 포트 범위 (49152~65535) 외부 차단

2. 이벤트 로그 모니터링 강화
   - Event ID 5722: Netlogon 세션 설정 실패
   - Event ID 5723: Netlogon 세션 설정 실패 (도메인 컨트롤러)
   - 비정상적인 빈도의 Netlogon 인증 요청 이상 탐지

3. 네트워크 세그멘테이션 확인
   - DC는 별도 VLAN에 격리, 불필요한 호스트의 접근 차단
```

---

### 보안 커뮤니티 반응

ZDI는 CVE-2026-41089에 대해 "EternalBlue 이후 도메인 컨트롤러에 가장 위험한 단일 취약점 후보 중 하나"라는 평가를 남겼다. Rapid7의 분석에서도 "DoD(Domain of Destruction) 시나리오"를 언급하며 즉각적인 대응을 촉구했다.

Krebs on Security는 이번 패치 화요일에 대해 "제로데이 없음이라는 헤드라인에 속아 Netlogon 패치를 미루면 안 된다"고 경고했다. 보안 실무진 사이에서는 "PoC가 나오기 전에 패치를 완료해야 한다"는 공통된 목소리가 이어지고 있다.

---

## 정리

- **2026년 5월 패치 화요일(5월 13일 배포)**: 120개 이상 CVE 수정, 제로데이 없음
- **CVE-2026-41089(Netlogon RCE, CVSS 9.8)**: 스택 버퍼 오버플로우, 워머블, 인증 불필요, 도메인 컨트롤러 전체 제어 가능 — 즉시 패치 필요
- **CVE-2026-41096(DNS 클라이언트 RCE, CVSS 9.8)**: 힙 버퍼 오버플로우, 모든 Windows 시스템이 영향권
- **CVE-2026-41103(SSO 플러그인, CVSS 9.1)**: Jira/Confluence SSO 연동 조직 대상, 신원 위조 통한 무인가 접근
- ZDI, Rapid7, Tenable 등 주요 보안 기관 모두 CVE-2026-41089 도메인 컨트롤러 즉시 패치를 최우선 권고
- 제로데이 부재는 안도 신호가 아님 — CVSS 9.8 워머블 RCE는 PoC 공개 이후 무기화 속도가 빠름

## Reference

- [Microsoft Patches 138 Vulnerabilities, Including DNS and Netlogon RCE Flaws — The Hacker News](https://thehackernews.com/2026/05/microsoft-patches-138-vulnerabilities.html)
- [138 CVEs Fixed: Netlogon RCE Leads Microsoft's Patch Pack — Vulert](https://vulert.com/blog/microsoft-patch-tuesday-may-2026-dns-netlogon-rce/)
- [Patch Tuesday: No zero days among 137 Microsoft CVEs, 4 Word RCEs — SC Media](https://www.scworld.com/news/patch-tuesday-no-zero-days-among-137-microsoft-cves-4-word-rces)
- [The May 2026 Security Update Review — Zero Day Initiative](https://www.zerodayinitiative.com/blog/2026/5/12/the-may-2026-security-update-review)
- [Microsoft's May 2026 Patch Tuesday Addresses 118 CVEs — Tenable](https://www.tenable.com/blog/microsofts-may-2026-patch-tuesday-addresses-118-cves-cve-2026-41103)
- [Patch Tuesday — May 2026 — Rapid7](https://www.rapid7.com/blog/post/em-patch-tuesday-may-2026/)
- [Patch Tuesday, May 2026 Edition — Krebs on Security](https://krebsonsecurity.com/2026/05/patch-tuesday-may-2026-edition/)
