---
title: "[BE] Apache HTTP Server 2.4.67 긴급 패치: HTTP/2 RCE와 AJP 메모리 취약점"
date: 2026-05-05 07:06:28 +09:00
categories: [BE]
tag: [Apache, HTTP2, CVE, 웹서버, AJP, 보안패치]
---

## 서론

2026년 5월 4일, Apache HTTP Server 프로젝트가 버전 **2.4.67**을 출시했다. 이번 릴리스는 단순한 기능 추가가 아니라 HTTP/2 프로토콜에서 원격 코드 실행(Remote Code Execution, RCE)이 가능한 치명적인 취약점과 `mod_proxy_ajp`의 다수 메모리 안전성 결함을 포함한 보안 긴급 패치다. Apache 공식 보안 페이지와 linuxcompatible.org, warp2search.net 등이 동시에 릴리스 소식을 전했다.

Apache HTTP Server는 전 세계 웹 서버 시장에서 여전히 상당한 점유율을 유지하고 있으며, 특히 **Java 백엔드 스택(Spring Boot, Tomcat, JBoss)**과 AJP(Apache JServ Protocol) 프로토콜로 연동되어 리버스 프록시 역할을 하는 레거시 구성에서 많이 사용된다. 이번 패치에서 수정된 `mod_proxy_ajp` 취약점은 악성 또는 침해된 AJP 백엔드 서버가 Apache에 특수 메시지를 보내 힙 버퍼 오버플로를 유발할 수 있어, Tomcat·JBoss와 연결된 환경에서도 주의가 필요하다.

단순히 "Apache 설치된 서버"만의 이야기가 아니다. Spring Boot를 Apache 앞에 두는 구성, 또는 외부 Apache가 내부 WAS(Web Application Server)와 AJP로 통신하는 전통적인 Java 배포 환경이라면 이번 패치를 반드시 검토해야 한다.

## 본론

### CVE-2026-23918: HTTP/2 이중 해제(Double Free) → RCE 가능

가장 위험도가 높은 취약점은 **CVE-2026-23918**으로, HTTP/2 프로토콜 처리 과정에서 발생하는 이중 해제(Double Free) 버그다. 클라이언트가 HTTP/2 이른 리셋 프레임(early reset frame)을 높은 부하 상태에서 전송할 때 이 버그가 트리거되며, 이론적으로 원격 코드 실행이 가능하다.

공식 Apache 보안 페이지에 따르면 이 취약점은 Apache HTTP Server **2.4.66 이하** 버전에 영향을 미친다. 2.4.67에서는 `mod_http2`를 버전 2.0.39로 업데이트하면서 스트림별 메모리 할당자(stream-specific memory allocator)를 제거해 문제를 해결했다. 서드파티 모듈과의 충돌로 인해 광범위한 불안정성을 야기하던 이 할당자를 제거하는 것이 이번 수정의 핵심이었다.

HTTP/2를 활성화한 공개 웹 서버를 운영 중이라면 이 취약점의 영향권에 있다. Apache 설정에서 HTTP/2를 명시적으로 비활성화하지 않는 한, 기본적으로 활성화되어 있을 수 있다.

```apache
# 현재 활성 프로토콜 확인 (apache2 설정 파일에서)
grep -r "Protocols" /etc/apache2/

# HTTP/2 임시 비활성화 (2.4.67 업그레이드 전 긴급 완화)
# /etc/apache2/sites-enabled/000-default.conf 등에서
Protocols http/1.1
```

### CVE-2026-33006: mod_auth_digest 타이밍 공격

**CVE-2026-33006**은 `mod_auth_digest` 모듈의 타이밍 공격(timing attack)이다. 공격자가 반복된 인증 요청에서 응답 시간 차이를 측정함으로써 자격증명 검증을 우회할 수 있는 사이드 채널(side-channel) 취약점이다.

Digest 인증은 Basic 인증보다 약간 더 안전하다고 여겨지지만, 현대 시스템에서는 Bearer Token, OAuth 2.0, mTLS 같은 더 강력한 인증 방식이 권장된다. 내부 API 서버나 관리 대시보드에서 레거시 Digest 인증을 유지 중이라면 이번 기회에 2.4.67로 업그레이드하면서 인증 방식도 함께 검토할 것을 권장한다.

