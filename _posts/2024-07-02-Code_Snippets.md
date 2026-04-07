---
title: "[Blog] VS Code Code Snippets로 Jekyll 글 템플릿 만들기"
date: 2024-07-02 10:20:57 +09:00
categories: [Tip]
tag: [Blog, Jekyll, VS Code]
---

> 이 글을 읽고 나면 Jekyll 기반 블로그 포스팅에서 반복 입력하던 작업을 훨씬 빠르게 줄일 수 있다.

## 계기

Jekyll 기반 블로그 포스팅을 작성할 때마다 `title`, `date`, `categories`, `tag` 같은 항목을 반복해서 입력해야 한다.
이 과정을 템플릿으로 만들어두면 글을 쓰기 전에 소모되는 시간을 크게 줄일 수 있다.

이번 글에서는 VS Code의 `Code Snippets` 기능으로 포스트 기본 템플릿을 만드는 방법을 정리해본다.

## 설정 방법

> 여러 환경에서 Github 기반 블로그를 관리하고 있어서, 나는 VS Code 전역 설정 대신 프로젝트 단위 설정을 선호한다.
> 그래서 설정 파일도 저장소에 함께 포함하는 방식으로 진행했다.

### 1. `.vscode` 폴더 생성

프로젝트 최상위 디렉터리에 `.vscode` 폴더를 만든다.

### 2. Snippets 파일 생성

원하는 이름의 파일을 만든 뒤 확장자를 `.code-snippets`로 지정한다.

ex) `load_template.code-snippets`

### 3. 템플릿 코드 작성

예시로 내가 사용한 템플릿 코드는 아래와 같다.

<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_01.png" alt="Code_Snippets_01">
</div>

특히 `date` 값은 스니펫을 실행한 시점의 시간을 `YYYY-MM-DD HH:MM:SS +09:00` 형식으로 자동 입력해줘서 꽤 유용했다.

### 4. 사용 방법

내 VS Code 환경에서는 첫 글자만 입력했을 때 자동 완성 목록이 바로 뜨지 않았다.
그래서 단축키로 스니펫을 호출하는 방식을 사용했다.

`Ctrl + Space`를 누르면 생성해둔 스니펫 후보가 나타난다.

<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_02.png" alt="Code_Snippets_02">
</div>

여기서 엔터를 누르면

<div align="left">
    <img src="./assets/images/Code_Snippets/Code_Snippets_03.png" alt="Code_Snippets_03">
</div>

이처럼 템플릿이 정상적으로 삽입되는 것을 확인할 수 있다.

이제 포스트를 새로 만들 때마다 같은 내용을 반복해서 입력할 필요가 없어졌다.
귀찮음을 줄였으니, 남은 건 꾸준히 글을 쓰는 일뿐이다.
