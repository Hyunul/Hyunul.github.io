---
title: (JSTL) JSTL 사용 이유, 기초 문법
date: 2024-07-08 16:13:45 +09:00
categories: [Tech, Web]
tag: [Spring]
---

# JSTL이란?
__JSTL__ 이란 __JavaServer Pages Standard Tag Library__ 의 약어로, Java 코드를 바로 사용하지 않고 HTML 태그 형태로 직관적인 코딩을 지원하는 라이브러리이다.  
일반적으로 HTML 태그만으로는 Java의 forEach 문과 같은 반복문을 사용할 수 없는데, JSTL 라이브러리를 사용한다면 HTML 태그 안에 직관적으로 쓰임새가 파악되는 반복문을 작성할 수 있게 된다.

# 왜 사용하나요?
흔히 사용하는 JSP는 HTML코드와 스크립트 코드가 섞이기에 __코드의 가독성__ 이 떨어진다. 반면에 JSTL을 사용하면 프로그래밍을 입문한 사람이라면 코드의 쓰임새를 직관적으로 이해할 수 있다는 장점이 있다.  
이로 인해 개발자가 아닌 HTML/CSS를 다루는 디자이너가 __간단한 코드 작업을 쉽게 수행하는 데 효과적__ 이다.

# 기본 문법
> - `c:` // 코어
> - `fmt:` // 포멧팅
> - `fn:` // 함수
> - `sql:` // 데이터베이스
> - `x:` // XML 처리

---

> - `c:url` // url 호출
> - `c:out` // 객체를 화면에 출력
> - `c:set` // 저장 영역에 객체를 저장
> - `c:forEach` // 반복문 제어
> - `c:remove` // 저장 영역에 객체를 삭제
> - `c:if` // 조건문 제어
> - `c:choose`, `c:when`, `c:otherewise` : 복합조건문 제어
> - `c:import!` : 다른 jsp화면을 현재 화면에 출력
> - `c:redirect` : 경로 이동

---

# forEach 사용 예시 (with. status)

`Ex) items = [0,1,2,3,4,5]`
```
<c:foreach items=”${items}” var=”item” varStatus=”status”>
    ${status.current}<br/>      <!– 현재 아이템 –>
    ${status.index}<br/>         0,1,2,3,4,5
    ${status.count}<br/>        1,2,3,4,5,6
    ${status.first}<br/>           index == 0일 때 true
    ${status.last}<br/>           index == 5일 때 true
    ${status.begin}<br/>        <!– 시작값 –>
    ${status.end}<br/>          <!– 끝값 –>
    ${status.step}<br/>         <!– 증가값 –>
< /c:forEach>
```