### CVE-2026-33007: mod_authn_socache NULL 포인터 역참조 → DoS

**CVE-2026-33007**은 `mod_authn_socache` 모듈의 NULL 포인터 역참조(NULL pointer dereference)다. 포워드 프록시(forward proxy) 구성에서 인증되지 않은 사용자가 특수 요청을 전송해 Apache 자식 프로세스를 강제로 크래시시킬 수 있다. 이는 서비스 거부(Denial of Service, DoS) 공격으로 이어진다.

이 취약점은 `mod_authn_socache`를 활성화한 환경에서만 유효하다. 해당 모듈이 필요하지 않다면 비활성화하는 것이 가장 간단한 완화책이다.

```apache
# mod_authn_socache 비활성화 (Ubuntu/Debian)
sudo a2dismod authn_socache
sudo systemctl reload apache2
```

### mod_proxy_ajp: Java 백엔드 연동 환경의 주의 사항

이번 릴리스에서 가장 많은 패치가 집중된 것은 `mod_proxy_ajp` 모듈이다. AJP는 Apache HTTP Server와 Tomcat·JBoss·WildFly 같은 Java EE 서버가 통신하는 데 사용되는 이진 프로토콜로, 전통적인 Apache + Tomcat 구성에서 핵심 역할을 한다.

이번 패치에서 수정된 주요 사항:

| 취약점 유형 | 설명 | 영향 |
|---|---|---|
| 힙 오버리드(Heap over-read) | AJP 파싱 함수의 복수 오류 | 백엔드 메모리 내용 유출 |
| 힙 버퍼 오버플로 | 악성 AJP 응답으로 힙 끝 4바이트 제어 쓰기 | 코드 실행 잠재 가능성 |
| 오프바이원(Off-by-one) | AJP 파싱 경계 조건 오류 | 불안정 동작 |

이러한 취약점들은 악의적이거나 침해된 백엔드 서버가 조건이다. 즉, 공격자가 먼저 Tomcat이나 JBoss에 대한 접근 권한을 얻은 다음, 그것을 이용해 Apache를 공격하는 시나리오다. 내부 네트워크에서만 운영되는 AJP 연결이라도, 공급망 공격이나 다른 취약점을 통해 내부 WAS가 침해된 경우 Apache까지 피해가 확산될 수 있다.

```xml
<!-- Tomcat server.xml: AJP 커넥터 보안 설정 -->
<!-- AJP를 사용하지 않는 경우 아예 비활성화 -->
<!-- <Connector protocol="AJP/1.3"
           address="127.0.0.1"
           port="8009"
           redirectPort="8443"
           requireSecret="true"
           secret="강력한-시크릿값" /> -->

<!-- Spring Boot 내장 Tomcat의 경우 AJP는 기본 비활성화 -->
```

Spring Boot는 기본적으로 내장 Tomcat을 사용하며 AJP는 기본적으로 비활성화되어 있다. 직접 `application.properties`나 `application.yml`에서 AJP를 활성화하지 않았다면 이 부분은 직접적인 영향이 없다. 그러나 외부 Apache 리버스 프록시를 사용하는 구성이라면 Apache 자체 업그레이드가 필요하다.

### 운영 환경별 영향 정리

| 환경 | 영향 여부 | 조치 |
|---|---|---|
| Apache + HTTP/2 활성화 (공개 서버) | **직접 영향** (CVE-2026-23918) | 즉시 2.4.67 업그레이드 |
| Apache + Digest 인증 | **영향** (CVE-2026-33006) | 업그레이드 + 인증 방식 재검토 |
| Apache + mod_authn_socache + 포워드 프록시 | **영향** (CVE-2026-33007) | 업그레이드 또는 모듈 비활성화 |
| Apache + Tomcat AJP 연동 | **잠재적 영향** (mod_proxy_ajp) | 업그레이드 + AJP 시크릿 설정 강화 |
| Spring Boot 내장 Tomcat (AJP 미사용) | **직접 영향 없음** | Apache 업그레이드만 필요 |
| Apache 없이 Nginx 사용 | **영향 없음** | 해당 없음 |

### 업그레이드 방법

**현재 버전 확인:**

