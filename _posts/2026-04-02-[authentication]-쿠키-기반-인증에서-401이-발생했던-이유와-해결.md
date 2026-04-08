---
title: "[Authentication] 쿠키 기반 인증에서 401이 발생했던 이유와 해결"
date: 2026-04-02 10:10:00 +09:00
categories: [Java]
tag: [Project, Authentication, Spring Security, Cookie, Next.js]
---

## 서론

`loslung` 배포 히스토리에서 가장 오래 발목을 잡은 문제 중 하나는 401이었다.  
브라우저에서는 분명 로그인 상태인데, 특정 API 요청은 백엔드에서 인증되지 않은 요청으로 처리되고 있었다.

처음에는 토큰 만료나 인증 로직 자체를 의심하기 쉬웠지만, 실제 원인은 **토큰이 어디에 저장되어 있느냐**보다 **그 요청이 어떤 경로로 백엔드에 도착하느냐**에 더 가까웠다.

이번 글에서는 2026년 4월 2일 [PR #6](https://github.com/Hyunul/loslung/pull/6)과 2026년 4월 6일 [PR #17](https://github.com/Hyunul/loslung/pull/17)을 중심으로, 쿠키 기반 인증 문제가 왜 생겼고 어떻게 해결했는지 정리한다.

## 문제 상황

운영 구조상 일부 요청은 Next.js를 거치지 않고 Apache를 통해 바로 Spring Boot로 들어갔다.  
그런데 백엔드의 `TokenAuthenticationFilter`는 원래 `Authorization` 헤더만 읽고 있었다.

결과는 명확했다.

- 프런트는 `httpOnly` 쿠키에 액세스 토큰을 저장
- 브라우저는 쿠키를 자동으로 전송
- 백엔드는 `Authorization` 헤더가 없다고 판단
- 결국 401

즉, "로그인 여부"보다 "백엔드가 무엇을 인증 수단으로 인식하고 있었는가"가 핵심이었다.

## 실제 수정 코드

문제를 해결한 핵심은 `TokenAuthenticationFilter`에서 토큰을 읽는 방식을 바꾼 것이다.

```java
private static final String ACCESS_TOKEN_COOKIE_NAME = "loslung_access_token";

private String resolveAccessToken(HttpServletRequest request) {
    String authorization = request.getHeader(HttpHeaders.AUTHORIZATION);
    if (authorization != null && authorization.startsWith("Bearer ")) {
        String tokenValue = authorization.substring(7).trim();
        return tokenValue.isEmpty() ? null : tokenValue;
    }

    Cookie[] cookies = request.getCookies();
    if (cookies == null) {
        return null;
    }

    for (Cookie cookie : cookies) {
        if (!ACCESS_TOKEN_COOKIE_NAME.equals(cookie.getName())) {
            continue;
        }

        String tokenValue = cookie.getValue();
        if (tokenValue == null) {
            return null;
        }

        tokenValue = tokenValue.trim();
        return tokenValue.isEmpty() ? null : tokenValue;
    }

    return null;
}
```

이제 백엔드는 다음 순서로 인증 정보를 해석하게 되었다.

1. 먼저 `Authorization` 헤더 확인
2. 없으면 `loslung_access_token` 쿠키 확인

이 변경은 단순하지만 효과가 컸다.  
특히 프록시를 타고 직접 백엔드로 들어오는 요청에서도 인증 상태를 일관되게 해석할 수 있게 되었다.

## 테스트까지 같이 추가한 점이 중요했다

히스토리에서 좋았던 부분은 "코드만 고치고 끝내지 않았다"는 점이다.  
같은 PR에서 쿠키 기반 인증을 검증하는 테스트도 함께 추가되었다.

```java
@Test
void characterLookupAcceptsAccessTokenCookie() throws Exception {
    TestUser user = registerUser("character-cookie-auth");
    updateProfile(user.token(), "loa_dev_key_mock");

    JsonNode lookup = readJson(
        mockMvc.perform(
                get("/api/me/characters/lookup")
                    .cookie(new MockCookie("loslung_access_token", user.token()))
                    .param("characterName", "mock-bard")
            )
            .andExpect(status().isOk())
            .andReturn()
    );

    assertThat(lookup.get("characterName").asText()).isEqualTo("mock-bard");
}
```

이 테스트 덕분에 "헤더 없는 요청도 인증되는가?"를 이후에도 반복 확인할 수 있게 되었다.

## `/auth/*` 예외 처리도 함께 정리해야 했다

이후 2026년 4월 6일 [PR #17](https://github.com/Hyunul/loslung/pull/17)에서는 인증 예외 경로를 다시 손봤다.

기존 로직은 `/auth`만 로그인 페이지로 봤지만, 실제 서비스에는 `/auth/reset-password` 같은 하위 경로가 있었다.

```ts
const isLoginPage = pathname === "/auth";
const isAuthRoute = pathname === "/auth" || pathname.startsWith("/auth/");
const isPublicPage =
  isAuthRoute ||
  pathname === "/" ||
  pathname.startsWith("/calculator") ||
  pathname === "/rewards";
```

이 수정으로 `/auth/*` 전체가 공개 경로로 처리되면서, 비밀번호 재설정 같은 플로우에서도 인증 미들웨어가 과하게 막지 않게 되었다.

## 이번 문제에서 배운 점

이번 401 문제는 토큰 검증 알고리즘이 틀려서 생긴 문제가 아니었다.  
실제로는 다음 두 가지를 놓쳐서 생긴 문제였다.

- 토큰이 헤더가 아니라 쿠키에 들어가는 경우가 있음
- 모든 인증 예외 경로가 `/auth` 하나로 끝나지 않음

즉, 인증은 보안 로직만의 문제가 아니라 **네트워크 경로와 라우팅 규칙의 문제이기도 하다.**

## 정리

`loslung`의 인증 문제를 복기해보면, 핵심은 복잡한 보안 기법이 아니라 "실제 요청 흐름과 인증 수단을 일치시키는 것"이었다.

- 백엔드는 헤더와 쿠키를 모두 읽도록 수정하고
- 테스트로 쿠키 기반 인증을 검증하고
- 프런트 프록시에서는 `/auth/*` 전체를 공개 경로로 정리했다

이 경험 이후로는 인증 문제가 생기면 토큰 값부터 보기보다, 먼저 "이 요청이 어떤 경로로 왔고 백엔드는 무엇을 읽고 있는가"부터 확인하게 되었다.

## Reference

- [PR #6 - fix(auth): support cookie-based auth in TokenAuthenticationFilter](https://github.com/Hyunul/loslung/pull/6)
- [PR #17 - Fix auth subroute proxy handling](https://github.com/Hyunul/loslung/pull/17)
