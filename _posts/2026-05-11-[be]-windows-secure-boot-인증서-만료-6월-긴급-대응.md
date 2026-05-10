---
title: "[BE] Windows Secure Boot 인증서 6월 만료 — 서버 운영자가 지금 당장 해야 할 것"
date: 2026-05-11 07:01:23 +09:00
categories: [BE]
tag: [Windows, SecureBoot, UEFI, 인증서, 인프라]
---

## 서론

2026년 6월 26일, Microsoft의 오래된 Secure Boot 인증서 두 종류가 만료된다. **Microsoft Corporation KEK CA 2011**과 **Microsoft UEFI CA 2011** — 이름에서 드러나듯 2011년에 서명된 이 인증서들은 15년 가까이 Windows 부팅 보안의 신뢰 체인을 지탱해 왔다. 여기에 더해 Windows 부트로더를 직접 서명하는 **Microsoft Windows Production PCA 2011**은 2026년 10월에 추가로 만료될 예정이다.

"인증서가 만료되면 시스템이 부팅되지 않는 거 아닌가?"라고 생각하기 쉽지만, 실제로 문제는 더 교묘하다. 만료 이후에도 기존 시스템은 정상 부팅된다. 그러나 **Secure Boot 보안 업데이트를 더 이상 수신하지 못하는** 상태가 된다. 즉, 부팅 체인 수준의 보안 취약점이 발생해도 패치를 적용할 수 없는 구조로 전락하는 것이다. 사실상 Secure Boot 보호막이 서서히 무력화되는 셈이다.

5월 8일 Help Net Security가 공개한 '2026년 5월 Patch Tuesday 전망' 기사는 "5월 12일 Patch Tuesday가 Secure Boot 인증서 만료 전 마지막으로 편안한 배포 창(window)"이라고 명확히 경고했다. 5월 13일부터는 업데이트 미적용 시스템에서 Windows 보안 앱에 노란색 경고 아이콘이 표시되기 시작하고, 만료일이 다가올수록 경고 강도가 높아진다.

이 이슈는 Windows Server를 운영하는 백엔드 엔지니어, DevOps 팀, 인프라 담당자 모두에게 직접적으로 관련된다. 특히 UEFI 부트 설정이 수동으로 관리되는 온프레미스 서버, 오래된 OEM 하드웨어, 또는 UEFI Secure Boot에 의존하는 CI/CD 파이프라인 환경이라면 즉각적인 점검이 필요한 시점이다.

## 본론

### Secure Boot 인증서 체계 이해

Secure Boot는 UEFI 펌웨어 레벨에서 동작하는 부팅 보안 메커니즘이다. 운영체제 로더(bootloader)가 신뢰할 수 있는 키로 서명됐는지를 부팅 시 검증하고, 신뢰하지 않는 키로 서명됐거나 서명이 없는 바이너리의 실행을 차단한다. 이 메커니즘은 부트킷(bootkit), 루트킷(rootkit) 등 OS 로드 이전에 실행되는 악성코드를 막는 마지막 방어선으로 기능한다.

Secure Boot 인증서 체계는 계층 구조로 이뤄진다:

```text
UEFI Firmware (Platform Key, PK)
  └─ KEK (Key Exchange Key)
       ├─ db (허용 서명 데이터베이스)
       │    └─ Windows 부트로더 서명 (Production PCA)
       └─ dbx (차단 서명 데이터베이스 — 취약 부트로더 블랙리스트)
```

이번 만료 대상 인증서들은 이 체계의 핵심을 담당한다:

| 인증서 | 별칭 | 만료일 | 역할 |
|--------|------|--------|------|
| Microsoft Corporation KEK CA 2011 | KEK 2011 | 2026년 6월 26일 | db/dbx 업데이트에 대한 서명 권한 부여 |
| Microsoft UEFI CA 2011 | UEFI CA 2011 | 2026년 6월 26일 | 타사 UEFI 드라이버 및 비Windows OS 검증 |
| Microsoft Windows Production PCA 2011 | PCA 2011 | 2026년 10월 | Windows 부트로더(bootmgr) 직접 서명 |

