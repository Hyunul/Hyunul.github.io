---
title: "[BE] TrapDoor 공급망 공격 — npm·PyPI·Crates.io에서 AWS 자격증명 대규모 탈취"
date: 2026-06-01 07:09:00 +09:00
categories: [BE]
tag: [공급망공격, npm, PyPI, DevSecOps, 클라우드보안]
---

## 서론

2026년 5월 마지막 주, 백엔드·DevOps 개발자라면 반드시 알아야 할 공급망 공격 두 건이 거의 동시에 보고됐다.

첫 번째는 **TrapDoor** 캠페인이다. The Hacker News 보도(5월 29일 기준)에 따르면, 이 캠페인은 npm, PyPI, Crates.io 세 패키지 레지스트리에 걸쳐 34개 이상의 악성 패키지와 384개 이상의 버전을 배포했다. 2026년 5월 22일부터 활성화된 것으로 추정되며, **개발자 시크릿, SSH 키, 클라우드 자격증명, CI/CD 토큰, 암호화폐 지갑 키** 등을 탈취 대상으로 삼는다.

두 번째는 Microsoft Security Research가 5월 28일 공개한 **타이포스쿼팅 npm 패키지** 사건이다. 위협 행위자 `vpmdhaj`는 단 4시간 만에 14개의 악성 npm 패키지를 올렸다. 대상은 OpenSearch, Elasticsearch, DevOps·환경변수 설정 관련 라이브러리를 사칭하는 형태였으며, AWS 자격증명과 HashiCorp Vault 토큰, GitHub Actions 시크릿을 목표로 했다.

두 공격 모두 클라우드 환경에서 작업하는 백엔드·인프라 팀의 개발 머신을 직접 겨냥했다. `npm install` 한 번이 프로덕션 AWS 계정을 통째로 넘길 수 있는 상황이다.

## 본론

### TrapDoor 캠페인 전체 구조

| 항목 | 내용 |
|---|---|
| 캠페인명 | TrapDoor |
| 최초 활동 | 2026-05-22 (추정) |
| 영향 레지스트리 | npm, PyPI, Crates.io |
| 악성 패키지 수 | 34개 이상 |
| 악성 버전 수 | 384개 이상 |
| 주요 탈취 대상 | 개발자 시크릿, 암호화폐 지갑 키, SSH 키, 클라우드 자격증명, CI/CD 파이프라인 토큰, 브라우저 저장 자격증명, 환경변수 |

TrapDoor의 특징은 **단일 레지스트리가 아닌 세 개 생태계를 동시에 표적**으로 삼는다는 점이다. npm은 Node.js·프런트엔드·백엔드 서버사이드 JavaScript 생태계, PyPI는 Python 기반 데이터·백엔드·자동화 생태계, Crates.io는 Rust 기반 시스템·인프라 생태계를 대표한다. 사용하는 언어가 무엇이든 감염 위험이 존재한다는 의미다.

탈취 대상의 범위도 넓다. 클라우드 자격증명에 그치지 않고 암호화폐 지갑 키, SSH 키, 브라우저 저장 비밀번호까지 수집한다. 개발 머신 하나를 감염시키는 것으로 공격자가 확보할 수 있는 정보의 가치가 상당히 크다.

### 타이포스쿼팅 npm 공격 상세 분석 (Microsoft Security Research)

Microsoft Security Blog(2026-05-28)에 따르면, 위협 행위자 `vpmdhaj`가 게시한 14개의 악성 npm 패키지는 다음 유형의 라이브러리를 사칭했다.

- OpenSearch 클라이언트 관련 패키지
- Elasticsearch 클라이언트 관련 패키지
- 환경변수·DevOps 설정 관련 패키지
- 클라우드 프로비저닝 도구 관련 패키지

**기술적 공격 구조 — 2단계 페이로드**

```json
// 악성 package.json의 scripts 섹션 (개념적 예시)
{
  "name": "opensearch-sdk",
  "version": "1.2.1",
  "scripts": {
    "postinstall": "node ./dist/setup.js"
  }
}
```

`npm install` 시 실행되는 lifecycle 훅(`postinstall`)을 통해 스테이저가 즉시 실행된다. Microsoft Security Research는 두 가지 변형을 관측했다.

**1세대 스테이저:** HTTP C&C 서버에 비콘을 보낸 뒤 2단계 페이로드를 다운로드해 실행한다.

