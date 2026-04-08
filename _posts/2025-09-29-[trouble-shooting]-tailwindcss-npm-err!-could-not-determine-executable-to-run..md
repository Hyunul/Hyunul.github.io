---
title: "[Trouble Shooting] TailwindCSS : npm ERR! could not determine executable to run."
date: 2025-09-29 23:08:22 +09:00
categories: [Error]
tag: [Troubleshooting]
---

### 문제 상황

---

tailwind-css 사용을 위해 아래와 같이 설치 시도.

```
npm install -D tailwindcss postcss autoprefixer < 여기까진 로그에 오류도 발생하지 않고 실행에 문제없음.

npx tailwindcss init -p < 이 명령어 실행 시 다음과 같은 문제 발생.

npm error could not determine executable to run
npm error A complete log of this run can be found...
```

### 해결

---

아래의 Reddit에서 해결 방법을 찾을 수 있었다.

<https://www.reddit.com/r/reactjs/comments/1i8mz7h/facing_issues_in_installing_tailwind_css/?tl=ko>

[Reddit의 reactjs 커뮤니티

reactjs 커뮤니티에서 이 게시물을 비롯한 다양한 콘텐츠를 살펴보세요

www.reddit.com](https://www.reddit.com/r/reactjs/comments/1i8mz7h/facing_issues_in_installing_tailwind_css/?tl=ko)

해결 방법은 다음과 같이 tailwind에 버전을 지정해주면 된다.

```
npm install -D tailwindcss@3.4.17 postcss autoprefixer
```
