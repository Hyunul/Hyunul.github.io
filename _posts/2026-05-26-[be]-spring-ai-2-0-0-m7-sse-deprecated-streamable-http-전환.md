---
title: "[BE] Spring AI 2.0.0-M7 릴리스: SSE Deprecated, Streamable HTTP 전환 및 CVE-2026-41863 패치"
date: 2026-05-26 07:20:00 +09:00
categories: [BE]
tag: [SpringAI, MCP, LLM, CVE, SpringBoot]
---

## 서론

2026년 5월 23일, Spring 팀이 Spring AI의 세 버전을 동시에 공개했다. 유지보수 릴리스인 **1.0.8**과 **1.1.7**, 그리고 다음 메이저 버전의 일곱 번째 마일스톤인 **2.0.0-M7**이다.

이번 릴리스에서 가장 주목할 변경점은 두 가지다.

첫째, 2.0.0-M7에서 **SSE(Server-Sent Events) 트랜스포트가 공식 deprecated** 됐다. MCP(Model Context Protocol) 서버를 운영하고 있거나 준비 중인 팀이라면 반드시 확인해야 하는 브레이킹 체인지다. **Streamable HTTP**가 새 기본값으로 자리를 잡았고, 이 결정은 표준 리버스 프록시·로드밸런서 환경과의 호환성을 크게 개선한다.

둘째, **CVE-2026-41863**이 함께 공개되고 패치됐다. Spring AI가 Anthropic Skills API를 통해 LLM이 반환한 파일명을 `Path.resolve()` 전에 검증하지 않아 경로 이탈(Path Traversal)이 가능한 취약점이다. CVSS 7.1 Medium 수준이지만, LLM이 외부 인풋을 파일시스템 경로로 변환할 때 발생하는 보안 리스크를 공식 CVE로 다룬 첫 번째 사례라는 점에서 의미가 크다.

Spring AI 2.0.0이 어떤 방향으로 진화하고 있는지, 그리고 지금 당장 어떤 버전에서 무엇을 업그레이드해야 하는지를 정리한다.

## 본론

### 버전별 변경 사항 요약

세 버전의 대상 사용자와 핵심 변경점을 먼저 정리하면 다음과 같다.

| 버전 | 대상 | 핵심 변경 |
|---|---|---|
| 1.0.8 | 1.0.x 사용자 | Redis VectorStore 자동 삭제 버그 수정 |
| 1.1.7 | 1.1.x 사용자 | Ollama+GraalVM 수정, OpenAI 스트리밍 수정, **CVE-2026-41863 패치** |
| 2.0.0-M7 | 2.0 마이그레이션 준비 중 | **SSE deprecated → Streamable HTTP**, ToolCallAdvisor, ToolSpec API |

### Spring AI 1.0.8: Redis VectorStore 자동 삭제 10개 제한 버그

1.0.8에서 수정된 핵심 버그는 `RedisVectorStore#doDelete`가 삭제 요청을 **처음 10개 항목만 처리**하고 나머지를 조용히 무시하던 문제다.

```java
// 버그가 있던 동작 (개념적 설명)
vectorStore.delete(List.of(id1, id2, ..., id15));
// 실제로는 id1 ~ id10만 삭제되고 id11 ~ id15는 무시됨
// 에러 없음, 로그 없음 → 탐지 불가
```

RAG 파이프라인에서 오래된 임베딩을 주기적으로 정리하는 배치 작업이 있다면, 1.0.8 이전 버전에서 이 작업이 제대로 완료되지 않았을 수 있다. 특히 10개 단위로 배치를 나누는 코드가 없었다면 데이터가 누적됐을 가능성이 있다. 업그레이드 후에는 스토어의 실제 항목 수를 한 번 확인해보는 것이 좋다.

### Spring AI 1.1.7: 두 가지 버그 수정과 CVE 패치

#### Ollama + GraalVM 네이티브 이미지 호환성

GraalVM `native-image`로 빌드한 Spring AI 앱에서 Ollama 클라이언트를 사용하면 런타임 초기화 오류가 발생하던 문제가 수정됐다. Reflection 설정 누락이 원인이었으며, `NativeConfiguration` 클래스에 Ollama 관련 타입이 추가됐다.

GraalVM 네이티브 이미지는 빌드 시점에 reflection 접근이 필요한 클래스를 미리 등록해야 하는데, Spring AI 초기 구현에서 Ollama 관련 타입이 빠져 있었다. 프로덕션 환경에서 네이티브 빌드를 활용하는 경우 반드시 확인해야 하는 수정이다.

#### OpenAI 스트리밍 청크 누락 (switchMap 버그)

`OpenAiChatModel`이 스트리밍 응답을 처리할 때, 내부 `switchMap` 연산자가 빠르게 연속된 청크 중 일부를 누락시키던 문제다.