```bash
apache2 -v
# 또는
httpd -v
```

**Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install --only-upgrade apache2
apache2 -v  # 2.4.67 이상인지 확인
```

**CentOS / RHEL / Amazon Linux:**

```bash
sudo yum update httpd
# 또는
sudo dnf update httpd
httpd -v
```

**업그레이드 후 설정 검증 및 재시작:**

```bash
# 설정 문법 검사
apachectl configtest
# 또는
apache2ctl configtest

# 설정이 정상이면 재시작
sudo systemctl restart apache2
# 또는
sudo systemctl restart httpd
```

**수동 빌드 환경:** Apache 공식 다운로드 페이지에서 2.4.67 소스를 받아 재빌드해야 한다. 자체 컴파일 환경이라면 패치 적용에 더 많은 시간이 걸릴 수 있으니 우선 HTTP/2 비활성화로 임시 완화부터 적용하는 것을 권장한다.

### 커뮤니티 반응

오픈소스 리눅스 커뮤니티(linuxcompatible.org, warp2search.net)에서는 "이번 릴리스는 단순 기능 패치가 아닌 중요 보안 수정으로, 가능한 한 빨리 적용해야 한다"는 입장이 공유됐다.

Apache HTTP Server 2.4.64 릴리스 때도 8개 취약점을 한꺼번에 수정한 바 있는데, 당시와 마찬가지로 이번 2.4.67도 취약점 공개와 패치 릴리스가 동시에 이루어진 점은 긍정적이다. 보안 취약점이 공개됐지만 패치가 아직 준비되지 않은 '제로데이' 상황과 달리, 패치가 준비된 시점에 취약점 정보를 공개하는 이 방식이 실질적인 피해를 줄이는 데 도움이 된다.

그러나 일부 DevOps 커뮤니티에서는 "아직도 Apache HTTP Server를 프로덕션에서 HTTP 엔드포인트로 직접 사용하는 경우가 얼마나 남아있는지"에 대한 논의도 나왔다. Nginx, Caddy, HAProxy 같은 더 현대적인 대안이 많아진 지금, Apache를 새 프로젝트에 도입하는 경우는 줄었지만 10년 이상 운영된 레거시 스택에서는 여전히 Apache가 핵심 구성 요소인 경우가 많다.

## 정리

- Apache HTTP Server 2.4.67이 2026-05-04 출시됐으며, HTTP/2 RCE(CVE-2026-23918), Digest 인증 타이밍 공격(CVE-2026-33006), mod_authn_socache DoS(CVE-2026-33007), mod_proxy_ajp 다수 메모리 안전성 문제를 수정했다.
- HTTP/2를 활성화한 공개 Apache 서버는 CVE-2026-23918에 직접적인 영향을 받으므로 즉시 2.4.67로 업그레이드해야 한다.
- Apache + Tomcat/JBoss AJP 연동 환경에서는 mod_proxy_ajp 취약점에 주의하고, AJP 시크릿 설정도 함께 점검해야 한다.
- Spring Boot 내장 Tomcat 단독 구성(AJP 미사용)은 직접적인 영향을 받지 않지만, Apache 리버스 프록시를 앞에 두는 구성이라면 Apache 업그레이드가 필수다.
- 임시 완화가 어렵다면 HTTP/2를 일시 비활성화(`Protocols http/1.1`)하거나 사용하지 않는 모듈을 비활성화하는 것을 우선 적용하고 빠른 시일 내에 정식 업그레이드를 진행한다.

## Reference

- [Apache HTTP Server 2.4 vulnerabilities - Apache Official](https://httpd.apache.org/security/vulnerabilities_24.html)
- [Apache HTTP Server 2.4.67 released - linuxcompatible.org](https://www.linuxcompatible.org/story/apache-http-server-2467-released)
- [Apache HTTP Server 2.4.67 released - warp2search.net](https://www.warp2search.net/story/apache-http-server-2467-released)
- [Apache HTTP Server Security Vulnerabilities in 2026 - stack.watch](https://stack.watch/product/apache/http-server/)
- [Apache Http Server Security vulnerabilities, CVEs - cvedetails.com](https://www.cvedetails.com/vulnerability-list/vendor_id-45/product_id-66/Apache-Http-Server.html)
