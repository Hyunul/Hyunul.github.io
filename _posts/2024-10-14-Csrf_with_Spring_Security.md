---
title: "[Spring] Spring Security와 CSRF"
date: 2024-10-14 08:17:46 +09:00
categories: [Spring]
tag: [csrf, spring]
---

## CSRF란?
---
CSRF는 `Cross-Site Request Forgery`의 약자로 쉽게 말해 `정상적인 사용자가 의도치 않은 위조 요청을 보내는 것`을 의미한다.  
Spring Security에서 CSRF Protection은 default로 설정된다. 즉, protection을 통해 GET요청을 제외한 요청으로부터 보호한다.  
또한, CSRF protection을 적용했을 때, html에서 다음과 같은 CSRF 토큰이 포함되어야 요청을 받아들이게 됨으로써, 위조 요청을 방지하게 된다.

```html
<input type="hidden" name="${_csrf.parameterName}" value="${_csrf.token}"/>
```

## Spring Security 설정
---
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

이와 같이 설정을 잘 완료하게 된다면, html에서 따로 CSRF 토큰을 포함시키지 않아도 Spring Security 측에서 토큰을 부여해준다.  

## REST API에서의 CSRF?
Spring Security Documentation에서는 non-browser clients 만을 위한 서비스라면 CSRF를 비활성화시켜도 된다고 한다.  
이는 REST API를 이용한 서버라면, Session 기반 인증과는 다르게 stateless하기 때문에 서버에 인증 정보를 보관하지 않는다.  
REST API에서 client는 권한이 필요한 요청을 하기 위해서는 요청에 필요한 인증 정보를 포함시켜야 한다.  
따라서 서버에 인증 정보를 저장하지 않기 때문에 불필요한 CSRF 코드를 작성할 필요가 없는 것이다.

## Reference
> [Spring Security - CSRF란?](https://velog.io/@woohobi/Spring-security-csrf%EB%9E%80)  