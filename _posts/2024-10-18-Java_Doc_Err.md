---
title: "[Java] JavaDoc 생성 시 MS949 인코딩 오류 해결 방법"
date: 2024-10-18 16:16:59 +09:00
categories: [Error]
tag: [Java, JavaDoc, Encoding, Error]
---

## 문제 상황

프로젝트 결과 보고서에 첨부할 Manual을 작성하던 중, JavaDoc을 생성해서 제출해야 하는 상황이 생겼다.
처음 해보는 작업이다 보니 두 가지 문제를 겪었다.

## 첫 번째 문제

JavaDoc 출력 경로를 내가 보기 편한 폴더로 바꿨다가 오히려 더 헷갈렸다.
결론부터 말하면, 처음에는 IDE가 잡아주는 기본 출력 경로를 그대로 사용하는 편이 훨씬 안전했다.

> 정확한 내부 동작까지 확인해보진 않았지만, 출력 경로를 임의로 바꾸면서 예상치 못한 문제가 생겼다. 괜히 건드렸다가 시간을 꽤 썼다.

## 두 번째 문제

여기가 진짜 핵심인데, 주석에 들어간 한글이 깨지면서 아래와 같은 에러가 발생했다.

<div align="left">
    <img src="./assets/images/Java_Doc_Err/JDE_01.png" alt="JDE_01">
</div>

보자마자 인코딩 문제라는 걸 알 수 있었다.
해결 방법은 간단했다. JavaDoc Export 과정에서 `VM options`에 아래 값을 넣고 `Finish`를 누르면 된다.

<div align="left">
    <img src="./assets/images/Java_Doc_Err/JDE_02.png" alt="JDE_02">
</div>

`-charset UTF-8 -encoding UTF-8`
