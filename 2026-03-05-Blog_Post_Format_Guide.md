---
title: "[Blog] 이 프로젝트의 포스트 작성 포맷 정리"
date: 2026-03-05 10:00:00 +09:00
categories: [Tip]
tag: [Blog, Guide]
---

기존 `_posts`의 전체 글을 기준으로, 현재 블로그에서 사용하는 작성 포맷을 정리했다.

## 파일명 규칙

포스트 파일명은 아래 패턴을 따른다.

```text
_posts/YYYY-MM-DD-제목.md
```

예시

```text
_posts/2024-10-16-Group_By.md
_posts/2025-01-23-폴링과 이벤트.md
```

## Front Matter 규칙

모든 포스트는 문서 상단에 YAML Front Matter를 둔다.

```yaml
---
title: "[카테고리] 글 제목"
date: YYYY-MM-DD HH:MM:SS +09:00
categories: [상위분류]
tag: [태그1, 태그2]
---
```

실제 프로젝트에서 확인한 공통점

- `title`은 대괄호 접두어(`[Spring]`, `[Error]`, `[Blog]`)를 자주 사용한다.
- `date`는 `+09:00` 타임존 오프셋을 포함한다.
- `categories`는 보통 1개(`Tip`, `Error`, `BE`, `CS` 등)로 작성한다.
- 태그 키는 `tags`가 아니라 `tag`를 사용 중이다.

## 본문 작성 스타일

본문은 Markdown 기반으로 다음 패턴이 많이 보인다.

- `##`, `###` 헤더로 섹션 분리
- 핵심 키워드는 백틱(``` ` ```)으로 강조
- 필요한 경우 인용문(`>`)으로 요약/주의사항 정리
- 코드 블록은 언어 지정(`java`, `sql`, `properties`, `gradle`) 사용

예시

```java
@Entity
public class User {
    @Column(name = "userId")
    private String userId;
}
```

## 이미지 삽입 스타일

이미지는 `assets/images` 하위에 보관하고 HTML `<img>` 태그를 자주 사용한다.

```html
<div align="left">
    <img src="./assets/images/폴더명/이미지.png" alt="설명">  
</div>
```

## 바로 복붙 가능한 포스트 템플릿

```markdown
---
title: "[주제] 제목"
date: 2026-03-05 10:00:00 +09:00
categories: [Tip]
tag: [Blog]
---

## 서론

글을 쓰게 된 배경과 문제 상황

## 본론

핵심 개념/설정/코드/예시

## 정리

요약과 적용 포인트

## Reference

- [참고 링크 제목](https://example.com)
```

## 체크리스트

- 파일명 날짜와 `date` 값이 일치하는가?
- `categories`와 `tag`가 누락되지 않았는가?
- 코드 블록 언어가 지정되어 있는가?
- 이미지 경로가 `./assets/images/...`로 맞는가?
