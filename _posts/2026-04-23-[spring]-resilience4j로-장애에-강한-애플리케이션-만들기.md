---
title: "[Spring] Resilience4j로 장애에 강한 애플리케이션 만들기"
date: 2026-04-23 15:30:00 +09:00
categories: [BE]
tag: [Spring, Resilience4j, CircuitBreaker, MSA, 장애대응]
---

## 서론

MSA(MicroService Architecture)로 서비스를 쪼개고 나면 "한 서비스의 장애가 다른 서비스를 어떻게 전파시키지 않을 것인가"라는 문제가 생긴다. 결제 서비스가 응답을 못하면 주문 서비스의 스레드가 전부 그쪽으로 묶이고, 결국 주문 서비스까지 죽어버리는 캐스케이딩 장애는 MSA의 고전적인 실패 패턴이다.

이런 문제를 막기 위한 패턴들(Circuit Breaker, Retry, Bulkhead, Rate Limiter 등)을 자바/스프링 생태계에서 가장 널리 쓰는 라이브러리가 **Resilience4j**다. 과거 Netflix의 Hystrix가 사실상 표준이었지만 2018년 유지보수 모드로 전환된 이후, Resilience4j가 자연스럽게 후계자 자리를 잡았다.

이 글에서는 Resilience4j가 왜 Hystrix를 대체했는지부터, 핵심 모듈 6가지의 동작 원리, Spring Boot와의 통합, 그리고 실제 운영에서 주의할 포인트까지 정리한다.

## 본론

### 왜 Hystrix가 아니라 Resilience4j인가

Hystrix는 아키텍처적으로 "모든 보호 대상 호출을 별도 스레드풀로 감싸는" 스레드 격리 모델에 강하게 의존했다. 이 방식은 동기 블로킹 I/O 시대에는 합리적이었지만, 다음과 같은 한계가 있었다.

- **스레드풀 오버헤드**: 호출마다 컨텍스트 스위칭 + 별도 스레드 상태 관리 비용 발생
- **리액티브 스택과의 불일치**: 비동기/논블로킹 코드에서 스레드 격리 자체가 의미가 약해짐
- **RxJava 1.x 의존**: 2018년 기준 이미 구버전이 된 RxJava에 강결합
- **무거운 설정**: 애노테이션 + Command 패턴 기반으로 러닝 커브가 큼

Resilience4j는 이 지점들을 모두 다르게 설계했다.

- **함수형 래핑**: `Supplier`, `Function`을 데코레이트하는 방식이라 호출당 스레드 없이 동작 가능
- **모듈 분리**: CircuitBreaker, Retry, RateLimiter 등이 각각 독립 JAR. 필요한 것만 import
- **Vavr → 제로 의존성**: 초기엔 Vavr에 의존했지만 2.x부터는 순수 자바 함수형 API만 사용
- **리액티브 지원**: Project Reactor, RxJava 2/3 어댑터가 공식 제공

### 핵심 모듈 6가지

Resilience4j는 "하나의 큰 프레임워크"가 아니라 조합 가능한 6개의 독립 모듈로 구성된다.

| 모듈 | 역할 | 비유 |
| --- | --- | --- |
| `CircuitBreaker` | 실패율 임계치 초과 시 호출 차단 | 두꺼비집 |
| `Retry` | 실패한 호출을 정책에 따라 재시도 | 재전송 큐 |
| `RateLimiter` | 일정 시간당 호출 수 제한 | 티켓 게이트 |
| `Bulkhead` | 동시 실행 수 제한(격벽) | 선박의 격벽 |
| `TimeLimiter` | 호출 타임아웃 강제 | 알람 시계 |
| `Cache` | JCache 기반 결과 캐싱 | 브라우저 캐시 |

이 중에서 가장 핵심이 되는 `CircuitBreaker`부터 살펴본다.

### CircuitBreaker: 3가지 상태 머신

`CircuitBreaker`는 명확한 상태 머신(state machine)이다. 내부적으로 슬라이딩 윈도우(sliding window)에 최근 호출들의 성공/실패를 기록하고, 통계에 따라 상태를 전이시킨다.