가장 즉각적인 위협은 **KEK CA 2011 만료**다. KEK가 만료되면 Microsoft는 보안 데이터베이스(db/dbx)를 업데이트하는 서명 권한을 잃는다. 결과적으로 향후 취약한 부트로더가 발견돼도 dbx에 추가 차단 항목을 등록할 수 없게 된다. 이는 2026년 이후 부팅 레벨 취약점에 대한 패치 적용이 불가능해진다는 의미다.

### 인증서 만료 후 실제로 어떤 일이 생기나

Microsoft 공식 문서가 설명하는 만료 시나리오를 정리하면:

**2026년 6월 26일 이후 (업데이트 미적용 시스템):**

1. 신규 2023년판 인증서(UEFI CA 2023, KEK 2023)로 서명된 부트로더나 드라이버를 신뢰하지 못한다.
2. Secure Boot 관련 보안 업데이트(db/dbx 업데이트)를 더 이상 수신하지 못한다.
3. 일부 타사 UEFI 드라이버(예: GPU 펌웨어, NIC 옵션 ROM)가 만료된 UEFI CA 2011에만 의존한 경우, 해당 드라이버 로드에 실패할 수 있다.

**2026년 10월 이후 (PCA 2011 만료 시):**

4. PCA 2011로만 서명된 Windows 부트로더(구버전)는 인증 실패로 부팅 불가 상태가 될 수 있다.

핵심은 "시스템이 갑자기 멈추는 것"이 아니라 "보안 보호막이 서서히 무력화되는 것"이다. 눈에 보이는 장애가 없기 때문에 인지하지 못하는 사이에 취약 상태로 방치될 위험이 있다.

### 영향을 받는 시스템 유형

**온프레미스 Windows Server:**
자동 업데이트를 비활성화한 서버 환경이 가장 위험하다. WSUS(Windows Server Update Services)나 SCCM으로 업데이트를 관리하는 환경이라면, 5월 12일 Patch Tuesday 이후 인증서 업데이트 KB가 포함된 누적 업데이트를 명시적으로 배포해야 한다.

**Linux 듀얼 부팅 및 서버:**
Linux 배포판의 shim 부트로더는 Microsoft UEFI CA 2011을 신뢰 체인으로 사용해 서명된다. UEFI CA 2011이 만료되면, shim이 새 인증서로 서명된 그레인 패키지를 신뢰하지 못하는 상황이 발생할 수 있다. Red Hat은 2026년 2월 "RHEL 환경을 위한 Secure Boot 인증서 변경 가이드"를 별도 발행했으며, Ubuntu도 shim-signed 패키지 업데이트로 대응하고 있다.

**OEM 펌웨어 미업데이트 기기:**
가장 해결이 어려운 케이스다. UEFI DB에 새 인증서(2023년판)를 등록하려면 OEM 펌웨어(BIOS) 업데이트가 필요한데, 일부 구형 하드웨어는 제조사가 펌웨어 업데이트 지원을 이미 종료했다. XDA Developers 보도에 따르면 이런 "구조적으로 수정이 불가능한 기기"가 수백만 대에 이를 것으로 추산된다. 이 경우 Secure Boot를 비활성화하거나 해당 하드웨어를 교체하는 방향으로 계획을 수립해야 한다.

**클라우드/가상화 환경:**
AWS, GCP, Azure의 Windows Server VM은 대부분 하이퍼바이저 레벨에서 UEFI 펌웨어를 관리하므로, 게스트 OS 수준의 Windows Update만으로 충분한 경우가 많다. 단, 커스텀 이미지나 Bring Your Own Image(BYOI)를 사용하는 경우 별도 점검이 필요하다. 또한 vSphere, Hyper-V 환경에서 가상 머신의 UEFI 설정이 구형 인증서를 사용하도록 고정돼 있다면 추가 대응이 요구된다.

### 지금 해야 할 것: 단계별 가이드

**Step 1. 현재 Secure Boot 인증서 상태 확인**