**2세대 스테이저(고도화):** Bun 런타임으로 컴파일된 약 195KB 크기의 크리덴셜 하베스터를 패키지 내부에 직접 포함한다. 외부 C&C 통신이 없어 네트워크 레벨 탐지를 회피한다.

```text
[2세대 공격 흐름]

npm install <악성패키지>
    └→ postinstall 훅 실행
         └→ Bun 컴파일 바이너리 로드
              ├→ AWS IMDS 엔드포인트 접근 (임시 자격증명 수집)
              ├→ AWS Secrets Manager (16개+ 리전 순회)
              ├→ HashiCorp Vault 토큰 환경변수 스캔
              ├→ ~/.aws/credentials 파일 읽기
              ├→ GITHUB_TOKEN, NPM_TOKEN 등 CI/CD 시크릿 수집
              └→ 수집 데이터 외부 엔드포인트 전송 (암호화)
```

**npm publish 토큰 탈취의 위험성**

이 공격 구조에서 가장 위험한 부분은 `npm publish` 토큰의 탈취다. 공격자가 이 토큰을 확보하면:

1. 피해자의 npm 계정으로 기존에 배포한 **정상 패키지**에 악성 버전을 배포할 수 있다.
2. 해당 정상 패키지를 사용하는 모든 다운스트림 개발자·서비스가 2차 피해자가 된다.

피해자가 동시에 가해자가 되는 구조다. Microsoft Security Research는 이미 일부 피해 계정의 정상 패키지에 악성 버전이 배포 시도된 흔적을 확인했다고 밝혔다.

### Sicoob.Sdk — NuGet 생태계에서의 금융 자격증명 탈취

같은 위협 행위자(`vpmdhaj`)는 NuGet 레지스트리에도 악성 패키지를 배포했다. **Sicoob.Sdk**(v2.0.0~v2.0.4)는 브라질 협동 금융 네트워크 Sicoob의 공식 C# SDK처럼 위장했다.

```csharp
// 정상 SDK처럼 보이는 생성자 호출 예시
// 실제로는 내부에서 자격증명 탈취가 발생

var client = new SicoobClient(
    clientId: "my-business-client-id",
    pfxPath: "/path/to/certificate.pfx",
    pfxPassword: "my-pfx-password"
);
```

`SicoobClient`가 인스턴스화되는 순간, 내부 악성 코드가 PFX 파일을 읽어 Base64로 인코딩한 뒤 클라이언트 ID, PFX 비밀번호, 인증서 데이터를 하드코딩된 서드파티 Sentry 엔드포인트로 전송한다. 소스 저장소에는 이 악성 코드가 없었으며, 빌드·배포 단계에서 삽입됐다 — **소스-패키지 불일치(Source-to-Package Mismatch)** 공격 기법이다.

PFX 인증서는 Sicoob 금융망 API에서 사업자 인증에 사용된다. 탈취되면 Pix 즉시 결제 자동화, 동적 QR 코드 생성 등 결제 관련 기능을 공격자가 직접 제어할 수 있게 돼 직접적인 금전 피해로 이어진다.

cybersecuritynews.com에 따르면 이 사건의 피해가 확산된 데는 **Google Search AI Mode가 Sicoob.Sdk를 합법적인 공식 C# 라이브러리로 추천**했다는 배경이 있다. 검색 AI가 악성 패키지를 정상 라이브러리로 소개한 셈이다. 검색 AI의 추천이 오히려 공격 면적을 넓히는 새로운 벡터가 된 사례다.

### 방어 체크리스트

이번 사건들에서 반복적으로 드러난 공격 패턴을 기반으로 한 실천 체크리스트:

**[1] 즉시 점검 사항 (이번 사건 관련)**

```bash
# npm 의존성에서 의심 패키지 확인
# opensearch-*, elasticsearch-* 계열 중 공식 패키지가 아닌 것 확인
npm ls | grep opensearch
npm ls | grep elasticsearch

# NuGet에서 Sicoob.Sdk 사용 여부 확인
dotnet list package | grep -i sicoob
```

**[2] npm 공급망 보안 일반 강화**

```bash
# 패키지 설치 시 postinstall 훅 실행 차단 (신중하게 적용, 일부 패키지 동작에 영향)
npm install --ignore-scripts

# 패키지 소유자 확인
npm info <패키지명> maintainers

# npm audit으로 알려진 취약점 확인
npm audit

# package-lock.json 또는 yarn.lock을 항상 커밋하고 변경 시 리뷰
```

