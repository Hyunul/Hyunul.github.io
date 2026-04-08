---
title: "[Trouble Shooting] Public Key Retrieval is not allowed 해결"
date: 2025-11-14 09:19:20 +09:00
categories: [Error]
tag: [Troubleshooting]
---

### [ 문제 상황 ]

JDBC URL로 Spring Boot와 로컬 MySQL을 연결하던 중 아래와 같은 오류가 발생.

```
Caused by: java.sql.SQLNonTransientConnectionException: Public Key Retrieval is not allowed
```

---

### [ 해결 방안 ]

이 오류는 MySQL 8.0 버전 이상에서 발생하는 오류이다.

더보기

기본적으로 MySQL DB에 접속하기 위해서 url, username, password 세 가지가 필요했으나, MySQL 8.0 버전부터 보안적인 이슈로 useSSL 옵션에 대한 설정이 필요해졌다.

useSSL : DB에 SSL로 연결

allowPublicKeyRetrieval : 서버에서 RSA 공개키를 검색하거나 가져와야하는지

즉, JDBC URL로 MySQL에 접속을 시도하는 나와 같은 케이스는 URL에 useSSL 옵션을 추가해주면 된다.

```
// useSSL=false&allowPublicKeyRetrieval=true

// ex)
jdbc:mysql://localhost:3306/test_db?useSSL=false&allowPublicKeyRetrieval=true
```
