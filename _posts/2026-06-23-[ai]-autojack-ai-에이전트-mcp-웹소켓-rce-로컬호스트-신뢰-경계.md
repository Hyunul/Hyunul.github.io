---
title: "[AI] AutoJack — AI 브라우징 에이전트가 RCE 공격 경로가 된 이유"
date: 2026-06-23 08:30:00 +09:00
categories: [AI]
tag: [AI-agent, MCP, RCE, AutoGen, security, localhost]
---

## 서론

AI 에이전트가 일상 업무에 깊숙이 들어오면서, "에이전트가 악성 웹페이지를 열면 어떻게 되는가"라는 질문이 더 이상 학문적 사고 실험이 아니게 됐다. 2026년 6월 18일, 마이크로소프트 Defender 보안 연구팀이 이 질문에 대한 구체적이고 재현 가능한 답을 내놨다. 그 이름은 **AutoJack**이다.

AutoJack은 AutoGen Studio의 MCP(Model Context Protocol) WebSocket에서 발견된 취약점 체인이다. 이론이 아니라 실제 작동하는 공격으로, 단 하나의 악성 웹페이지만으로 AI 에이전트가 실행 중인 호스트 머신에서 임의 코드를 실행할 수 있다. 브라우저를 사용하는 에이전트는 호스트의 로컬호스트와 동일한 신뢰 수준을 가지는데, 이 전제가 얼마나 위험한 가정인지를 AutoJack이 정확히 증명했다.

AutoGen Studio는 마이크로소프트가 만든 오픈소스 AI 에이전트 프로토타이핑 UI다. 개발자들이 멀티에이전트 워크플로우를 실험하고 테스트하는 데 널리 쓰인다. 이번 연구는 AutoGen Studio 특정 버전에 국한된 이야기지만, 그 시사점은 MCP 생태계와 AI 에이전트 개발 도구 전반으로 확장된다. AI 에이전트에게 어떤 권한을 어떻게 부여할 것인지, 그리고 에이전트가 신뢰할 수 없는 콘텐츠를 처리할 때 어떤 격리를 적용해야 하는지에 대한 근본적인 질문이다.

## 본론

### MCP와 AutoGen Studio의 구조

이번 취약점을 이해하려면 먼저 AutoGen Studio가 어떻게 동작하는지 알아야 한다.

AutoGen Studio는 MCP 서버를 로컬호스트에서 실행하고, WebSocket 엔드포인트(`ws://localhost:8081/api/mcp/ws/`)를 통해 에이전트 명령을 처리한다. 에이전트가 외부 도구를 호출할 때, 브라우저 UI가 이 WebSocket으로 명령을 보내고 결과를 받아온다.

"로컬호스트에서만 실행 중이니 외부에서 접근할 수 없다"는 전제는 일반적인 사용 환경에서는 어느 정도 유효하다. 일반 브라우저가 외부 사이트를 방문할 때, CORS 정책과 출처(origin) 검사가 외부 사이트에서 로컬호스트 WebSocket으로의 연결을 차단할 수 있다.

그런데 **AI 브라우징 에이전트**가 개입하면 이 가정이 무너진다.

```
[일반 사용자]        [AI 브라우징 에이전트]
      |                       |
      | 외부 사이트 방문       | 악성 웹페이지 방문
      v                       v
  [브라우저]           [에이전트 브라우저]
      |                       |
      | ws://localhost:8081   | ws://localhost:8081
      | CORS 차단 → 실패      | 로컬호스트 = 에이전트 자신
      |                       | 출처 검사 통과 → 성공
      v                       v
 [접근 불가]          [WebSocket 연결 확립]
```

에이전트는 개발자와 같은 머신의 로컬호스트에서 실행된다. 에이전트가 악성 웹페이지를 방문했을 때, 그 페이지의 JavaScript가 `ws://localhost:8081`로 WebSocket 연결을 시도하면, 에이전트 컨텍스트에서는 "로컬호스트에서의 연결"로 인식된다. 출처 검사를 우회하게 된다.

### 취약점 체인: 세 가지 결함의 결합

마이크로소프트 연구팀은 AutoJack을 가능하게 한 세 가지 개별 취약점을 식별했다.

#### 1. 출처 허용 목록 우회 (CWE-1385)

AutoGen Studio의 MCP WebSocket은 `http://127.0.0.1` 또는 `http://localhost`에서의 연결만 신뢰하도록 설계됐다. 그러나 개발자와 동일한 머신에서 실행되는 AI 브라우징 에이전트(headless browser)는 그 자체가 `localhost`다. 에이전트가 방문한 악성 페이지에서 WebSocket 연결을 시도하면, 이 연결은 `localhost` 출처로 인식된다. 허용 목록 우회가 성립한다.

