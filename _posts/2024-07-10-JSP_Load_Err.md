---
title: "[JSP] Spring Boot에서 Error resolving template 해결하기"
date: 2024-07-10 09:15:46 +09:00
categories: [Error]
tag: [JSP, Spring Boot, Error]
---

## 문제 상황

Spring Boot + JSP + JSTL 기반으로 웹 프로젝트를 구성하던 중, `WEB-INF` 아래에 있는 JSP 파일을 정상적으로 불러오지 못했다.

## 해결 과정

### 1. 의존성 설정

Spring Boot는 기본적으로 JSP를 바로 지원하지 않으므로, 아래 의존성을 추가해줘야 한다.

```gradle
implementation 'org.apache.tomcat.embed:tomcat-embed-jasper'
implementation 'jakarta.servlet:jakarta.servlet-api'
implementation 'jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api'
implementation 'org.glassfish.web:jakarta.servlet.jsp.jstl'
```

### 2. `application.properties` 수정

`WEB-INF` 디렉터리 아래의 JSP를 찾도록 `prefix`와 `suffix`를 설정한다.

```properties
spring.mvc.view.prefix=/WEB-INF/views/
spring.mvc.view.suffix=.jsp
```

JSP를 수정했을 때 서버를 매번 재시작하지 않고 바로 반영하려면 `development` 옵션도 함께 켜두는 편이 편하다.

```properties
server.servlet.jsp.init-parameters.development=true
```

설정을 마친 뒤 서버를 실행하면 아래처럼 JSP가 정상적으로 렌더링되는 것을 확인할 수 있다.

<div align="left">
    <img src="./assets/images/JSP_Load_Err/JSP_Load_Err_01.png" alt="JSP_Load_Err_01">
</div>

## Reference

> [[Spring] Spring Boot 3에서 JSP 설정방법](https://velog.io/@rhkdbtj/Spring-Spring-boot-3%EC%97%90%EC%84%9C-jsp-%EC%84%A4%EC%A0%95%EB%B0%A9%EB%B2%95)
