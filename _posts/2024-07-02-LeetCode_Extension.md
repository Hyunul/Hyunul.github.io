---
title: "[Git] LeetHub로 LeetCode 풀이를 GitHub에 자동 저장하기"
date: 2024-07-02 17:47:14 +09:00
categories: [Tip]
tag: [Git, GitHub, LeetCode, LeetHub]
---

"코테 준비해야지..."라는 생각은 대학생 때부터 늘 하고 있었다.
예전에는 백준으로 많이 연습했지만, 요즘은 주변에서 LeetCode를 더 자주 추천하는 분위기였다.
그래서 찾아본 것이 `LeetHub`였다. 이 확장 프로그램은 LeetCode 문제를 제출했을 때 풀이를 내 GitHub 레포지토리에 자동으로 커밋해준다.

## 설정 방법

### 1. 확장 프로그램 추가

먼저 크롬 웹 스토어에서 `LeetHub V3`를 설치한다.

<div align="left">
    <img src="./assets/images/LeetHub/LeetHub_01.png" alt="LeetHub_01">
</div>

설치 후 크롬 오른쪽 상단의 확장 프로그램 버튼을 누르면 아래와 같은 창이 뜬다.

<div align="left">
    <img src="./assets/images/LeetHub/LeetHub_02.png" alt="LeetHub_02">
</div>

### 2. GitHub 인증

한 번 더 클릭하면 다음 화면으로 넘어가는데, 여기서 `Authenticate`를 눌러 인증을 진행한다.

<div align="left">
    <img src="./assets/images/LeetHub/LeetHub_03.png" alt="LeetHub_03">
</div>

### 3. GitHub Repo 설정

로그인이 끝나면 설정 화면이 나타난다.
첫 번째 항목에서는 `Create a new Private Repository`를 선택하고, 두 번째 항목에는 원하는 레포지토리 이름을 입력한 뒤 `Get Started`를 누르면 된다.

<div align="left">
    <img src="./assets/images/LeetHub/LeetHub_04.png" alt="LeetHub_04">
</div>

이제 정상적으로 동작하는지 확인해보자.

문제를 풀고 제출 옆의 `Push` 버튼을 누르면, 방금 만든 Repo에 풀이가 자동으로 커밋되는 것을 볼 수 있다.

<div align="left">
    <img src="./assets/images/LeetHub/LeetHub_05.png" alt="LeetHub_05">
</div><br>

막상 해보니 LeetCode는 생각보다 훨씬 어려웠다.
특히 백준의 Easy와 LeetCode의 Easy는 체감 난이도가 꽤 달랐다.
결국 도구보다 중요한 건 꾸준히 푸는 습관인 것 같다.