**[3] CI/CD 파이프라인 시크릿 보호**

```yaml
# GitHub Actions: 시크릿 최소 권한 원칙
permissions:
  contents: read        # 필요한 권한만
  packages: write       # 실제 필요한 것만 남기기

# AWS IAM Role for Service Accounts 사용 권고
# 장기 자격증명(Access Key ID/Secret) 대신 임시 자격증명만 사용
```

**[4] 개발 환경 격리**

- 패키지 개발·테스트에 프로덕션 AWS 자격증명을 사용하지 않는다.
- `~/.aws/credentials`에는 최소 권한 개발 전용 프로파일만 설정한다.
- 개발 머신에서 CI/CD 시크릿에 직접 접근하는 패턴을 제거한다.

### 업계의 반응

Microsoft Security Research는 "이번 공격은 단순한 타이포스쿼팅을 넘어, npm publish 토큰을 탈취해 정상 패키지에 백도어를 심는 2단계 공급망 공격 구조를 가진다"고 분석했다. 또한 Bun 컴파일 바이너리를 사용한 페이로드는 기존의 JavaScript 기반 악성 코드 탐지 도구로는 정적 분석이 어렵다는 점도 지적했다.

The Hacker News는 TrapDoor 캠페인을 "npm, PyPI, Crates.io를 동시에 표적으로 삼는 다중 레지스트리 공격으로, 특정 언어 생태계를 넘어 전체 개발 툴체인을 겨냥하고 있다"고 평가했다.

오픈소스 보안 커뮤니티에서는 패키지 레지스트리의 신뢰 모델에 대한 근본적인 논의가 다시 불거지고 있다. npm, PyPI 모두 자동화된 악성 패키지 탐지 시스템을 운영하지만, 소스-패키지 불일치 공격이나 Google AI 추천을 악용하는 방식에는 기술적 방어만으로는 한계가 있다는 지적이 나온다.

socket.dev(패키지 보안 분석 서비스)와 같이 패키지의 실제 동작을 샌드박스에서 분석하는 도구의 필요성이 재조명되고 있다. 패키지를 설치하기 전 동적 분석 결과를 확인하는 방어선을 추가하는 것이 향후 표준 관행이 될 것이라는 전망도 나온다.

## 정리

- TrapDoor 캠페인(5월 22일~)이 npm·PyPI·Crates.io에서 34개 이상의 악성 패키지로 AWS 자격증명, SSH 키, CI/CD 토큰 등을 탈취하고 있다.
- Microsoft Security Blog(5월 28일)는 타이포스쿼팅 npm 14개 패키지를 추가 공개했다 — OpenSearch/Elasticsearch 사칭, Bun 컴파일 크리덴셜 하베스터 사용.
- npm publish 토큰 탈취로 정상 패키지에 백도어 삽입이 가능한 2단계 구조여서 위험도가 특히 높다.
- NuGet Sicoob.Sdk는 .NET 개발자 대상 PFX 인증서 탈취로 금융 결제 직접 피해로 이어질 수 있으며, Google AI가 합법 라이브러리로 추천해 노출을 확대했다.
- `npm install --ignore-scripts` 적용, 패키지 소유자 확인, CI/CD 시크릿 최소 권한 원칙을 즉시 실천해야 한다.
- 개발 머신에 프로덕션 AWS 자격증명과 CI/CD 토큰을 함께 두는 관행을 반드시 재검토해야 한다.

## Reference

- [The Hacker News — TrapDoor Supply Chain Attack Spreads Credential-Stealing Malware via npm, PyPI, and CratesIO](https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html)
- [Microsoft Security Blog — Typosquatted npm packages used to steal cloud and CI/CD secrets](https://www.microsoft.com/en-us/security/blog/2026/05/28/typosquatted-npm-packages-used-steal-cloud-ci-cd-secrets/)
- [The Hacker News — Malicious Sicoob NuGet Steals Banking Credentials as npm Packages Target Cloud Secrets](https://thehackernews.com/2026/05/malicious-sicoob-nuget-steals-banking.html)
- [cybersecuritynews.com — Typosquatted npm Packages Steal Cloud and CI/CD Secrets From Developer Systems](https://cybersecuritynews.com/typosquatted-npm-packages-steal-cloud-and-ci-cd-secrets/)
- [socket.dev — Malicious NuGet Package Impersonates Sicoob SDK](https://socket.dev/blog/malicious-nuget-package-impersonates-sicoob-sdk)