```java
// 문제가 있던 패턴 (개념적 설명)
// switchMap은 이전 구독을 취소하고 새 구독을 시작하는 특성이 있어
// 빠른 스트리밍에서 일부 청크가 취소될 수 있었음

// 수정 후: flatMap으로 대체 → 모든 청크가 순서대로 처리됨
```

스트리밍 UI를 구현할 때 텍스트가 불규칙하게 끊기거나 특정 구간이 아예 누락되는 현상을 경험했다면 이 버그의 영향을 받은 것일 수 있다. 1.1.7로 업그레이드하면 개선된다.

#### CVE-2026-41863: LLM 출력 기반 경로 이탈 취약점

이번 릴리스에서 가장 중요한 보안 수정이다. Spring AI가 Anthropic Skills API를 통해 LLM이 반환한 파일명을 그대로 `Path.resolve()`에 전달해 파일을 쓰던 코드에서 경로 이탈(Path Traversal)이 가능했다.

```java
// 취약한 패턴 (수정 전)
String filename = toolCallResult.getFilename(); // LLM이 반환한 값
Path targetFile = basePath.resolve(filename);   // "../../../etc/cron.d/malicious"도 허용됨
Files.write(targetFile, content);

// 안전한 패턴 (수정 후: Spring AI 1.1.7)
String filename = toolCallResult.getFilename();
Path targetFile = basePath.resolve(filename).normalize();
if (!targetFile.startsWith(basePath.normalize())) {
    throw new SecurityException("Path traversal detected in LLM-provided filename");
}
Files.write(targetFile, content);
```

LLM이 `../../../etc/passwd`, `../../../home/user/.ssh/authorized_keys`와 같은 경로 이탈 문자열을 반환하면, 의도한 출력 디렉터리 밖의 파일을 덮어쓸 수 있었다. 실제 공격이 보고된 건 아니지만, LLM 출력을 신뢰하고 파일시스템 작업에 그대로 사용하는 패턴의 위험성을 공식 CVE로 인정했다는 점이 중요하다.

```yaml
CVE: CVE-2026-41863
CVSS: 7.1 (Medium)
공격 벡터: 네트워크, 낮은 권한 필요, 사용자 상호작용 불필요
영향 버전: Spring AI 1.1.0 ~ 1.1.x
수정 버전: Spring AI 1.1.7
공개일: 2026-05-23
```

Spring AI 1.1.x를 사용 중이라면 **즉시 1.1.7로 업그레이드**가 필요하다.

### Spring AI 2.0.0-M7: 가장 큰 브레이킹 체인지

#### SSE Deprecated → Streamable HTTP로 전환

MCP 1.0 스펙 초기에 SSE가 채택됐던 이유는 브라우저·HTTP/1.1 환경에서 서버→클라이언트 스트리밍을 구현하기 쉬웠기 때문이다. 하지만 실제 운영에서 여러 문제가 드러났다.

**SSE의 한계:**
- 단방향 통신만 가능 (서버→클라이언트)
- 대부분의 로드밸런서가 SSE 연결을 타임아웃으로 끊거나 버퍼링함
- nginx, HAProxy 등 표준 리버스 프록시 설정에 별도 조정 필요
- 클라이언트→서버 메시지는 별도 HTTP POST로 처리해야 해 구현이 복잡

**Streamable HTTP의 장점:**
- HTTP/1.1과 HTTP/2 모두에서 동일하게 동작
- 표준 로드밸런서·리버스 프록시와 즉시 호환
- 양방향 스트리밍 지원
- 기존 HTTP 인프라를 그대로 재사용 가능

2.0.0-M7부터 SSE 트랜스포트는 deprecated로 마킹됐으며, Streamable HTTP가 기본값이다. 기존 SSE 기반 MCP 클라이언트와의 하위 호환성은 일정 기간 유지되지만, 새로운 구현에서는 Streamable HTTP를 사용하도록 권고된다.

Spring 팀이 공개한 마이그레이션 방향은 다음과 같다.

```yaml
# application.yml - 2.0.0-M7 이후 MCP 설정 예시
spring:
  ai:
    mcp:
      client:
        transport: streamable-http  # 새 기본값 (SSE는 deprecated)
      server:
        transport: streamable-http
```

#### ToolCallAdvisor: 도구 호출 표준화

기존에는 도구 호출 처리가 각 모델 구현체에 분산돼 있었다. 2.0.0-M7부터 `ToolCallAdvisor`라는 공식 어드바이저로 표준화됐다.

```java
// 2.0.0-M7 권장 패턴
@Bean
ChatClient chatClient(ChatModel chatModel) {
    return ChatClient.builder(chatModel)
        .defaultAdvisors(new ToolCallAdvisor())
        .build();
}
```