- **CLOSED**: 정상 상태. 모든 호출이 그대로 대상 서비스로 전달된다.
- **OPEN**: 실패율이 임계치를 넘은 상태. 호출이 즉시 `CallNotPermittedException`으로 거부된다.
- **HALF_OPEN**: `OPEN`에서 일정 시간이 지난 뒤 제한된 수의 테스트 호출만 허용하는 상태. 이 호출들의 결과로 다시 `CLOSED`/`OPEN`을 결정한다.

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)                               // 실패율 50% 초과 시 OPEN
    .slowCallRateThreshold(50)                              // 느린 호출 비율 50% 초과 시 OPEN
    .slowCallDurationThreshold(Duration.ofSeconds(2))       // 2초 넘으면 "느린 호출"
    .waitDurationInOpenState(Duration.ofSeconds(30))        // OPEN 유지 시간
    .permittedNumberOfCallsInHalfOpenState(5)               // HALF_OPEN에서 허용할 테스트 호출 수
    .slidingWindowType(SlidingWindowType.COUNT_BASED)
    .slidingWindowSize(100)                                 // 최근 100개 호출 기준 통계
    .minimumNumberOfCalls(20)                               // 최소 20개 이상일 때만 판단
    .build();

CircuitBreaker cb = CircuitBreaker.of("paymentService", config);

Supplier<Payment> decorated = CircuitBreaker
    .decorateSupplier(cb, () -> paymentClient.charge(orderId));

Payment result = Try.ofSupplier(decorated)
    .recover(throwable -> Payment.fallback())
    .get();
```

여기서 `minimumNumberOfCalls`가 중요하다. 호출이 5건뿐인데 그 중 3건이 실패했다고 해서 서킷을 열어버리면 노이즈 레벨이 너무 높다. 의미 있는 통계가 쌓인 뒤부터 판단하게 해야 한다.

슬라이딩 윈도우는 `COUNT_BASED`(최근 N건)와 `TIME_BASED`(최근 N초간)를 선택할 수 있는데, 트래픽이 꾸준하면 `COUNT_BASED`, 트래픽이 들쭉날쭉하면 `TIME_BASED`가 맞다.

### Retry: 무작정 재시도는 장애를 키운다

Retry는 단순하지만 잘못 쓰면 오히려 장애를 확산시킨다. 대상 서비스가 이미 과부하로 느려졌는데, 클라이언트 전체가 동시에 재시도를 때리면 부하가 배가 된다(**retry storm**).

```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(500))
    .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
        500,    // 초기 500ms
        2.0,    // 지수 배수
        0.5     // ±50% 지터
    ))
    .retryOnException(e -> e instanceof IOException)
    .retryOnResult(response -> ((HttpResponse) response).status() == 503)
    .build();
```

핵심은 **exponential backoff + jitter**다. 지수 백오프만 쓰면 모든 클라이언트가 같은 타이밍에 재시도해 "재시도 폭풍"이 그대로 유지된다. 랜덤 지터를 넣어 타이밍을 흩어야 한다.

또한 **Idempotent한 호출에만** Retry를 붙여야 한다. 결제 승인 같은 비멱등 연산을 아무 생각 없이 재시도하면 이중 결제가 생긴다. 불가피하게 비멱등 호출을 재시도해야 한다면 Idempotency-Key 헤더와 함께 설계해야 한다.

### Bulkhead: 하나의 느린 호출이 전체를 삼키지 않게

`Bulkhead`는 특정 다운스트림 호출에 쓸 수 있는 동시 실행 수를 제한한다. 결제 API가 갑자기 느려져도 그쪽으로 20개까지만 동시 호출이 가능하다면, 나머지 톰캣 스레드는 다른 요청(상품 조회 등)을 계속 처리할 수 있다.

- `SemaphoreBulkhead`: 세마포어로 동시 실행 수만 제한. 가볍다.
- `ThreadPoolBulkhead`: 별도 스레드풀 + 큐를 할당. 비동기 실행, 완전한 격리.

```java
BulkheadConfig semaphoreConfig = BulkheadConfig.custom()
    .maxConcurrentCalls(20)
    .maxWaitDuration(Duration.ofMillis(100))
    .build();

Bulkhead bulkhead = Bulkhead.of("paymentService", semaphoreConfig);
```

Hystrix가 무조건 스레드풀 격리를 강제했던 것과 달리, Resilience4j는 세마포어 방식을 기본으로 두고 필요할 때만 스레드풀 모드를 쓸 수 있게 한다. 대부분의 경우 세마포어로 충분하다.

### TimeLimiter: 무한 대기를 끊는다

`TimeLimiter`는 `CompletableFuture` 형태의 비동기 호출에 타임아웃을 강제한다. HTTP 클라이언트가 자체 타임아웃을 가지고 있더라도, 비즈니스 관점에서 "이 호출은 최대 2초"라는 상한을 별도로 둘 수 있다.

```java
TimeLimiterConfig config = TimeLimiterConfig.custom()
    .timeoutDuration(Duration.ofSeconds(2))
    .cancelRunningFuture(true)
    .build();
