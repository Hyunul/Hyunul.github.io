---
title: "[JSTL] JSTL이 필요한 이유와 기본 태그 문법"
date: 2024-07-08 16:13:45 +09:00
categories: [Tip]
tag: [JSTL, JSP, View]
---

## JSTL이란?

**JSTL**은 **JavaServer Pages Standard Tag Library**의 약자로, JSP에서 자바 코드를 직접 섞기보다 HTML에 가까운 태그 형태로 로직을 표현하도록 돕는 라이브러리다.
HTML만으로는 반복문이나 조건문을 표현하기 어렵지만, JSTL을 사용하면 태그 기반으로 보다 읽기 쉬운 JSP를 작성할 수 있다.

## 왜 사용할까?

JSP는 HTML과 스크립트 코드가 뒤섞이기 쉬워서 가독성이 떨어지기 쉽다.
반면 JSTL을 사용하면 반복, 조건, 출력 같은 로직을 태그로 분리할 수 있어 구조가 더 명확해진다.
그래서 협업하거나 유지보수할 때 특히 유리하다.

## 기본 문법

- `c:`: core
- `fmt:`: formatting
- `fn:`: function
- `sql:`: database
- `x:`: XML 처리

---

## 자주 사용하는 태그

- `c:url`: URL 생성
- `c:out`: 값을 화면에 출력
- `c:set`: 값을 저장
- `c:forEach`: 반복문 제어
- `c:remove`: 저장된 값 제거
- `c:if`: 조건문 제어
- `c:choose`, `c:when`, `c:otherwise`: 복합 조건문 처리
- `c:import`: 다른 JSP 또는 리소스를 현재 화면에 포함
- `c:redirect`: 경로 이동

---

## `forEach` 사용 예시 (`varStatus`)

`Ex) items = [0, 1, 2, 3, 4, 5]`

```jsp
<c:forEach items="${items}" var="item" varStatus="status">
    ${status.current}<br/> <!-- 현재 아이템 -->
    ${status.index}<br/> <!-- 0, 1, 2, 3, 4, 5 -->
    ${status.count}<br/> <!-- 1, 2, 3, 4, 5, 6 -->
    ${status.first}<br/> <!-- index == 0 일 때 true -->
    ${status.last}<br/> <!-- index == 5 일 때 true -->
    ${status.begin}<br/> <!-- 시작값 -->
    ${status.end}<br/> <!-- 끝값 -->
    ${status.step}<br/> <!-- 증가값 -->
</c:forEach>
```
