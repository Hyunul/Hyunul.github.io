---
title: "[JPA] 컬럼명이 snake_case로 바뀌는 문제 해결"
date: 2024-10-15 08:16:35 +09:00
categories: [Error]
tag: [JPA, Hibernate, Naming Strategy]
---

## 문제 상황

JPA를 사용할 때 `@Entity` 또는 `@Column`에 카멜 케이스 이름을 사용했는데, 실제 쿼리에서는 스네이크 케이스로 변환되어 나가는 경우가 있었다.

```java
@Column(name = "userId")
// userId가 user_id로 변경되어 쿼리가 생성됨.
```

## 해결 방법

Hibernate의 네이밍 전략을 명시적으로 지정하면 자동 변환을 막을 수 있다.

```properties
# 언더바 자동 변환 방지
# Java에서 선언한 이름을 가능한 그대로 사용

# 명시적으로 지정하지 않은 이름에 적용할 기본 전략
spring.jpa.hibernate.naming.implicit-strategy=org.hibernate.boot.model.naming.ImplicitNamingStrategyLegacyJpaImpl

# 물리 테이블/컬럼명에 최종 적용되는 전략
spring.jpa.hibernate.naming.physical-strategy=org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
```