#### 2. 인증 미들웨어 누락 (CWE-306)

WebSocket 서버에는 GitHub, MSAL, Firebase 등을 지원하는 인증 미들웨어가 존재했다. 그러나 이 미들웨어는 `/api/mcp/*` 경로에 대해 "핸들러가 자체적으로 토큰을 검증할 것"이라는 가정 하에 인증 검사를 건너뛰었다. 실제로는 MCP 핸들러에도 검증 로직이 없었다.

```python
# 문제가 있는 미들웨어 구조 (의사 코드)
@middleware
async def auth_middleware(request, call_next):
    if request.path.startswith("/api/mcp/"):
        # "MCP 핸들러가 처리할 것"이라는 잘못된 가정
        return await call_next(request)
    # 다른 경로는 토큰 검증 수행
    token = request.headers.get("Authorization")
    if not verify(token):
        return 401
    return await call_next(request)
```

모든 인증 모드(github, msal, firebase)가 설정된 경우에도 MCP 경로로의 WebSocket 연결은 인증 없이 수락됐다.

#### 3. 안전하지 않은 명령 실행 (CWE-78)

WebSocket 엔드포인트는 `server_params` 쿼리 파라미터로 Base64 인코딩된 JSON을 받아, 이를 그대로 시스템 명령으로 실행했다. 실행 허용 파일에 대한 화이트리스트도, 입력 검증도 없었다.

```
ws://localhost:8081/api/mcp/ws/?server_params=<base64_encoded_payload>
```

```text
# base64 디코딩 후 내용 예시
{
  "command": "powershell.exe",
  "args": ["-enc", "<base64_encoded_ps_script>"]
}
```

`calc.exe`, `powershell.exe -enc ...`, `bash -c '...'` 등 어떤 실행 파일이든 `server_params`로 전달하면 그대로 실행됐다.

### 전체 공격 흐름

세 가지 취약점이 결합하면 다음과 같은 공격 흐름이 만들어진다.

```
1. 개발자가 AutoGen Studio 실행 (localhost:8081)
          |
2. 에이전트가 자동으로 또는 과제 수행 중 악성 웹페이지 방문
          |
3. 악성 페이지의 JavaScript:
   ws://localhost:8081/api/mcp/ws/?server_params=<공격 페이로드>
   → WebSocket 연결 시도
          |
4. 출처 검사 통과 (에이전트 = localhost)
   인증 검사 없음 (MCP 경로 미들웨어 스킵)
          |
5. server_params의 명령이 개발자 권한으로 실행
          |
6. 개발자 머신에서 임의 코드 실행 (RCE)
```

단 하나의 웹페이지를 에이전트가 방문하는 것만으로, 에이전트가 실행 중인 개발자 머신에서 임의 코드가 실행될 수 있는 구조다.

### 실제 위험 범위와 제한 요소

연구팀은 몇 가지 중요한 제한 사항도 함께 공개했다.

**PyPI 배포에는 해당 없음**: 문제의 MCP WebSocket 서피스는 PyPI(Python Package Index) 정식 배포 버전에 포함되지 않았다. `pip install autogen-studio`로 설치한 사용자들은 영향을 받지 않는다. 현재 PyPI에 있는 최신 버전(0.4.2.2)은 취약한 코드를 포함하지 않는다.

**연구 수준, 야생 악용 없음**: 마이크로소프트는 이 취약점이 능동적으로 악용되는 사례를 발견하지 못했다고 밝혔다. 이번은 연구팀이 발견하여 수정 전 공개한 사례다.

**소스 빌드 사용자 위험**: GitHub 메인 브랜치에서 직접 빌드하거나 개발 환경에서 실행하는 사용자는 영향을 받을 수 있었다.

마이크로소프트는 해당 내용을 MSRC(Microsoft Security Response Center)에 보고했으며, AutoGen 유지보수팀은 **커밋 b047730**에서 다음 수정 사항을 메인 브랜치에 병합했다:

- URL 기반 파라미터 바인딩 제거 → 서버사이드 파라미터 바인딩으로 교체
- MCP 경로를 인증 스킵 목록에서 제외
- MCP 경로에 표준 인증 플로우 적용

### AI 에이전트 시대의 새로운 공격 표면