```

### Spring Boot 통합: 애노테이션 기반 설정

`resilience4j-spring-boot3` 스타터를 쓰면 설정은 `application.yml`에, 적용은 애노테이션에 맡길 수 있다.

```yaml
resilience4j:
  circuitbreaker:
    instances:
      paymentService:
        failureRateThreshold: 50
        slowCallRateThreshold: 50
        slowCallDurationThreshold: 2s
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 5
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 100
        minimumNumberOfCalls: 20
  retry:
    instances:
      paymentService:
        maxAttempts: 3
        waitDuration: 500ms
        exponentialBackoffMultiplier: 2
```

```java
@Service
public class PaymentService {

    @CircuitBreaker(name = "paymentService", fallbackMethod = "chargeFallback")
    @Retry(name = "paymentService")
    @TimeLimiter(name = "paymentService")
    public CompletableFuture<Payment> charge(Long orderId) {
        return paymentClient.chargeAsync(orderId);
    }

    private CompletableFuture<Payment> chargeFallback(Long orderId, Throwable t) {
        return CompletableFuture.completedFuture(Payment.pending(orderId));
    }
}
```

### 데코레이터 적용 순서

여러 애노테이션을 함께 쓸 때 적용 순서는 중요하다. Resilience4j Spring Boot 통합은 기본적으로 다음 순서로 데코레이터를 합성한다.

```text
Retry ( CircuitBreaker ( RateLimiter ( TimeLimiter ( Bulkhead ( Call ) ) ) ) )
```

즉 가장 바깥이 `Retry`, 가장 안쪽이 실제 호출이다. 이 순서가 의미하는 바는 "한 번의 재시도 안에서 서킷 브레이커와 레이트 리미터가 판단되고, 실제 호출은 타임아웃과 벌크헤드로 보호받는다"는 것이다. 이 순서를 뒤집어야 하는 경우(예: Retry 바깥에 CircuitBreaker)는 프로그래매틱 조합으로 직접 구성해야 한다.

### 메트릭과 관측성

`resilience4j-micrometer` 모듈은 모든 인스턴스의 상태를 Micrometer 메트릭으로 노출한다. Prometheus + Grafana 조합을 쓰고 있다면 다음 지표만 보면 된다.

- `resilience4j_circuitbreaker_state`: 현재 상태(0=CLOSED, 1=OPEN, 2=HALF_OPEN)
- `resilience4j_circuitbreaker_calls`: 성공/실패/느린 호출 카운터
- `resilience4j_retry_calls`: 재시도 성공/실패 횟수
- `resilience4j_bulkhead_available_concurrent_calls`: 남은 동시 호출 가능 수

서킷이 `OPEN`으로 전이되는 순간을 알람으로 잡아야 실제 운영에서 가치가 있다. 상태 전이 이벤트는 `CircuitBreaker.getEventPublisher().onStateTransition(...)`로도 구독 가능하다.

## 정리

- **Resilience4j는 Hystrix의 후계자**다. 함수형 데코레이터 기반 설계로 가볍고, 리액티브 스택과도 잘 맞는다.
- **CircuitBreaker, Retry, RateLimiter, Bulkhead, TimeLimiter, Cache** 6개의 독립 모듈을 조합해 쓴다. 모든 걸 한 번에 도입하지 말고, 서킷 브레이커 → 타임아웃 → 리트라이 순서로 적용하는 게 안전하다.
- **Retry는 idempotent 호출에만** 붙이고, 반드시 **exponential backoff + jitter**와 함께 써야 한다. 그렇지 않으면 재시도가 장애를 키운다.
- **`minimumNumberOfCalls`를 반드시 설정**하자. 호출 표본이 작을 때 서킷이 열려 노이즈로 장애처럼 보이는 상황을 막아준다.
- **메트릭 대시보드와 알람을 함께 구축**해야 의미가 있다. 서킷이 열린 걸 로그 뒤져서 발견하는 순간 이미 늦다.
- 스프링 부트 환경이라면 `resilience4j-spring-boot3` + `application.yml` + 애노테이션 조합이 가장 부담이 적다.

"장애에 강한 시스템"은 장애가 안 나는 시스템이 아니라, 장애가 나도 빠르게 격리되고 빠르게 회복되는 시스템이다. Resilience4j는 그걸 위한 가장 표준적인 도구다.

## Reference

- [Resilience4j 공식 문서](https://resilience4j.readme.io/)
- [Resilience4j GitHub](https://github.com/resilience4j/resilience4j)
- [Spring Boot 3 + Resilience4j 가이드](https://resilience4j.readme.io/docs/getting-started-3)
- [Hystrix 유지보수 모드 전환 공지](https://github.com/Netflix/Hystrix/blob/master/README.md)
- [Martin Fowler - Circuit Breaker 패턴](https://martinfowler.com/bliki/CircuitBreaker.html)
