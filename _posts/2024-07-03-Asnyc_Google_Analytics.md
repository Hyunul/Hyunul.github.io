---
title: "[Blog] GitHub Pages 블로그에 Google Analytics 방문자 통계 연동하기"
date: 2024-07-03 07:28:22 +09:00
categories: [Tip]
tag: [Blog, GitHub Pages, Google Analytics]
---

Github Pages 기반으로 운영되는 블로그는 Tistory나 Velog처럼 방문자 수 통계를 기본 제공하지 않는다.
그래서 이번 글에서는 Google Analytics(이하 `GA`)를 GitHub 블로그에 연동해 방문자 통계를 확인하는 방법을 정리해보려 한다.

## 설정 방법

> 생각보다 설정은 간단하다.

### 1. 측정 ID 확인

GA를 블로그에 적용하려면 구글에서 발급하는 `측정 ID`가 필요하다.

GA 홈에 들어가면 왼쪽 하단에 톱니바퀴 모양의 `관리` 메뉴가 보인다.
여기서 `데이터 수집 및 수정` 아래의 `데이터 스트림`을 선택하면 등록한 블로그를 확인할 수 있다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_01.png" alt="GA_01">
</div>

해당 항목을 클릭하면 아래와 같은 화면이 나오는데, 여기서 `측정 ID`를 복사해두면 된다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_02.png" alt="GA_02">
</div>

### 2. 측정 ID 설정

이제 복사한 값을 Jekyll 설정 파일에 넣어주면 된다. 아래 이미지는 블로그 루트에 있는 `_config.yml` 파일이다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_03.png" alt="GA_03">
</div>

파일을 내려보면 해당 위치가 보이는데, `provider`는 `google`로 두고 `id`에 복사한 측정 ID를 붙여넣으면 설정이 끝난다.

### 3. 테스트

설정이 끝났다면 GA가 제대로 동작하는지 확인해보자.
블로그 방문 통계는 애널리틱스 사이드바의 `보고서` 탭에서 확인할 수 있다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_04.png" alt="GA_04">
</div>

정상적으로 동작하는 것을 확인했다.

하나씩 내 블로그가 완성되어가는 모습을 보니 꽤 뿌듯했다.
다음에는 블로그 글을 검색 엔진에 노출시키는 방법도 정리해볼 생각이다.