```powershell
# Windows 11 / Server 2022 이상
Confirm-SecureBootUEFI
# 출력: True (활성화됨)

# 인증서 업데이트 상태 확인 (Windows Security 앱)
# → 장치 보안 → 코어 격리 → Secure Boot
# 5월 13일 이후 업데이트 미적용 시 노란 경고 아이콘 표시

# PowerShell로 현재 db 인증서 목록 확인
Get-SecureBootPolicy
```

```bash
# Linux에서 Secure Boot 상태 확인
mokutil --sb-state
# 출력: SecureBoot enabled

# shim 버전 확인 (RHEL/CentOS)
rpm -qi shim-x64

# shim 버전 확인 (Ubuntu/Debian)
dpkg -l shim-signed
```

**Step 2. Windows 업데이트 적용 (5월 12일 Patch Tuesday 이후)**

```powershell
# Windows Update 강제 실행
Install-Module PSWindowsUpdate -Force
Get-WindowsUpdate -AcceptAll -Install

# WSUS 환경에서는 해당 KB 번호를 확인 후 수동 배포
# (5월 12일 Patch Tuesday 릴리스 노트에서 Secure Boot 관련 KB 확인)
```

**Step 3. UEFI 펌웨어 업데이트**

소프트웨어 업데이트만으로는 UEFI DB 업데이트가 적용되지 않는 경우도 있다. 하드웨어 제조사별 BIOS/UEFI 업데이트 방법:

```text
Dell: Dell Command | Update 또는 Dell SupportAssist 사용
      support.dell.com → 제품 번호로 최신 BIOS 버전 확인

HP: HP Support Assistant
    support.hp.com → 제품 시리얼로 펌웨어 업데이트 확인

Lenovo: Lenovo System Update
        support.lenovo.com → BIOS 업데이트 다운로드

Supermicro (서버): sum (Supermicro Update Manager)
                   또는 BMC 웹 인터페이스를 통한 BIOS 업데이트
```

**Step 4. BitLocker 사용 환경 사전 준비**

UEFI 펌웨어 업데이트는 TPM 측정값을 변경시켜 BitLocker 잠금을 유발할 수 있다. 펌웨어 업데이트 전 반드시:

```powershell
# BitLocker 복구 키 확인 및 백업
manage-bde -protectors -get C:

# 복구 키를 Microsoft 계정 또는 AD에 백업
# manage-bde -protectors -adbackup C: -id {GUID}

# 일시적으로 BitLocker 자동 잠금 해제 설정
# (서버 재부팅 없이 펌웨어 업데이트가 가능한 경우 생략 가능)
```

**Step 5. Linux (RHEL/Ubuntu) 환경 업데이트**

```bash
# RHEL 계열: shim 패키지 업데이트
sudo dnf update shim shim-x64 grub2-efi-x64

# Ubuntu/Debian 계열: shim-signed 업데이트
sudo apt update && sudo apt upgrade shim-signed grub-efi-amd64-signed

# 업데이트 후 grub 설정 갱신
sudo grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg  # RHEL
sudo update-grub                                         # Ubuntu
```

### 5월 12일 Patch Tuesday가 특별한 이유

Help Net Security, Zecurit 등 보안 미디어가 5월 12일 Patch Tuesday를 "마지막으로 편안한 배포 창"으로 지목한 데는 이유가 있다. 이 업데이트에는 새로운 Secure Boot 인증서(2023년판 UEFI CA, KEK)를 UEFI 신뢰 데이터베이스에 등록하는 DB 업데이트가 포함될 것으로 예상된다.

이 업데이트를 적용하면 기기의 UEFI DB에 신규 인증서가 등록되고, 만료 이후에도 새로운 보안 업데이트를 계속 수신할 수 있는 상태가 유지된다. 반대로 이 기회를 놓치면:

- 6월 26일 이후 Secure Boot 보안 업데이트 누적 미적용 상태 지속
- 7월 이후 별도 적용 시 UEFI 펌웨어 레벨에서 호환성 문제 발생 가능
- 일부 기기에서는 별도 패치 없이 Secure Boot 유지를 위한 설정 변경이 매우 복잡해질 수 있음

