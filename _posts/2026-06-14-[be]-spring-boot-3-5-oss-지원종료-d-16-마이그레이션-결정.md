---
title: "[BE] Spring Boot 3.5 OSS 지원 종료 D-16 — 마이그레이션 결정을 더 이상 미룰 수 없다"
date: 2026-06-14 11:00:00 +09:00
categories: [BE]
tag: [SpringBoot, Java, 마이그레이션, EOL, Jackson3, SpringSecurity7]
---

## 서론

2026년 6월 30일, Spring Boot 3.5의 오픈소스(OSS) 지원이 종료된다. 오늘이 6월 14일이니 정확히 **16일이 남았다**. Spring Boot 3.5가 마지막 3.x 마이너 릴리스라는 점에서, 이번 EOL은 단순한 버전 종료가 아니다 — Spring Boot 3.x 생태계 전체의 공식 오픈소스 지원이 끊기는 시점이다.

HeroDevs, foojay.io, endoflife.ai 등 여러 자바 개발 커뮤니티가 최근 Spring Boot 마이그레이션에 대한 심층 분석을 잇달아 발표하고 있다. 공통적인 메시지는 하나다: **결정을 더 이상 미룰 수 없다**.

지원 종료 후 발생하는 CVE에는 패치가 나오지 않는다. Spring Framework, Spring Security, Spring Data, Tomcat, Jackson, Hibernate 등 수십 개 의존성 라이브러리에서 발견되는 새로운 취약점이 3.5.x 버전에 영향을 미쳐도, Spring 커뮤니티는 더 이상 3.5.x 브랜치에 수정을 제공하지 않는다. 결과적으로 CVE가 공개적으로 알려진 상태에서 패치 경로가 없는 상황이 계속 누적된다.

이 글에서는 Spring Boot 4.0의 주요 변경사항과 마이그레이션 전략, 그리고 16일 안에 내려야 할 현실적인 결정을 정리한다.

## 본론

### Spring Boot 3.5 EOL 이후 무슨 일이 생기나

Spring Boot의 공식 지원 종료 이후 달라지는 것들을 구체적으로 짚어보자.

**CVE 누적, 패치 없음**

Spring Boot는 수십 개 라이브러리 위에 올라선다. 이 의존성들에서 발견되는 새로운 CVE가 3.5.x에 영향을 미쳐도 공식 패치가 없다. foojay.io는 이 상황을 "CVE Blind Spot"이라고 표현했다. 취약점은 NVD에 공개 등록되는데 패치는 없는 상태 — 공격자는 알고 있고 방어자는 손을 쓸 수 없는 구조다.

**컴플라이언스 리스크**

SOC 2, ISO 27001, PCI-DSS 같은 보안 컴플라이언스 프레임워크는 지원되는(supported) 소프트웨어 사용을 요구하는 경우가 많다. EOL 소프트웨어 사용은 감사 과정에서 지적 사항이 될 수 있다. EU의 사이버 복원력법(CRA, Cyber Resilience Act)도 소프트웨어 의존성의 지속적 보안 관리를 요구하므로, 글로벌 서비스를 운영하는 조직에게는 규제 리스크로 이어질 수 있다.

**커뮤니티 지원 축소**

Spring Initializr의 기본 선택, 각종 프레임워크 통합 가이드, IDE 플러그인 지원이 점차 4.x 기준으로 전환된다. 새로운 문제에 대한 Stack Overflow 답변이나 커뮤니티 지원도 4.x 기준으로 수렴하기 시작한다.

### Spring Boot 4.0이란: 어떤 플랫폼으로 전환되나

Spring Boot 4.0은 단순한 버전 업그레이드가 아니다. **Spring Framework 7.0 기반**으로 전환되며, 주요 의존성이 메이저 버전 업그레이드를 동반한다.

| 의존성 | 3.5.x | 4.0.x |
|---|---|---|
| Spring Framework | 6.2 | 7.0 |
| Spring Security | 6.x | 7.0 |
| Spring Data | 2024.x | 2025.1 |
| Hibernate | 6.x | 7.1 |
| Jackson | 2.x | 3.0 |
| 최소 Java 버전 | 17 | 17 |

