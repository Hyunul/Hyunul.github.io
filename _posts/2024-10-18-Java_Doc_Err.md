---
title: "[Spring] Java Doc 생성 오류 (error: unmappable character for encoding MS949)"
date: 2024-10-18 16:16:59 +09:00
categories: [Error]
tag: [Spring]
---

## 문제상황

프로젝트의 결과 보고서를 작성하던 중 Manual을 작성하려고 하는 상황이다.  
상사로부터 JavaDoc을 생성해서 제출하라는 업무 지시를 받았다.  
생전 처음 접하는 JavaDoc, 나는 두 가지의 에러를 마주치게 되었다.

## 첫번째 문제

어차피 작성된 파일은 지정된 폴더로 옮길건데 내가 찾기 편한 폴더에 만들었다가 옮겨도 되지 않을까??  
안된다. JavaDoc의 출력 디렉터리(만들어지는 곳)는 건드리지 말자... 이거 건드렸다가 30분이 사라졌다.

> 추측이긴 한데 같은 패키지 안에서 만들어지도록 설계되어있나보다. 찾아보진 않았다.

## 두번째 문제

여기가 진짜 핵심인데 주석에 달린 한글들이 자꾸 깨져서 에러가 발생한다.

<div align="left">
    <img src="./assets/images/Java_Doc_Err/JDE_01.png" alt="JDE_01">  
</div>

누가봐도 인코딩 에러다. 해결 시작하자.  
Java_Doc을 생성하기 위해 Export를 진행하다 보면 다음과 같은 창이 뜨는데, 해결 방법은 정말 간단하다.  
VM options에 다음 명령어를 기입하고 Finish를 누르면 간단히 해결.

<div align="left">
    <img src="./assets/images/Java_Doc_Err/JDE_02.png" alt="JDE_02">  
</div>
`-charset UTF-8 -encoding UTF-8`