Microsoft TechCommunity 블로그는 5월 Patch Tuesday를 "가장 중요한 단일 보안 업데이트 배포 기회 중 하나"라고 표현했다.

### 인프라 담당자를 위한 체크리스트

```text
□ Windows Server: 5월 12일 Patch Tuesday 누적 업데이트 적용 완료 확인
□ OEM 펌웨어: 제조사 사이트에서 최신 BIOS/UEFI 버전 확인 및 업데이트
□ 구형 하드웨어: 펌웨어 업데이트 지원 여부 확인, 미지원 시 교체 계획 수립
□ BitLocker 환경: 펌웨어 업데이트 전 복구 키 사전 백업 필수
□ Linux 듀얼 부팅: shim-signed / grub2-efi 최신 버전 업데이트
□ 클라우드 VM: 커스텀 이미지 사용 시 UEFI 설정 별도 점검
□ vSphere/Hyper-V: VM UEFI 템플릿에 구형 인증서 강제 설정 여부 확인
□ CI/CD 파이프라인: Secure Boot 검증이 포함된 빌드 스크립트 점검
```

## 정리

- **Microsoft Corporation KEK CA 2011**, **Microsoft UEFI CA 2011**이 **2026년 6월 26일** 만료된다. **Windows Production PCA 2011**은 **2026년 10월** 추가 만료 예정이다.
- 만료 이후 시스템이 갑자기 부팅 불가 상태가 되는 것은 아니지만, 향후 Secure Boot 보안 업데이트를 받지 못해 부팅 체인 보호막이 사실상 무력화된다.
- **2026년 5월 12일 Patch Tuesday**에 인증서 교체 업데이트가 포함될 예정이며, 이것이 만료 전 마지막으로 편안한 배포 창이다.
- 5월 13일부터 업데이트 미적용 시스템의 Windows 보안 앱에 노란 경고 아이콘이 표시되기 시작한다.
- 구형 OEM 하드웨어는 펌웨어 업데이트 제공이 종료됐을 경우 영구적으로 취약한 상태가 될 수 있어 교체 계획 수립이 필요하다.
- BitLocker 사용 환경은 UEFI 펌웨어 업데이트 전 복구 키 백업이 필수다.
- Windows Server, Linux 서버(shim 업데이트), 클라우드 VM, CI/CD 파이프라인 등 UEFI Secure Boot를 사용하는 모든 인프라를 즉시 점검해야 한다.

## Reference

- [Act now: Secure Boot certificates expire in June 2026 — Microsoft TechCommunity](https://techcommunity.microsoft.com/blog/windows-itpro-blog/act-now-secure-boot-certificates-expire-in-june-2026/4426856)
- [Windows Secure Boot certificate expiration and CA updates — Microsoft Support](https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e)
- [Secure Boot playbook for certificates expiring in 2026 — Microsoft TechCommunity](https://techcommunity.microsoft.com/blog/windows-itpro-blog/secure-boot-playbook-for-certificates-expiring-in-2026/4469235)
- [May 2026 Patch Tuesday forecast: AI starts driving security industry changes — Help Net Security (2026.05.08)](https://www.helpnetsecurity.com/2026/05/08/may-2026-patch-tuesday-forecast/)
- [Microsoft's Secure Boot certificates expire in June 2026, but older PCs may never get the fix — XDA Developers](https://www.xda-developers.com/microsoft-secure-boot-certificates-expire-june-2026-older-pcs/)
- [Secure Boot Certificate Changes in 2026: Guidance for RHEL Environments — Red Hat Customer Portal](https://access.redhat.com/articles/7128933)
- [Secure Boot certificate changes in 2026: Guidance for RHEL environments — Red Hat Developer](https://developers.redhat.com/articles/2026/02/04/secure-boot-certificate-changes-2026-guidance-rhel-environments)
- [Secure Boot Transition FAQ — Dell US](https://www.dell.com/support/kbdoc/en-us/000390990/secure-boot-transition-faq)
- [Patch Tuesday May 2026: Security Updates & CVE Analysis — Zecurit](https://zecurit.com/endpoint-management/patch-tuesday/)
