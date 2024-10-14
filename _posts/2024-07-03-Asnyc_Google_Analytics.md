---
title: "[Blog] 깃허브 블로그의 방문자 수를 구해보자."
date: 2024-07-03 07:28:22 +09:00
categories: [Tip]
tag: [Blog, GA]
---

Github Pages 기반으로 운영되는 블로그들은 Tistory나 Velog처럼 방문자 수 통계가 제공되지 않는다.  
따라서 이 글을 통해 Google Analytics (이하 "GA")를 Github 블로그에 연동시켜 방문자 수 통계 기능을 추가할 것이다.

## **설정 방법**

> 진짜 별거 없는데 빠르게 설명해주겠다.

### **1. 측정 ID 확인**

GA를 내 블로그에 적용시키려면 구글에서 발급해주는 `측정 ID`라는 것을 내 블로그에 심을 필요성이 있다.

GA 홈에 들어가게 되면 왼쪽 하단에 톱니바퀴 모양의 `관리` 탭이 보일 것이다.  
이 친구를 누르면 여러 탭들이 보이는데, 그 중 `데이터 수집 및 수정` 탭의 `데이터 스트림`을 누르게 되면 내가 등록한 블로그가 나온다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_01.png" alt="GA_01">  
</div>

이를 클릭한다면 아래의 사진과 같이 나오는데, 여기서 "측정 ID" 이놈이 중요하니 복사해주자.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_01.png" alt="GA_02">  
</div>

### **2. 측정 ID 설정**

이제 이놈을 어디에다가 쓰느냐... 다음 사진은 우리의 Jekyll 디렉토리에 존재하는 `_config.yml` 파일이다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_03.png" alt="GA_03">  
</div>

파일을 스크롤하여 내리다보면 사진에 해당하는 부분이 나올텐데, `provider`와 `google`의 `id`에 아까 복사한 측정 ID를 붙여넣으면 모든 설정이 끝난다.

### **3. 테스트**

모든 설정이 끝났으니 GA가 제대로 동작하는지 살펴보자.
내 블로그의 방문자 수는 애널리틱스 사이드바의 `보고서` 탭에서 확인이 가능하다.

<div align="left">
    <img src="./assets/images/Google Analytics/GA_04.png" alt="GA_04">  
</div>

정상적으로 작동하는 것을 확인할 수 있었다.

하나하나 나만의 블로그가 완성되어가는 모습을 보니, 입꼬리가 점점 1시와 11시로 올라가는 내 모습을 볼 수 있었다..

다음 포스팅은 내 블로그의 글을 검색 엔진에 노출시키는 방법에 대해서 작성해보겠다.
