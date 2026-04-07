---
title: "[Database] PostgreSQL과 MySQL 차이점, 장단점, 선택 기준"
date: 2026-03-06 08:26:42 +09:00
categories: [BE]
tag: [Database, PostgreSQL, MySQL, RDBMS]
---

## 서론

백엔드 개발에서 데이터베이스는 시스템의 안정성과 확장성을 좌우하는 핵심 요소다.
관계형 데이터베이스(RDBMS) 중 가장 널리 사용되는 두 축은 PostgreSQL과 MySQL이다.
둘 다 강력하고 안정적인 데이터베이스이지만, 설계 철학과 강점은 분명히 다르다.

이번 글에서는 PostgreSQL과 MySQL의 주요 차이를 실무 관점에서 비교하고, 어떤 상황에서 각각이 더 잘 맞는지 정리해본다.

## 본론

PostgreSQL과 MySQL은 모두 오픈소스 관계형 데이터베이스이지만, 설계 원칙과 제공 기능에서 차이를 보인다.

### 1. PostgreSQL의 특징과 용도

**강점**

- **표준 SQL 준수와 높은 확장성**: SQL 표준을 엄격하게 따르며, `JSONB`, 지리 공간 데이터 등 다양한 타입과 함수를 지원한다.
- **강력한 ACID 보장**: 데이터 무결성이 중요한 시스템에서 특히 강점을 가진다.
- **복잡한 쿼리 처리에 강함**: 서브쿼리, 윈도우 함수, CTE 같은 기능을 활용한 분석 작업에 유리하다.
- **고급 기능 지원**: `MVCC` 기반 동시성 처리와 `PostGIS` 같은 확장 기능이 강력하다.

**주요 용도 및 추천 상황**

- 금융, 은행, ERP처럼 데이터 무결성이 최우선인 시스템
- 대규모 분석, BI, 데이터 웨어하우스
- GIS(지리 정보 시스템), 위치 기반 서비스
- 확장성과 커스터마이징이 중요한 엔터프라이즈 환경

**예시 쿼리**

```sql
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS running_total
FROM orders;
```

### 2. MySQL의 특징과 용도

**강점**

- **사용과 운영이 비교적 쉬움**: 설치와 관리가 단순한 편이고, 일반적인 웹 서비스에 빠르게 적용하기 좋다.
- **읽기 성능에 강점이 있음**: 조회가 많은 서비스에서 좋은 성능을 보여준다.
- **커뮤니티와 자료가 풍부함**: 오래된 생태계 덕분에 참고 자료와 해결 사례가 많다.
- **복제 구성이 비교적 쉬움**: 읽기 부하 분산과 고가용성 구성에 많이 활용된다.

**주요 용도 및 추천 상황**

- WordPress 같은 CMS 기반 웹 서비스
- 빠르게 개발하고 배포해야 하는 스타트업, 중소규모 프로젝트
- 조회 비중이 높은 블로그, 뉴스, 콘텐츠 서비스
- 일반적인 웹 호스팅 환경을 적극 활용해야 하는 경우

**예시 쿼리**

```sql
SELECT
    u.username,
    p.post_title,
    p.post_content
FROM users u
JOIN posts p ON u.user_id = p.author_id
WHERE u.is_active = TRUE;
```

### 3. 주요 차이점 요약

| 특징 | PostgreSQL | MySQL |
| :--- | :--------- | :---- |
| **SQL 표준** | 엄격한 준수, 높은 확장성 | 비교적 유연, 일부 표준 차이 존재 |
| **ACID** | 강력한 보장 | InnoDB 사용 시 강력 보장 |
| **성능 특성** | 복잡한 쿼리와 쓰기 작업에 강함 | 읽기 성능과 단순 쿼리에 강함 |
| **데이터 타입** | JSONB, 배열, 지리 공간 등 풍부함 | 일반적인 데이터 타입 중심 |
| **커뮤니티** | 개발자/전문가 중심 | 폭넓은 사용자층과 자료 |
| **라이선스** | PostgreSQL License | GPL 기반 배포 |

## 정리

PostgreSQL과 MySQL 중 어느 하나가 절대적으로 우월하다고 말하기는 어렵다.
중요한 것은 현재 서비스가 요구하는 데이터 특성, 트래픽 패턴, 운영 방식에 어떤 데이터베이스가 더 잘 맞는지 판단하는 일이다.

- **PostgreSQL**은 데이터 무결성, 복잡한 쿼리, 높은 확장성이 중요한 경우에 더 적합하다.
- **MySQL**은 빠른 개발, 쉬운 운영, 읽기 중심의 웹 서비스에 특히 효율적이다.

결국 데이터베이스 선택은 성능 비교표 하나로 끝나는 문제가 아니라, 서비스 특성과 팀의 운영 역량까지 함께 고려해야 하는 설계 결정이라고 생각한다.

## Reference

- [PostgreSQL vs MySQL: A Detailed Comparison - GeeksforGeeks](https://www.geeksforgeeks.org/postgresql-vs-mysql-a-detailed-comparison/)
- [What is the difference between PostgreSQL and MySQL? - IBM](https://www.ibm.com/topics/postgresql-vs-mysql)