현재 최신 안정 버전은 **Spring Boot 4.0.7**이며, OSS 지원은 2026년 12월 31일까지 제공된다.

### 변경사항 1: Jackson 3 — 패키지 구조 자체가 바뀐다

Spring Boot 4.0에서 가장 광범위한 영향을 미치는 변경사항 중 하나가 **Jackson 3** 기본 탑재다. Jackson 3는 Jackson 2.x와 패키지 구조 자체가 달라졌다.

**그룹 ID 변경:**

```xml
<!-- 기존 (Jackson 2.x) -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>

<!-- 변경 후 (Jackson 3) -->
<dependency>
    <groupId>tools.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

pom.xml이나 build.gradle에서 Jackson 의존성을 직접 선언하는 곳이 있다면 모두 수정해야 한다.

**주요 API 변경:**

```java
// Spring Boot 3.5 (Jackson 2.x)
@JsonComponent
public class CustomSerializer extends JsonSerializer<MyClass> {
    @Override
    public void serialize(MyClass value, JsonGenerator gen,
                          SerializerProvider provider) throws IOException {
        // ...
    }
}

// Spring Boot 4.0 (Jackson 3)
@JacksonComponent  // @JsonComponent → @JacksonComponent
public class CustomSerializer extends JsonSerializer<MyClass> {
    @Override
    public void serialize(MyClass value, JsonGenerator gen,
                          SerializerProvider provider) throws IOException {
        // API 시그니처는 유사하나, 패키지 임포트가 tools.jackson.*으로 변경됨
    }
}
```

또한 `Jackson2ObjectMapperBuilderCustomizer`는 `JsonMapperBuilderCustomizer`로 이름이 바뀌었고, Spring MVC/WebFlux JSON 설정 프로퍼티도 일부 재구성됐다.

**영향받는 코드 유형:**
- 커스텀 Serializer/Deserializer (`extends JsonSerializer<T>`, `extends JsonDeserializer<T>`)
- `ObjectMapper`를 직접 생성하는 코드
- `@JsonComponent`를 사용하는 모든 클래스
- Jackson 관련 `@Configuration` 빈

### 변경사항 2: Spring Security 7 — 암묵적 동작이 사라진다

Spring Security 7에서 가장 중요한 변화는 **암묵적(implicit) 동작의 완전 제거**다. 기존 Spring Security 6.x에서는 설정하지 않아도 "합리적인 기본값"으로 동작하던 항목들이 많았다. 7에서는 모든 보안 동작을 명시적으로 선언해야 한다.

```java
// Spring Boot 3.5 (Spring Security 6.x)
// 특별한 설정 없이도 CSRF 보호, 세션 관리 등 암묵적 기본값 적용
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/**").authenticated()
            .anyRequest().permitAll()
        );
        return http.build();
    }
}

// Spring Boot 4.0 (Spring Security 7)
// 모든 보안 동작을 명시적으로 선언
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/**").authenticated()
                .anyRequest().permitAll()
            )
            .csrf(csrf -> csrf.disable())              // 명시적 비활성화 또는 설정
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .httpBasic(Customizer.withDefaults());     // 명시적 활성화
        return http.build();
    }
}
```

Spring Security 팀은 6.5를 먼저 적용하고, 6.5에서 제공하는 "7.0 방식으로 설정을 미리 전환하는 전략"을 활용한 뒤 7.0으로 올라갈 것을 공식 마이그레이션 가이드에서 권장한다.

### 변경사항 3: 테스트 어노테이션 변경

테스트 코드에 미치는 영향도 상당하다. 자주 쓰이는 테스트 지원 어노테이션이 바뀌었다.

```java
// Spring Boot 3.5
@SpringBootTest
class MyServiceTest {
    @MockBean      // Spring 제공 Mock
    private MyRepository myRepository;

    @SpyBean       // Spring 제공 Spy
    private MyService myService;
}

// Spring Boot 4.0
@SpringBootTest
class MyServiceTest {
    @MockitoBean      // @MockBean → @MockitoBean
    private MyRepository myRepository;

    @MockitoSpyBean   // @SpyBean → @MockitoSpyBean
    private MyService myService;
}
```

또한 `@SpringBootTest`가 더 이상 MockMVC, WebClient, TestRestTemplate을 자동으로 설정하지 않는다. 슬라이스 테스트를 사용하거나 명시적으로 추가해야 한다.

```java
// Spring Boot 4.0: MockMVC 사용 시 명시적 추가
@SpringBootTest
@AutoConfigureMockMvc   // 명시적 추가 필요
class MyControllerTest {
    @Autowired
    private MockMvc mockMvc;
}
```

### 변경사항 4: 모듈화와 새로운 스타터 요구사항

Spring Boot 4.0은 새로운 모듈 아키텍처를 도입했다. 기존에 서드파티 라이브러리만 추가하면 Spring Boot Auto-configuration이 자동으로 잡아주던 통합들이, 이제 Spring Boot 공식 스타터를 명시적으로 추가해야 동작한다.

```xml
<!-- Spring Boot 4.0: Flyway DB 마이그레이션 사용 시 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-flyway</artifactId>
</dependency>

<!-- Spring Boot 4.0: Liquibase 사용 시 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-liquibase</artifactId>
</dependency>
```

Flyway나 Liquibase를 `com.flyway:flyway-core` 직접 의존성으로만 사용하던 프로젝트는 스타터 추가가 필요하다.

### 변경사항 5: 지원 종료된 컴포넌트들

Spring Boot 4.0에서 완전히 제거된 항목들이 있다.

- **Undertow 임베디드 서버 지원 제거**: Servlet 6.1 기반 전환과 함께 Undertow가 제거됐다. Undertow를 사용 중이라면 Tomcat 또는 Jetty로 전환이 필요하다.
- **Spring Session Hazelcast & MongoDB**: 외부 팀으로 이전됐다.
- **Pulsar Reactive 지원 종료**: Spring Pulsar에서 Reactor 지원이 제거됐다.
- **임베디드 실행 가능 jar 런치 스크립트**: 레거시 배포 파이프라인을 사용하는 경우 검토가 필요하다. 컨테이너 기반 배포를 사용하는 조직은 영향이 없다.

### 마이그레이션 전략: 안전한 경로

Spring 공식 권장 마이그레이션 경로는 다음과 같다.

**1단계: Spring Boot 3.5.x 최신으로 올리고 Deprecation 정리**

Spring Boot 4.0으로 바로 올라가기 전에, 현재 사용 중인 3.x 버전에서 3.5.x 최신 패치 버전으로 먼저 업그레이드한다. 이 과정에서 `@Deprecated` 경고를 모두 해소한다. 3.5.x에서 Deprecation이 정리된 상태여야 4.0 마이그레이션 시 컴파일 에러가 줄어든다.

**2단계: 의존성 분석**

`./mvnw dependency:tree` 또는 `./gradlew dependencies` 결과를 보며, Jackson, Spring Security, Hibernate를 직접 확장하거나 의존하는 코드가 어디에 있는지 파악한다. 커스텀 Serializer, Security Config, Repository 구현체가 주요 점검 대상이다.

**3단계: 테스트 커버리지 확보**

마이그레이션 전 통합 테스트 커버리지를 최대한 높인다. Spring Boot 4.0의 주요 변경사항이 많은 만큼, 테스트가 없으면 어떤 기능이 깨졌는지 파악하기 어렵다. 특히 Security Config 변경이 API 인증 동작에 미치는 영향은 통합 테스트 없이는 검증하기 힘들다.

**4단계: 별도 브랜치에서 4.0 마이그레이션**

```xml
<!-- pom.xml -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>4.0.7</version>  <!-- 현재 최신 안정 버전 -->
</parent>
```

컴파일 에러를 하나씩 해소하면서 테스트를 통과시킨다. HeroDevs의 추정치에 따르면 중간 규모 코드베이스 기준 200~500 시간의 작업이 소요될 수 있다는 점을 염두에 두고 현실적인 일정을 잡아야 한다.

### 16일 안에 완료할 수 없다면: 현실적 옵션

현실적으로 16일 안에 Spring Boot 4.0으로 마이그레이션을 완료하는 것은 대부분의 조직에서 불가능하다.

**옵션 1: HeroDevs NES (Never-Ending Support)**

HeroDevs는 EOL 이후에도 Spring Boot 3.5.x에 대한 상업적 보안 패치를 제공하는 서비스다. 마이그레이션 기간 동안 CVE 노출 없이 시간을 버는 임시 완충재로 활용할 수 있다. EU CRA 환경에서 "지원되는 소프트웨어 사용" 의무를 충족하는 방법 중 하나로도 거론된다. 다만 이는 장기 해결책이 아니다.

**옵션 2: 단계별 마이그레이션 계획 수립 후 3.5.x 운영 유지**

EOL 이후에도 단기간 3.5.x를 계속 운영하면서 마이그레이션을 완료하는 계획을 수립한다. 이 기간 동안 신규 CVE를 수동으로 모니터링하고 위험도를 평가하는 체계를 갖춰야 한다. 컴플라이언스 상황에 따라 이 옵션이 허용되지 않을 수 있으므로 보안/법무팀과 협의가 필요하다.

### 지금 당장 해야 할 체크리스트

마이그레이션 방향을 결정했든 아니든, 오늘 당장 할 수 있는 것들이 있다.

```text
즉각 체크리스트:
□ 현재 서비스가 사용하는 Spring Boot 버전 확인
□ 의존성 트리에서 Jackson, Spring Security, Hibernate 버전 확인
□ 커스텀 Serializer/Deserializer, @JsonComponent 사용 여부 확인
□ @MockBean/@SpyBean 사용 테스트 코드 수 파악
□ Undertow 사용 여부 확인 (embedded server)
□ Scripted/Custom integration (Flyway, Liquibase 직접 의존성) 확인
□ EOL 관련 팀 내 공유 및 의사결정 일정 잡기
```

## 정리

- Spring Boot 3.5의 OSS 지원은 2026년 6월 30일(D-16)에 종료된다. 이후 발견되는 CVE에는 공식 패치가 제공되지 않는다.
- Spring Boot 4.0의 주요 변경사항: Jackson 3(tools.jackson 패키지), Spring Security 7(명시적 설정 의무화), `@MockitoBean`/`@MockitoSpyBean`, Undertow 제거, 모듈화 스타터 필요.
- 권장 마이그레이션 경로: 3.5.x 최신 + Deprecation 정리 → 테스트 커버리지 확보 → 4.0.7로 마이그레이션.
- 즉각 마이그레이션이 불가한 경우 HeroDevs NES 같은 상업적 지원을 단기 옵션으로 검토할 수 있다.
- 커뮤니티의 공통 시각은 "EOL 소프트웨어 사용의 CVE 누적 위험과 컴플라이언스 리스크가 마이그레이션 비용보다 크다"는 것이다. 결정을 미룰수록 마이그레이션 복잡도만 높아진다.

## Reference

- [Spring Boot 4.0 Migration Guide — GitHub (spring-projects)](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
- [Spring Boot 3.5 EOL: What the Migration Really Takes — HeroDevs](https://www.herodevs.com/blog-posts/spring-boot-3-5-eol-what-the-migration-really-takes)
- [Spring Boot 3.5 EOL — The CVE Blind Spot Nobody Talks About — foojay.io](https://foojay.io/today/crossing-the-river-styx-spring-boot-3-5-and-the-zombie-dependency-problem/)
- [Spring Boot Migration and the CRA: When Good Enough Isn't — foojay.io](https://foojay.io/today/spring-boot-migration-and-the-cra-when-good-enough-isnt/)
- [Migrating to Spring Security 7.0 — Spring Security Official Docs](https://docs.spring.io/spring-security/reference/7.0/migration/index.html)
- [Spring Boot 4.0 Migration Guide for Production Teams — DEV Community](https://dev.to/aytronn/spring-boot-40-migration-guide-for-production-teams-what-actually-breaks-and-how-to-upgrade-safely-22me)
- [Spring Boot End of Life Dates — endoflife.date](https://endoflife.date/spring-boot)
