---
title: "[BE] Spring Boot 4.1.0 정식 출시 — gRPC 자동설정, SSRF 방어, Kotlin 2.3 통합"
date: 2026-06-17 08:00:00 +09:00
categories: [BE]
tag: [SpringBoot, gRPC, SSRF, Kotlin, SpringFramework]
---

## 서론

2026년 6월 10일, Spring Boot 4.1.0이 Maven Central에 정식 출시되었습니다. Spring Boot 4.0이 등장한 이후 첫 마이너 릴리스인 4.1은 생각보다 알차게 채워져 있습니다. 특히 **gRPC 자동 구성(auto-configuration)**, **HTTP 클라이언트 SSRF 방어**, 그리고 **Kotlin 2.3 지원**이 포함되어, 마이크로서비스와 클라우드 네이티브 환경을 구축하는 백엔드 개발자들에게 직접적인 영향이 있는 변경들입니다.

spring.io 공식 블로그와 GitHub wiki의 릴리스 노트를 기반으로, 이번 글에서는 Spring Boot 4.1.0의 주요 신규 기능들을 하나씩 살펴보고, 기존 4.0 환경에서 업그레이드할 때 주의해야 할 파괴적 변경(breaking change)들도 정리해보겠습니다.

## 본론

### Spring gRPC 자동 구성

Spring Boot 4.1.0의 가장 큰 신규 기능은 **Spring gRPC 통합**입니다. 기존에는 gRPC 서버와 클라이언트를 Spring Boot 애플리케이션에 통합하려면 별도 라이브러리와 복잡한 수동 설정이 필요했습니다. 4.1부터는 Spring Boot가 gRPC 서버·클라이언트의 자동 구성을 기본 제공합니다.

지원하는 두 가지 배포 모드가 있습니다.

**1. 독립 실행형 Netty 서버 모드**

gRPC 전용 Netty 서버를 별도 포트에서 구동합니다. REST API와 gRPC 서비스를 동시에 제공하는 멀티 프로토콜 서버를 구성할 때 유용합니다.

```yaml
spring:
  grpc:
    server:
      port: 9090
      enabled: true
```

**2. Servlet 컨테이너 HTTP/2 통합 모드**

기존 서블릿 컨테이너(Tomcat, Jetty 등)의 HTTP/2 위에서 gRPC를 동작시킵니다. 추가 포트 없이 하나의 서버에서 REST와 gRPC를 함께 처리할 수 있습니다.

gRPC 서비스 구현은 기존 Spring 방식과 자연스럽게 통합됩니다:

```java
@GrpcService
public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {

    private final UserRepository userRepository;

    @Override
    public void getUser(GetUserRequest request, StreamObserver<UserResponse> observer) {
        User user = userRepository.findById(request.getId())
            .orElseThrow(() -> new StatusRuntimeException(Status.NOT_FOUND));

        UserResponse response = UserResponse.newBuilder()
            .setId(user.getId())
            .setName(user.getName())
            .setEmail(user.getEmail())
            .build();

        observer.onNext(response);
        observer.onCompleted();
    }
}
```

gRPC 클라이언트도 마찬가지로 자동 구성이 지원되어, `@GrpcClient` 어노테이션 하나로 채널 관리와 로드밸런싱이 자동 처리됩니다. InfoQ의 분석에 따르면 이 기능은 "마이크로서비스 간 고성능 통신이 필요한 팀들이 Spring Boot 생태계를 벗어나지 않고도 gRPC를 도입할 수 있게 해주는 중요한 이정표"로 평가받고 있습니다.

### SSRF 방어: InetAddressFilter

이번 릴리스에서 보안 측면에서 가장 주목할 추가 기능은 **`InetAddressFilter`**를 통한 SSRF(Server-Side Request Forgery) 방어입니다.

SSRF는 공격자가 서버를 통해 내부 네트워크 자원에 접근하도록 유도하는 공격 기법입니다. 예를 들어, 애플리케이션이 사용자가 제공한 URL로 HTTP 요청을 보내는 기능이 있을 때, 공격자가 `http://169.254.169.254/latest/meta-data/`(AWS 인스턴스 메타데이터 서버) 같은 내부 주소를 입력하면 클라우드 자격증명이 노출될 수 있습니다.

Spring Boot 4.1의 `InetAddressFilter`는 HTTP 클라이언트(반응형 및 블로킹 모두)에서 실제 TCP 연결을 시도하기 전에 대상 IP 주소를 검사합니다:

