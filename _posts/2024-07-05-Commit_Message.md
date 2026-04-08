---
title: "[Git] 좋은 커밋 메시지 작성법과 기본 규칙"
date: 2024-07-05 07:27:29 +09:00
categories: [Tip]
tag: [Git, Commit Message, Convention]
---

## 계기

개인 프로젝트에서는 Commit Message를 대충 적고 넘어가는 경우가 많았다.
하지만 협업 환경에 들어가면 훨씬 많은 커밋을 남기게 되고, 기준 없이 작성한 메시지는 나중에 읽기도 어렵다.
그래서 흔히 말하는 "좋은 커밋 메시지"의 기본 원칙을 정리해봤다.

## 구조

Commit Message는 보통 다음 구조로 작성한다.

- `type`: 제목
- `body`: 본문, 생략 가능
- `Resolves`: `#issueNo` 형식의 해결 이슈, 생략 가능
- `See also`: 참고 이슈, 생략 가능

## 기본 규칙

- 제목과 본문은 **빈 줄로 구분**
- 제목은 영문 기준 **50자 이하**
- 제목의 첫 글자는 **대문자**로 작성
- 제목 끝에는 **마침표를 쓰지 않기**
- 제목은 **명령문**으로 작성하고 과거형은 피하기
- 본문은 한 줄에 영문 기준 **72자 이하**
- `어떻게`보다 `무엇`과 `왜`를 담기

## Type

- `feat`: 새로운 기능 추가, 기존 기능의 요구사항 반영
- `fix`: 버그 수정
- `build`: 빌드 관련 수정
- `chore`: 패키지 매니저 설정, 기타 자잘한 수정
- `ci`: CI 설정 수정
- `docs`: 문서나 주석 수정
- `style`: 코드 스타일, 포맷팅 수정
- `refactor`: 기능 변화 없는 코드 리팩터링
- `test`: 테스트 코드 추가 또는 수정
- `release`: 버전 릴리스

## Subject

`type`과 함께 헤더를 구성한다.

ex) `feat: add register API`

## Body

헤더만으로 충분히 설명된다면 생략해도 된다.
추가 설명이 필요하다면 변경 내용과 이유를 본문에 함께 적어준다.

## Footer

어떤 이슈와 관련된 커밋인지 `issue number`를 함께 남긴다.

## References

> [[Git] Commit message 규칙](https://velog.io/@jiheon/Git-Commit-message-%EA%B7%9C%EC%B9%99)
> [[Git] 좋은 커밋 메세지 작성하기위한 규칙들](https://beomseok95.tistory.com/328)
