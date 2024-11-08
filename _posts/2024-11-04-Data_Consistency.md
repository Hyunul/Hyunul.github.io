---
title: "[CS] 동시성 이슈를 해결하는 방법들 (feat. 데이터 정합성)"
date: 2024-11-04 07:23:33 +09:00
categories: [BE]
tag: [Spring, BE, CS, DB, JPA, Java]
---

CS에서 동시성이란 프로그램이나 알고리즘의 여러 부분이나 단위가 `결과에 영향을 주지 않고 순서와 상관없이 또는 부분적으로 실행`될 수 있는 기능을 말한다.  
동시성과 교착 상태(Dead Lock)을 설명하는 예시로 유명한 `식사하는 철학자 문제`가 있다.

> 다섯 명의 철학자가 하나의 원탁에 앉아 식사를 한다. 각각의 철학자들 사이에는 포크가 하나씩 있고, 앞에는 접시가 있다. 접시 안에 든 요리는 포크를 두개 사용하여 먹어야만 하는 스파게티 이다.
>
> 그리고 각각의 철학자는 다른 철학자에게 말을 할 수 없으며, 번갈아가며 각자 식사하거나 생각하는 것만 가능하다. 따라서 식사를 하기 위해서는 왼쪽과 오른쪽의 인접한 철학자가 모두 식사를 하지 않고 생각하고 있어야만 한다.
>
> 또한 식사를 마치고 나면, 왼손과 오른손에 든 포크를 다른 철학자가 쓸 수 있도록 내려놓아야 한다. 이 때, 어떤 철학자도 굶지 않고 식사할 수 있도록 하는 방법은 무엇인가?

## 문제상황

2명 이상의 사용자가 거의 동시에 요청을 보내거나 서버에 지연이 생겨 처리가 늦어질 경우, 데이터의 정합성에 문제가 생길 수도 있다.

## 문제 해결 방안

### 비관적 락 (Pessimistic Lock)

- 데이터에 락을 걸어서 정합성을 맞추는 방법
- Exclusive Lock을 걸게 되면 다른 트랜잭션에서는 락이 해제되기 전까지 데이터를 가져갈 수 없게 됨.
- 자원 요청에 따른 `동시성 문제가 발생할 것이라고 예상`하고 락을 걸어버림
- 데드락 발생 가능
- `트랜잭션을 롤백할 필요가 없으므로 데이터 충돌이 많을 때 적합`  
  JPA에서는 다음과 같이 사용할 수 있다.

```java
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select s from Stock s where s.id = :id")
    Stock findByIdWithPessimisticLock(Long id);
```

### 낙관적 락 (Optimistic Lock)

- Lock을 이용하지 않고 `버전`을 이용함으로써 정합성을 맞추는 방법
- 데이터를 읽은 후에 update를 수행할 때 현재 내가 읽은 버전이 맞는지 확인하며 update
- 자원에 락을 걸어서 선점하지 않고, 동시성 문제가 발생하면 그때가서 처리
- 내가 읽은 버전에서 revision이 생겼을 경우, application에서 다시 읽은 후에 작업을 수행하는 롤백 작업 필요
- `트랜잭션의 롤백에 대한 비용이 비싸므로 충돌이 적을 때 적합`

JPA에서는 다음과 같이 사용할 수 있다.

```java
    @Lock(LockModeType.OPTIMISTIC)
    @Query("select s from Stock s where s.id = :id")
    Stock findByIdWithOptimisticLock(Long id);
```

위와 같은 DB에 대한 Lock 외에도 Redis나 ZooKeeper와 같은 분산 락을 통한 해결도 가능하지만, 이는 추가 공부를 통해 잘 알게 된다면 해당 게시글을 업데이트하도록 하겠다.