```java
@Bean
public InetAddressFilter ssrfProtectionFilter() {
    return InetAddressFilter.builder()
        .denyPrivateAddresses()        // 사설 IP 차단 (10.x, 172.16-31.x, 192.168.x)
        .denyLoopback()                // 루프백 차단 (127.x, ::1)
        .denyLinkLocal()               // 링크로컬 차단 (169.254.x)
        .allowHosts("api.external.com") // 명시적 화이트리스트
        .build();
}
```

이 필터는 `RestTemplateBuilder`, `RestClient.Builder`, `WebClient.Builder` 등 Spring Boot가 자동 구성하는 HTTP 클라이언트 빌더에 공통으로 적용됩니다. 외부 URL로 요청을 보내는 기능(예: 웹훅 발송, 외부 API 호출, 파일 다운로드 기능)이 있는 서비스라면 이 필터를 적극 활성화하는 것이 권장됩니다.

또한 4.1에서는 `TestRestTemplate`, `RestTemplateBuilder`, `HttpClientSettings` 간의 쿠키 처리 동작도 일관성 있게 정렬(align)되었습니다. 이전에는 테스트 환경과 실제 환경의 쿠키 동작이 미묘하게 달라 문제가 생기는 경우가 있었는데, 이 부분이 개선되었습니다.

### Jackson 설정 세분화

Jackson ObjectMapper 관련 설정이 더 세분화되었습니다. 기존 `spring.jackson.*` 프로퍼티에 읽기/쓰기를 구분하는 설정이 추가되었습니다:

```yaml
spring:
  jackson:
    read:
      allow-comments: true
      allow-unquoted-field-names: false
    write:
      indent-output: false
      write-dates-as-timestamps: false
      write-enums-using-to-string: true
```

또한 커스텀 팩토리 빌더를 위한 콜백 인터페이스도 추가되었습니다:

- `JsonFactoryBuilderCustomizer` — 기본 JSON 팩토리 커스터마이징
- `CborFactoryBuilderCustomizer` — CBOR 포맷 지원
- `XmlFactoryBuilderCustomizer` — XML 포맷 지원

그리고 `spring.config.import`를 사용할 때 파일 인코딩을 명시할 수 있게 되었습니다:

```yaml
spring:
  config:
    import: "classpath:external-config.properties[encoding=utf-8]"
```

한글이나 특수 문자가 포함된 설정 파일을 외부에서 임포트할 때 유용한 기능입니다.

### 데이터 레이어 개선

**MongoDB Batch 지원**

Spring Batch와 MongoDB를 함께 사용하는 환경에서 자동 구성이 새로 지원됩니다:

```yaml
spring:
  batch:
    data:
      mongo:
        schema:
          initialize: true  # MongoDB에 배치 메타데이터 스키마 자동 생성
```

이전에는 Spring Batch를 MongoDB와 함께 쓸 때 JobRepository, JobLauncher 등을 모두 수동으로 구성해야 했습니다. 4.1부터는 `spring.batch.data.mongo.schema.initialize=true` 설정 하나로 MongoDB 기반 배치 메타데이터 스키마가 자동 초기화됩니다.

**Redis Listener 자동 구성**

`@RedisListener` 어노테이션이 붙은 엔드포인트는 이제 `RedisMessageListenerContainer`를 자동으로 등록합니다. 이전에는 수동으로 컨테이너 빈을 설정해야 했습니다:

```java
@Component
public class RedisEventHandler {

    @RedisListener(topics = "user-events")
    public void handleUserEvent(String message) {
        // 구독 메시지 처리
    }

    @RedisListener(topics = "order-events", pattern = true)
    public void handleOrderEvent(String channel, String message) {
        // 패턴 기반 구독 처리
    }
}
```

**Log4j 파일 로테이션**

Log4j 사용 환경에서 로그 파일 로테이션 전략을 application.yml로 관리할 수 있게 되었습니다:

```yaml
logging:
  log4j2:
    rolling:
      strategy: size-and-time  # size | time | size-and-time | cron
      max-size: 10MB
      max-history: 30
```

`size`, `time`, `size-and-time`, `cron` 4가지 전략을 지원합니다. 운영 환경에서 로그 볼륨 관리가 간편해집니다.

**임베디드 LDAP SSL/LDAPS 지원**

개발·테스트용 임베디드 LDAP 서버에서도 이제 SSL/LDAPS 구성을 지원합니다. 실제 LDAPS 환경을 로컬에서 에뮬레이션해야 하는 시나리오에서 유용합니다.

