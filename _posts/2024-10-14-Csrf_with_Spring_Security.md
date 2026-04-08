---
title: "[Spring Security] CSRF 개념과 Spring Security 설정"
date: 2024-10-14 08:17:46 +09:00
categories: [Java]
tag: [Spring Security, CSRF, Security]
---

## CSRF란?

CSRF는 `Cross-Site Request Forgery`의 약자로, 사용자가 의도하지 않은 요청을 인증된 상태에서 보내게 만드는 공격을 의미한다.
Spring Security는 기본적으로 CSRF 보호를 활성화하며, 일반적으로 `GET`을 제외한 상태 변경 요청을 보호 대상으로 본다.

CSRF 보호가 켜져 있으면 HTML 폼에는 다음과 같은 토큰 값이 함께 포함되어야 한다.

```html
<input type="hidden" name="${_csrf.parameterName}" value="${_csrf.token}" />
```

## Spring Security 설정

1. 라이브러리 추가

```gradle
implementation 'org.springframework.boot:spring-boot-starter-security'
```

2. Security Config 작성

```java
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf((csrf) -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
    }
}
```

이렇게 설정하면 서버가 CSRF 토큰을 발급하고 검증할 수 있다.
폼 기반 요청을 처리하는 화면이라면, 클라이언트에서도 이 토큰을 요청에 함께 포함해야 정상 처리된다.

## REST API에서의 CSRF

Spring Security 공식 문서에서는 브라우저 기반 세션 인증이 아닌, non-browser clients 중심의 서비스라면 CSRF 비활성화를 고려할 수 있다고 설명한다.
REST API는 보통 세션 상태를 서버에 저장하지 않는 `stateless` 구조를 사용하고, 매 요청마다 인증 정보를 명시적으로 보낸다.
이 경우 쿠키 기반 세션 인증에서 주로 문제가 되는 CSRF 위험이 상대적으로 낮기 때문에, 상황에 따라 CSRF를 비활성화하기도 한다.

## Reference

> [Spring Security - CSRF란?](https://velog.io/@woohobi/Spring-security-csrf%EB%9E%80)