AutoJack이 시사하는 더 큰 그림이 있다. AI 에이전트가 웹 브라우징, 파일 시스템 접근, 코드 실행, 외부 서비스 호출 등 강력한 권한을 가지게 되면서, 에이전트 자체가 새로운 공격 표면이 된다.

기존 보안 모델에서 "로컬호스트 = 안전"이라는 가정은 사람이 직접 브라우저를 조작하는 세계에서는 상당히 유효했다. 일반 브라우저는 CORS 정책과 출처 검사 등의 보안 메커니즘이 잘 작동한다. 그러나 AI 에이전트가 자동으로 웹을 탐색하고 도구를 호출하는 환경에서는, 로컬호스트와 에이전트 브라우저 사이의 신뢰 경계가 근본적으로 다르다.

MCP 생태계는 2025년 이후 폭발적으로 성장하고 있다. 수많은 MCP 서버가 로컬호스트 WebSocket을 통해 AI 에이전트와 통신한다. 이 중 얼마나 많은 구현체가 AutoJack과 동일한 가정, 즉 "로컬호스트 = 신뢰"라는 전제 하에 만들어졌는지 알 수 없다.

MCP 서버를 만드는 개발자들이 주목해야 할 방어 원칙:

```text
1. 명시적 인증 (Explicit Authentication)
   - 로컬호스트 연결이라도 토큰 기반 인증 구현
   - 인증 미들웨어가 모든 경로를 커버하는지 확인

2. 입력 검증 및 화이트리스트 (Input Validation)
   - 실행 허용 명령어 화이트리스트 적용
   - 파라미터를 URL에서 직접 받지 말고 서버사이드 바인딩 사용

3. 최소 권한 원칙 (Least Privilege)
   - 에이전트 브라우징 컨텍스트를 개발자 계정에서 격리
   - 샌드박스 프로파일에서 에이전트 실행

4. 에이전트 브라우징 격리
   - 에이전트 browsing identity를 개발자 identity와 분리
   - 에이전트에서 로컬 서비스 접근 허용 여부 명시적으로 제어
```

## 정리

- AutoJack: AutoGen Studio MCP WebSocket의 세 가지 취약점 체인 (출처 허용 목록 우회 CWE-1385 + 인증 미들웨어 누락 CWE-306 + 안전하지 않은 명령 실행 CWE-78)
- 단 하나의 악성 웹페이지로 AI 브라우징 에이전트를 통해 개발자 호스트에서 RCE 가능
- PyPI 배포 버전(0.4.2.2)에는 해당 없으며, 현재까지 실제 야생 악용 보고 없음
- 커밋 b047730에서 패치 완료
- 핵심 교훈:
  - 로컬호스트 WebSocket이라도 명시적 인증 레이어 필수
  - 명령 실행 엔드포인트는 화이트리스트 기반으로 제한
  - AI 에이전트 브라우저 컨텍스트를 개발자 권한과 격리
  - MCP 서버 구현 시 인증과 입력 검증을 설계 단계부터 포함
  - `localhost = 신뢰`라는 전제를 AI 에이전트 환경에서는 더 이상 유효하지 않은 것으로 간주
- 업계 반응: TechRadar는 "AI 에이전트가 왜 위험할 수 있는지를 가장 구체적으로 보여준 연구 사례"라고 평가했다. 보안 연구 커뮤니티에서는 이번 사례를 계기로 MCP 생태계 전반에 대한 보안 감사의 필요성이 제기되고 있으며, The Hacker News는 유사한 패턴의 취약점이 다른 MCP 구현체에도 잠재할 수 있다는 우려를 전했다.

## Reference

- [AutoJack: How a single page can RCE the host running your AI agent | Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/06/18/autojack-single-page-rce-host-running-ai-agent/)
- [AutoJack Attack Lets One Web Page Hijack AI Agent for Host Code Execution | The Hacker News](https://thehackernews.com/2026/06/autojack-attack-lets-one-web-page.html)
- [Microsoft warns AI agents are being 'AutoJack'-ed to deliver RCE payloads by browsing untrusted websites | TechRadar](https://www.techradar.com/pro/security/microsoft-warns-ai-agents-are-being-autojack-ed-to-deliver-rce-payloads-by-browsing-untrusted-websites)
- [AutoJack Exploit Chain Hits Microsoft AutoGen Studio With Zero-Click RCE Attack | GB Hackers](https://gbhackers.com/autojack-exploit-chain-hits-microsoft-autogen/)
- [AutoJack Exploit Enables AI Agent Hijacking Through a Single Web Page | CyberPress](https://cyberpress.org/autojack-exploit-enables-ai-agent-hijacking/)
