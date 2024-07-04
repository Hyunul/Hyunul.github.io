---
title: (VSC) Code Snippets를 사용하여 default 템플릿을 만들어보자.
date: 2024-07-02 10:20:57 +09:00
categories: [Tech, VSC]
tag: [VSC]
---

> 우리는 이 글을 읽음으로써 더 이상 Jekyll 기반의 블로그 포스팅을 할 때 시간을 낭비하지 않을 수 있게 될 것이다.

# __찾게 된 계기__

Jekyll 기반의 블로그 포스팅을 할 때 반드시 적어주어야 하는 사항들이 있다.. (title, date, categories, tag 등등)
그런데 이를 템플릿화시킨다면? 포스팅 시간이 획기적으로 줄어들 것이다.

시작해보자.

# __🛠 설정 방법 🛠__
> 먼저 나는 여러 장소에서 Github 기반의 블로그를 운영하기에 하나의 VSC에 전역 설정을 하지 않는다.
> 따라서 Github에 설정 파일을 함께 올릴 생각으로 처음부터 프로젝트 단위로 설정을 시작하였다.

## __1. .vscode 폴더 생성__
프로젝트 최상위 디렉토리에 .vscode 폴더를 생성하자.

## __2. Snippets 파일 생성__
파일명을 임의로 정하고, 확장자를 .code-snippets으로 바꿔준다.

ex) load_template.code-snippets

## __3. 사용할 템플릿 코드 작성__
예시로 나의 템플릿 코드를 보여주겠다.

<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_01.png" alt="Code_Snippets_01">  
</div>

이건 진짜 꿀팁인데 `date`에 해당되는 코드는 템플릿 코드를 실행한 시점의 시간을 `YYYY-MM-DD HH:MM:SS +09:00` 포맷으로 바꿔서 작성해준다... 안쓸 수가 없겠지?

## __4. 사용 방법__
내 VSC에 문제가 있는 것인지는 모르겠지만... 가장 첫 문자를 쓰면 보통 단축어가 나오는데 현재 내가 작성한 시점에서는 나오지 않아 다른 방법으로 대체했다.

`ctrl + 스페이스 바` 를 누르면 내가 생성한 단축어가 나오게 된다.
<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_02.png" alt="Code_Snippets_02">  
</div>

그리고 엔터를 누르면?  
<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_03.png" alt="Code_Snippets_03">  
</div>
성공적으로 실행되는 것을 확인할 수 있었다.

앞으로 귀찮다고 핑계댈 일이 사라져버렸다..
열심히 써야겠지...? 😓