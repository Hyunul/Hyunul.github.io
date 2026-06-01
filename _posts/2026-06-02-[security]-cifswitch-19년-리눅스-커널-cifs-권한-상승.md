---
title: "[Security] CIFSwitch: 19년 묵은 리눅스 커널 CIFS 취약점, 로컬 루트 권한 탈취 가능"
date: 2026-06-02 07:10:11 +09:00
categories: [Security]
tag: [Linux, CVE, Privilege Escalation, Kernel, CIFS]
---

## 서론

2026년 5월 28일, 보안 연구원 Asim Manizada가 리눅스 커널에서 19년간 존재해온 로컬 권한 상승(LPE, Local Privilege Escalation) 취약점을 공개했다. 이름은 **CIFSwitch**. 별거 아닌 이름처럼 들릴 수 있지만, 이 취약점은 리눅스 커널의 CIFS(Common Internet File System) 서브시스템에 내재된 구조적 결함에서 비롯됐으며, 비권한 로컬 사용자가 루트 권한을 획득할 수 있게 만든다.

취약점이 커널 코드에 처음 도입된 시점은 2007년이다. 이후 19년 동안 코드 리뷰, 보안 감사, 수천 명의 커널 개발자들이 해당 코드를 수정하고 검토했음에도 불구하고, 이 결함은 발견되지 않은 채 살아남았다. 보안 연구 커뮤니티에서 이 취약점이 주목받는 이유가 여기에 있다.

공개 당시 CVE 번호는 아직 공식 발급 전이었다. 일부 출처에서는 CVE-2026-31431로 추적하고 있으며, RedHat의 보안 공지에서도 해당 식별자를 참조하고 있다. PoC(개념 증명 코드) 역시 GitHub에 공개된 상태여서 빠른 패치 적용이 중요한 상황이다.

## 본론

### CIFS와 cifs.spnego가 뭔지부터

CIFSwitch를 이해하려면 먼저 CIFS가 무엇인지 알아야 한다. CIFS는 Common Internet File System의 약자로, Windows가 파일 공유에 사용하는 SMB 프로토콜의 리눅스 구현이다. 리눅스 시스템에서 `mount -t cifs`로 Windows 파일 공유나 NAS 스토리지를 마운트할 때 이 서브시스템이 동작한다.

그 중 `cifs.spnego`는 CIFS 클라이언트가 Kerberos 기반 인증을 수행할 때 사용하는 커널 키(kernel key) 타입이다. SPNEGO는 Simple and Protected GSSAPI Negotiation Mechanism의 약자로, 인증 협상 메커니즘을 추상화하는 프로토콜이다. 커널은 인증 자격증명 처리를 위해 유저스페이스의 `cifs.spnego` 헬퍼 프로그램(`cifs-utils` 패키지에 포함)을 호출한다.

이 구조에서 커널과 유저스페이스 헬퍼 간의 신뢰 관계를 제대로 검증하지 않는 것이 이번 취약점의 핵심이다.

### 취약점의 기술적 원인: 검증 부재

리눅스 커널의 키 관리 서브시스템(keyring)은 `request_key()` 시스템 콜을 통해 특정 키를 요청할 수 있다. 정상적인 흐름에서는 CIFS 클라이언트 코드만이 `cifs.spnego` 타입의 키를 생성해야 한다.

그런데 커널은 `cifs.spnego` 키의 **description(설명 문자열)이 어디서 왔는지를 검증하지 않았다**. 공격자는 이 허점을 이용해 `request_key()` 시스템 콜을 직접 호출하면서 가짜 `cifs.spnego` 키 description을 제공할 수 있다. 이때 커널은 해당 키를 정상적인 CIFS 요청으로 착각하고, 루트 권한으로 동작하는 `cifs.spnego` 유저스페이스 헬퍼를 실행한다.

공격 흐름을 단계별로 정리하면 다음과 같다:

1. 공격자가 사용자 네임스페이스(user namespace)를 생성한다.
2. 사용자 네임스페이스 내에서 `request_key("cifs.spnego", <조작된 description>, ...)` 호출.
3. 커널이 description origin을 검증하지 않아, 실제 CIFS 마운트 요청이 아님에도 `cifs.spnego` 헬퍼를 rootful 컨텍스트로 실행한다.
4. 네임스페이스 경계를 넘어 호스트 루트 권한을 획득한다.