어드바이저 체인 내에서 도구 호출을 처리하게 됨으로써, 로깅·재시도·검증 등의 크로스커팅 관심사를 도구 호출 단계에서도 일관되게 적용할 수 있게 됐다.

#### ToolSpec 플루언트 API

어노테이션 기반(`@Tool`) 방식의 대안으로, 런타임에 동적으로 도구를 정의할 수 있는 `ToolSpec` 인터페이스가 추가됐다.

```java
// 어노테이션 방식: 컴파일 타임 정의
@Tool(description = "사용자 데이터베이스 검색")
public String searchDatabase(String query) { ... }

// ToolSpec 방식: 런타임 동적 정의
ToolSpec spec = ToolSpec.builder()
    .name("search_database")
    .description("사용자 데이터베이스 검색")
    .inputSchema(JsonSchema.of(SearchInput.class))
    .handler((input) -> handleSearch(input))
    .build();

chatClient.prompt()
    .user("최근 주문 목록 조회해줘")
    .tools(spec)
    .call();
```

멀티테넌트 환경에서 테넌트별로 다른 도구 세트를 제공하거나, 사용자 권한에 따라 사용 가능한 도구를 동적으로 구성해야 하는 시나리오에서 특히 유용하다.

#### Gemini 2.5 Flash 통합 업데이트

Gemini API 클라이언트가 최신 Gemini 2.5 Flash 모델을 지원하도록 업데이트됐다. Google I/O 2026에서 발표된 Gemini 3.5 Flash와는 별개로, 2.5 Flash 계열의 안정화된 통합을 지원한다.

### Spring AI 2.0.0의 방향성과 5월 릴리스 트레인 변경

한편, Spring 팀은 5월 11일 **May Release Train 일정 변경**을 공지했다. 원래 5월 11~22일로 예정됐던 릴리스 트레인이 **6월 1~5일**로 연기됐다. Spring Boot 4.1.0 GA 릴리스도 이 일정에 포함되어 있어, 6월 초에 함께 공개될 예정이다.

지금까지의 마일스톤들을 종합하면, Spring AI 2.0.0은 세 가지 방향으로 수렴하고 있다.

1. **MCP 인프라 표준화**: SSE → Streamable HTTP, ToolCallAdvisor 등으로 MCP 생태계와의 정합성 강화
2. **에이전트 워크플로 지원**: 동적 도구 구성(ToolSpec), Plan-and-execute 패턴을 위한 기반 API 정비
3. **LLM 보안 패턴 내재화**: LLM 출력을 신뢰하지 않는 방어적 프로그래밍 패턴 확립 (CVE-2026-41863이 첫 번째 공식 사례)

세 번째 방향이 특히 주목할 만하다. LLM이 파일명·경로·명령 등을 생성할 때 발생하는 보안 리스크는 아직 업계 전반에서 체계적으로 다루지 않은 영역이다. Spring AI 팀이 CVE를 통해 이 문제를 공식화했다는 건, 앞으로 LLM 기반 애플리케이션의 보안 설계 기준이 더 명확해질 것임을 시사한다.

## 정리

- **즉시 조치 필요**: Spring AI 1.1.0~1.1.x 사용자는 CVE-2026-41863(경로 이탈) 패치를 위해 **1.1.7로 업그레이드**해야 한다.
- Spring AI 1.0.x를 Redis VectorStore와 함께 사용 중이라면 1.0.8의 자동 삭제 10개 제한 버그 영향을 확인해야 한다.
- 2.0.0-M7에서 SSE 트랜스포트가 deprecated됐고 Streamable HTTP가 기본값이 됐다. MCP 통합 코드를 미리 검토해야 한다.
- LLM이 제안하는 파일명·경로는 신뢰하지 말 것. `Path.resolve(filename).normalize()`로 정규화한 뒤, 의도한 기본 디렉터리 내에 위치하는지 반드시 검증해야 한다.
- Spring AI 2.0.0 GA는 Spring Boot 4.1.0과 함께 2026년 6월 첫째 주에 릴리스될 예정이다.

## Reference

- [Spring AI 1.0.8, 1.1.7, 2.0.0-M7 Available Now | spring.io 공식 블로그](https://spring.io/blog/2026/05/23/spring-ai-1-0-8-1-1-7-2-0-0-M7-available-now/)
- [CVE-2026-41863 Security Advisory | spring.io](https://spring.io/security/cve-2026-41863/)
- [May Release Train Date Changes | spring.io](https://spring.io/blog/2026/05/11/may-train-shift/)
- [Spring AI GitHub Releases](https://github.com/spring-projects/spring-ai/releases)
- [Spring Boot 4.1.0-RC1 Available Now | spring.io](https://spring.io/blog/2026/04/23/spring-boot-4-1-0-RC1-available-now/)
