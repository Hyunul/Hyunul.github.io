---
title: "[Error] JPA에서 Camel 형태의 칼럼이 Snake 형태의 칼럼으로 자동 변경될 때"
date: 2024-10-15 08:16:35 +09:00
categories: [Error]
tag: [Spring, JPA]
---

## 문제 상황

JPA 사용 시 @Entity 또는 @Column 에서 카멜(Camel) 표기법 사용 시 JPA가 해당 칼럼의 이름을 스네이크(Snake) 표기법으로 변경해서 쿼리 생성.

```java
@Column(name = "userId")
// userId가 user_id로 변경되어 쿼리가 생성됨.
```

## 해결 방법

```properties
# 언더바 자동변경 방지
# java에서 선언했던 변수 이름을 테이블 매핑 시 그대로 사용

# value 등을 통해서 명시적으로 지정하지 않은 테이블들의 규칙 지정
spring.jpa.hibernate.naming.implicit-strategy=org.hibernate.boot.model.naming.ImplicitNamingStrategyLegacyJpaImpl

# 모든 규칙이 적용되고 가장 마지막에 적용되는 규칙이므로 공통적인 DB규칙을 지정할 때 사용
spring.jpa.hibernate.naming.physical-strategy=org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
```
