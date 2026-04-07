---
title: "[Deployment] loslung 온프레미스 배포를 Docker Compose와 Apache로 구성한 과정"
date: 2026-04-02 09:30:00 +09:00
categories: [BE]
tag: [Project, Deployment, Docker, Apache, On-Premise]
---

## 서론

`loslung`의 배포 히스토리를 다시 보면, 가장 먼저 정리해야 했던 것은 Docker 자체가 아니라 요청 경로였다.  
이 프로젝트는 단순히 "프런트 1개, 백엔드 1개" 구조가 아니라, **Next.js Route Handler가 처리해야 하는 API와 Spring Boot가 처리해야 하는 API가 공존하는 구조**였기 때문이다.

2026년 4월 2일 [PR #1](https://github.com/Hyunul/loslung/pull/1)과 [PR #7](https://github.com/Hyunul/loslung/pull/7)을 기준으로, `loslung`은 온프레미스 환경에서 `Docker Compose + Apache reverse proxy` 구조로 정리되기 시작했다.

이번 글에서는 그 과정에서 어떤 식으로 배포 구성을 잡았는지, 그리고 왜 프록시 설계가 먼저 중요했는지를 코드와 함께 정리한다.

## 문제 상황

처음에는 배포만 되면 끝일 것처럼 보였지만, 실제로는 아래 문제를 먼저 해결해야 했다.

- PostgreSQL, Spring Boot, Next.js를 함께 띄울 운영 구성이 필요함
- 헬스체크와 컨테이너 의존성을 명확히 해야 함
- `/api/me/*` 같은 일부 경로는 Next.js가 처리하고, 나머지 `/api/*`는 백엔드가 처리해야 함
- HTTPS 종료와 리버스 프록시는 Apache가 맡아야 함

즉, 배포 문제라기보다 **서비스 경계와 요청 소유권을 다시 정의하는 문제**에 가까웠다.

## Docker Compose 구성

먼저 컨테이너 구성은 `postgres`, `backend`, `frontend` 세 서비스로 정리되었다.

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-loslung}
      POSTGRES_USER: ${POSTGRES_USER:-loslung}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}

  backend:
    build:
      context: ./backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DB_URL: jdbc:postgresql://postgres:5432/${POSTGRES_DB:-loslung}
      DB_USERNAME: ${POSTGRES_USER:-loslung}
      DB_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}
      SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE:-prod}
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8080/api/health"]

  frontend:
    build:
      context: ./frontend
    depends_on:
      backend:
        condition: service_healthy
    environment:
      NODE_ENV: production
      BACKEND_URL: http://backend:8080/api
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "/dev/null", "http://localhost:3000/api/health"]
```

여기서 핵심은 두 가지였다.

1. 백엔드는 DB health check 이후에만 뜨도록 `depends_on`을 둔다.
2. 프런트는 백엔드 health check 이후에 올라오도록 연결한다.

이렇게 해야 "컨테이너는 떴지만 실제 서비스는 아직 안 뜬 상태"를 조금 더 줄일 수 있었다.

## Apache 리버스 프록시 설계

이 프로젝트에서 더 중요한 것은 Apache 설정이었다.  
이유는 모든 `/api/*` 요청이 백엔드로 가는 구조가 아니었기 때문이다.

```apache
<VirtualHost *:443>
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"

    # Frontend internal API routes -> Next.js route handlers
    ProxyPass /api/me/ http://127.0.0.1:3100/api/me/
    ProxyPassReverse /api/me/ http://127.0.0.1:3100/api/me/

    # API -> backend (Spring Boot)
    ProxyPass /api/ http://127.0.0.1:8100/api/
    ProxyPassReverse /api/ http://127.0.0.1:8100/api/

    # Everything else -> frontend
    ProxyPass / http://127.0.0.1:3100/
    ProxyPassReverse / http://127.0.0.1:3100/
</VirtualHost>
```

이 설정이 중요한 이유는 다음과 같다.

- 로그인 사용자 관련 API 중 일부는 Next.js Route Handler가 처리한다.
- 일반 API는 Spring Boot가 처리한다.
- 같은 `/api/*`라도 모두 같은 프로세스로 보내면 안 된다.

즉, Docker Compose가 서비스 단위 구성을 정리했다면, Apache는 **요청 단위 구성을 정리한 셈**이었다.

## 배포 과정에서 얻은 교훈

이번 배포 흐름에서 가장 크게 배운 점은, 배포는 "컨테이너를 띄우는 작업"이 아니라는 점이었다.

실제로 먼저 정리해야 했던 것은 아래와 같았다.

- 어떤 서비스가 어떤 경로를 처리하는가
- health check는 어디를 기준으로 둘 것인가
- 프록시가 서비스 구조를 정확히 반영하고 있는가
- 환경변수와 기동 순서가 실제 의존 관계와 맞는가

특히 이 프로젝트처럼 Next.js와 Spring Boot가 동시에 API를 가지는 구조에서는, 프록시 규칙이 곧 서비스 구조라고 봐도 과언이 아니었다.

## 정리

`loslung`의 배포 히스토리를 돌아보면, 초기 배포의 핵심은 Docker를 도입한 것보다 **서비스 경계를 배포 구조에 반영한 것**에 있었다.

- Docker Compose로 서비스 단위를 정리하고
- Apache로 요청 경계를 나누고
- health check로 기동 순서를 고정했다

배포 문제를 만났을 때 "컨테이너가 왜 안 뜨지?"부터 보기 쉽지만, 실제로는 "이 요청이 원래 어디로 가야 하지?"를 먼저 따져보는 편이 더 빠를 때가 많다.

## Reference

- [PR #1 - chore(deploy): add on-premise deployment scripts](https://github.com/Hyunul/loslung/pull/1)
- [PR #7 - chore(deploy): Docker Compose 및 On-Premise 배포 환경 구성](https://github.com/Hyunul/loslung/pull/7)