Asim Manizada는 이 과정을 "커널이 유저스페이스 키 description을 아무런 의심 없이 믿는다"는 표현으로 설명했다. 커널 개발 커뮤니티의 업스트림 패치 설명도 이를 확인한다: "smb: client: reject userspace cifs.spnego descriptions"라는 커밋 메시지가 정확히 이 검증 부재를 수정한다는 것을 보여준다.

### 공격 성립 조건

CIFSwitch는 원격 공격이 아닌 **로컬 권한 상승** 취약점이다. 공격이 성립하기 위해서는 다음 조건이 모두 충족되어야 한다:

- **취약한 커널 버전**: 2007년 이후 대부분의 리눅스 커널 버전이 해당된다.
- **취약한 cifs-utils 버전**: `cifs.spnego` 헬퍼가 포함된 cifs-utils 패키지가 설치되어 있어야 한다. SMB/CIFS 마운트를 사용하는 환경에서는 거의 필수적으로 설치된다.
- **사용자 네임스페이스(user namespaces) 활성화**: 대부분의 현대 리눅스 배포판에서 기본적으로 활성화되어 있다.
- **SELinux/AppArmor 비차단**: 특정 SELinux 또는 AppArmor 정책이 해당 공격 경로를 차단하지 않는 경우. 일부 강화된 정책은 이 공격을 부분적으로 방어할 수 있다.

클라우드 환경에서 특히 주의가 필요한 건, 멀티테넌트 환경이나 컨테이너 브레이크아웃 시나리오에서 이 취약점이 조합 공격의 일부로 사용될 수 있기 때문이다. 초기 접근(initial access)을 이미 확보한 공격자가 권한을 루트로 상승시키는 데 활용 가능하다.

### 영향 받는 배포판

BleepingComputer와 SecurityWeek의 보도에 따르면 여러 주요 리눅스 배포판이 영향을 받는다:

- **Ubuntu**: 사용자 네임스페이스가 기본 활성화되어 있어 취약 가능성 높음
- **Debian**: Debian 기반 시스템 전반이 해당됨
- **Rocky Linux / RHEL 계열**: CIQ Knowledge Base에서 Rocky Linux 8, 9, 10에 대한 완화 방법을 공개
- **CloudLinux**: 자체 커널 업데이트와 임시 완화 방법 공지
- **기타 배포판**: cifs-utils와 user namespaces를 기본 활성화한 대부분의 현대 배포판

AppArmor 정책이 강화된 환경(Ubuntu의 일부 hardened 프로필 등)에서는 공격 경로가 부분적으로 차단될 수 있다.

### 패치 정보 및 완화 방법

**공식 업스트림 패치**:
업스트림 리눅스 커널에서 수정 커밋이 이미 반영됐다. 커밋 ID는 `3da1fdf4efbc`이며, 커밋 메시지는 "smb: client: reject userspace cifs.spnego descriptions"다. 이 패치는 유저스페이스에서 생성한 `cifs.spnego` description을 커널이 거부하도록 검증 로직을 추가한다. stable 브랜치 반영도 큰 지연 없이 이루어질 예정이다.

주요 배포판 벤더들은 이미 패치 릴리스를 준비 중이거나 일부는 공지를 완료했다. 각 배포판의 보안 업데이트 채널을 통해 커널 업데이트를 확인하고 즉시 적용하는 것을 권장한다.

**임시 완화 방법**:
즉시 커널 업데이트가 어려운 환경이라면 다음 임시 조치를 고려할 수 있다:

1. **사용자 네임스페이스 비활성화**:
   ```bash
   sysctl -w kernel.unprivileged_userns_clone=0
   ```
   단, 이 설정은 컨테이너 런타임 등 user namespaces에 의존하는 다른 기능에도 영향을 미친다.

2. **cifs-utils 패키지 제거** (CIFS 마운트가 불필요한 경우):
   ```bash
   apt remove cifs-utils  # Debian/Ubuntu
   dnf remove cifs-utils  # RHEL/Rocky
   ```

3. **AppArmor/SELinux 정책 강화**: 특정 정책으로 `request_key()` 호출을 제한하는 방법.

### 19년이 지나도 발견되지 않은 이유