**OpenTelemetry 환경 변수 정렬**

OpenTelemetry 관련 환경 변수 지원이 표준 OTel 사양과 더 잘 정렬되었습니다. Spring Boot의 자동 구성 프로퍼티와 OTel 표준 환경 변수 사이의 불일치가 줄어들어, 기존 OTel 에이전트나 컬렉터 설정을 그대로 재활용하기 편해졌습니다.

### 파괴적 변경(Breaking Changes) 정리

4.0에서 4.1로 업그레이드할 때 반드시 확인해야 할 변경 사항들입니다.

| 항목 | 변경 내용 | 대응 방법 |
|------|-----------|-----------|
| Apache Derby | 지원 deprecated | H2 또는 HSQLDB로 마이그레이션 권장 |
| Layertools jar mode | 완전 제거 | 레이어드 JAR 구성 방식 재검토 필요 |
| jOOQ 최소 버전 | 3.20 요구 (Java 21 필수) | jOOQ 버전 및 JVM 업그레이드 필요 |
| Maven `-DskipTests` | AOT 처리에 미적용됨 | `maven.test.skip` 프로퍼티 사용으로 전환 |
| Spring Data JPA `deferred` 모드 | `AsyncTaskExecutor` 빈 필수 | 관련 빈 명시적 등록 필요 |
| Spring Data JPA `lazy` 모드 | 부트스트랩 실행기 자동 구성 제거 | 필요 시 직접 구성해야 함 |

특히 jOOQ를 사용하는 프로젝트는 **Java 21 이상의 JVM이 필수**가 되어, JVM 버전 업그레이드 일정도 함께 고려해야 합니다. 4.0에서 deprecated된 클래스, 메서드, 프로퍼티는 모두 4.1에서 일괄 제거되었으므로, 마이그레이션 전 deprecation 경고를 전부 해소하는 것이 권장됩니다.

### 이전 버전과의 관계

Spring Boot 4.1.0에는 **Spring Boot 4.0.7의 모든 버그 수정, 문서 개선, 보안 패치**가 포함되어 있습니다. 4.0.x를 사용 중이라면 4.1.0으로의 업그레이드가 보안 관점에서도 권장됩니다. 마이그레이션 가이드 전문과 deprecated API 전체 목록은 공식 GitHub wiki에서 확인할 수 있습니다.

## 정리

- Spring Boot 4.1.0이 2026년 6월 10일 Maven Central에 출시
- **gRPC 자동 구성**: 독립 Netty 서버 또는 기존 서블릿 HTTP/2 위에서 gRPC 서버·클라이언트를 Spring Boot 방식으로 통합 가능. `@GrpcService` 어노테이션으로 서비스 정의
- **SSRF 방어**: `InetAddressFilter`로 HTTP 클라이언트의 내부 IP·루프백·링크로컬 요청 자동 차단. 외부 URL 처리 기능이 있는 서비스라면 필수 적용 권장
- **Jackson 세분화**: 읽기/쓰기 구분 설정(`spring.jackson.read.*`, `spring.jackson.write.*`), 포맷별 팩토리 빌더 콜백, 설정 임포트 인코딩 지정 지원
- **데이터 레이어**: MongoDB Batch 자동 구성, Redis Listener 자동 구성, Log4j 4가지 파일 로테이션 전략 지원
- **파괴적 변경 주의**: Derby deprecated, Layertools 완전 제거, jOOQ 3.20+ (Java 21 필수), Maven `-DskipTests` 동작 변경, Spring Data JPA 부트스트랩 모드 변경
- InfoQ와 Spring 커뮤니티는 gRPC 통합과 SSRF 방어를 이번 릴리스의 핵심 기여로 평가. 업그레이드 전 GitHub wiki 마이그레이션 가이드 확인 필수

## Reference

- [Spring Boot 4.1.0 available now — spring.io](https://spring.io/blog/2026/06/10/spring-boot-4/)
- [Spring Boot 4.1 Release Notes — GitHub Wiki](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.1-Release-Notes)
- [Spring Boot 4.1 Adds gRPC Auto-Configuration, SSRF Mitigation, and Kotlin 2.3 Support — InfoQ](https://www.infoq.com/news/2026/06/spring-boot-4-1/)
- [Spring Boot 4.1.0 M1 Release Notes — GitHub Wiki](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.1.0-M1-Release-Notes)
- [Spring Boot End of Life (EOL) Dates — endoflife.date](https://endoflife.date/spring-boot)
