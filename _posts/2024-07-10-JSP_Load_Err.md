---
title: "[Spring] JSP 파일을 못 읽을 때"
date: 2024-07-10 09:15:46 +09:00
categories: [Tech, Web]
tag: [Spring]
---

# 문제상황

Spring Boot와 JSP, JSTL 기반의 웹 프로젝트를 구성하다가 Spring이 WEB-INF에 있는 JSP 파일을 불러오지 못함.

# 해결 과정

## 의존성 설정

Spring Boot에서는 기본적으로 JSP를 지원하지 않으므로 다음의 의존성을 추가해줘야 함.

```gradle
implementation 'org.apache.tomcat.embed:tomcat-embed-jasper'
implementation 'jakarta.servlet:jakarta.servlet-api'
implementation 'jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api'
implementation 'org.glassfish.web:jakarta.servlet.jsp.jstl'
```

## application.properties 수정

WEB-INF 디렉토리를 사용하기 위해 `prefix`와 `suffix`를 작성해준다.

```properties
spring.mvc.view.prefix=/WEB-INF/views/
spring.mvc.view.suffix=.jsp
```

또한 JSP를 수정했을 때 서버를 재실행시키지 않아도 바로 반영되도록 `development`를 활성화시킨다.

```properties
server.servlet.jsp.init-parameters.development=true
```

모든 설정과 JSP 파일을 작성한 뒤에 서버를 실행시키면 다음과 같이 잘 작동하는 것을 확인할 수 있다.

<div align="left">
    <img src="./assets/images/JSP_Load_Err/JSP_Load_Err_01.png" alt="JSP_Load_Err_01">  
</div>

# Reference

> [[Spring] Spring Boot 3에서 JSP 설정방법](https://velog.io/@rhkdbtj/Spring-Spring-boot-3%EC%97%90%EC%84%9C-jsp-%EC%84%A4%EC%A0%95%EB%B0%A9%EB%B2%95)