보안 커뮤니티에서 이 취약점이 특히 주목받는 이유 중 하나는 19년이라는 긴 기간 동안 감지되지 않았다는 점이다. CIFS 서브시스템은 수많은 커널 개발자들이 관여해왔고, CVE 데이터베이스에 등록된 커널 취약점만 해도 수천 건에 달한다. 그럼에도 이 결함은 발견되지 않았다.

Asim Manizada의 기술 분석에 따르면, 이 취약점은 커널의 키 서브시스템과 CIFS 서브시스템이 상호작용하는 경계 영역에 위치해 있어, 어느 한 서브시스템만 집중해서 리뷰할 때는 발견하기 어렵다. 두 서브시스템의 신뢰 경계를 동시에 고려하는 시각이 필요한 취약점이라는 것이다.

CloudLinux 보안팀도 이 취약점에 대해 "개별 서브시스템 수준에서는 각각 합리적으로 보이는 코드가, 시스템 전체 관점에서는 취약한 경계를 형성할 수 있다"고 평했다. 이는 대규모 오픈소스 프로젝트에서의 보안 리뷰 방법론에 대한 근본적인 질문을 제기한다.

## 정리

CIFSwitch는 단순한 커널 버그 이상의 시사점을 담고 있다. 19년간 리눅스 커널 코드베이스에서 살아남은 이 취약점은, 복잡한 서브시스템 간 경계에서 발생하는 신뢰 검증 부재가 얼마나 오랫동안 탐지되지 않을 수 있는지를 보여준다.

보안 커뮤니티의 반응은 즉각적이었다. BleepingComputer는 "여러 배포판에 걸쳐 루트 접근을 허용하는 새 리눅스 취약점"이라는 헤드라인으로 보도했고, SecurityWeek는 이 취약점의 조합 공격 가능성을 강조했다. TuxCare는 자사 라이브패치 솔루션을 통한 커널 재부팅 없는 패치 적용 방법을 공지하면서, 특히 운영 중인 서버 환경에서의 빠른 대응을 촉구했다. Rocky Linux 커뮤니티는 CIQ Knowledge Base를 통해 Rocky Linux 8, 9, 10 각 버전별 완화 방법을 상세히 공개했다.

운영 환경을 관리하는 백엔드 엔지니어와 시스템 관리자 입장에서는, 특히 멀티테넌트 환경이나 컨테이너 플랫폼에서의 리스크를 우선적으로 평가할 필요가 있다. 커널 업데이트가 핵심 대응책이며, 즉시 패치가 어려운 환경에서는 위에서 언급한 임시 완화 방법을 적용하는 것이 권장된다.

오래된 코드가 반드시 검증된 안전한 코드를 의미하지는 않는다는 것, 이번 CIFSwitch가 다시 한번 상기시켜준 교훈이다.

## Reference

- [New CIFSwitch Linux flaw gives root on multiple distributions — BleepingComputer](https://www.bleepingcomputer.com/news/security/new-cifswitch-linux-flaw-gives-root-on-multiple-distributions/)
- [19-Year-Old Linux Kernel Vulnerability Exposes Systems to Root Access — SecurityWeek](https://www.securityweek.com/19-year-old-linux-kernel-vulnerability-exposes-systems-to-root-access/amp/)
- [New Linux CIFSwitch Kernel Vulnerability Allows Attackers to Gain Root Access — CybersecurityNews](https://cybersecuritynews.com/linux-cifswitch-kernel-vulnerability/)
- [CIFSwitch Linux Kernel Flaw Grants Local Root on cifs-utils — TuxCare](https://tuxcare.com/blog/cifswitch-cve/)
- [CIFSwitch Mitigation and Kernel Update on CloudLinux — CloudLinux Blog](https://blog.cloudlinux.com/cifswitch-mitigation-and-kernel-update)
- [CVE-2026-31431 — RedHat Security](https://access.redhat.com/security/cve/cve-2026-31431)
- [Mitigating CIFSwitch on Rocky Linux 8, 9, 10 — CIQ Knowledge Base](https://kb.ciq.com/article/rocky-linux/rl-cifswitch-mitigation)
- [CIFSwitch: 19-Year-Old Linux Kernel Privilege Escalation Affects Multiple Distributions — Threat-Modeling.com](https://threat-modeling.com/cifswitch-linux-kernel-privilege-escalation/)
- [CIFSwitch Local Root Exploit: Public Details and PoC Disclosed — SecurityOnline](https://securityonline.info/cifswitch-local-root-exploit-poc/)
