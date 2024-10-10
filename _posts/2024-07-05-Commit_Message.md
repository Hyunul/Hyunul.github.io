---
title: "[Git] 좋은 Commit message 작성법"
date: 2024-07-05 07:27:29 +09:00
categories: [Tech, Git]
tag: [Git]
---

# **찾게 된 계기**

나는 항상 개인 프로젝트의 Commit Message를 대충 지어오곤 했다. 그러던 중 "나중에 회사에 들어가게 되면 많은 양의 Commit Message를 남기게 될텐데.. 처음부터 정리가 안된다면 나중에 감당이 가능할까?"라는 마음에서 찾아보기 시작했다.  
이제 흔히 말하는 "좋은 커밋 메세지"를 작성하는 방법을 알아보자.

# **사용 목적**

# **구조**

Commit Message는 다음과 같은 구조로 이루어져 있다.

> - type(제목): title(제목)
> - body: (본문, 생략가능)
> - Resolves: #issueNo, ...(해결한 이슈, 생략 가능)
> - See also: #issueNo, ...(참고 이슈, 생략 가능)

# **기본 규칙**

- 제목과 본문을 **빈 행으로 구분**
- 제목은 영문 기준 **50글자 이하**
- 첫 글자는 **대문자**로 작성
- 제목 끝에 **마침표 X**
- 제목은 **명령문**으로 사용, 과거형 X
- 본문의 각 행은 영문 기준 **72글자 이하**
- 어떻게보다는 **무엇과 왜**

# **Type**

> - feat: 새로운 기능 추가, 기존의 기능을 요구 사항에 맞추어 수정
> - fix: 기능에 대한 버그수정
> - build: 빌드 관련 수정
> - chore: 패키지 매니저 수정, 그 외 기타 수정
> - ci: CI 관련 설정 수정
> - docs: 문서(주석) 수정
> - style: 코드 스타일, 포맷팅에 대한 수정
> - refactor: 기능의 변화가 아닌 코드 리팩터링 ex) 변수 이름 변경
> - test: 테스트 코드 추가/수정
> - release: 버전 릴리즈

# **Subject**

Type과 함께 헤더를 구성.  
ex) feat: Add_register_api

# **Body**

헤더로 표현이 가능하다면 생략 가능.  
아닌 경우에는 자세한 내용을 함께 적어 본문 구성.

# **Footer**

어떠한 이슈에 대한 commit인지 issue number를 포함.

# **References**

> [[Git] Commit message 규칙](https://velog.io/@jiheon/Git-Commit-message-%EA%B7%9C%EC%B9%99)  
> [[Git] 좋은 커밋 메세지 작성하기위한 규칙들](https://beomseok95.tistory.com/328)
