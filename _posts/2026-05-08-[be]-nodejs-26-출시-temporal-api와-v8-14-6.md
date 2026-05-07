---
title: "[BE] Node.js 26 출시: Temporal API 정식 활성화와 V8 14.6이 가져오는 변화"
date: 2026-05-08 08:00:00 +09:00
categories: [BE]
tag: [Nodejs, JavaScript, TemporalAPI, V8, 런타임]
---

## 서론

2026년 5월 5일, Node.js 26.0.0이 공식 출시됐다. 짝수 버전이므로 올해 10월에 LTS(Long-Term Support) 전환이 예정된 버전이다. Node.js는 2년마다 새 LTS를 내놓는데, 26은 그 사이클에서 2026년의 메이저 버전이다.

이번 릴리스에서 가장 주목받는 변화는 **Temporal API의 기본 활성화**다. Temporal은 JavaScript 날짜/시간 처리의 고질적 문제를 해결하기 위해 TC39에서 수년간 설계해 온 새로운 표준 API다. 이전까지는 `--experimental-temporal` 플래그를 직접 붙여야만 사용할 수 있었는데, Node.js 26부터는 플래그 없이 전역에서 바로 사용 가능해졌다.

백엔드 개발자 입장에서 이게 왜 중요한가? 간단히 말하면, 수십 년 된 `Date` 객체의 문제(타임존 처리 어려움, 가변 객체, 달력 시스템 지원 부재 등)를 드디어 언어 표준으로 해결할 수 있게 됐다는 뜻이다. `moment.js`나 `date-fns`를 반드시 써야 했던 이유 중 상당 부분이 Temporal로 흡수된다.

V8 엔진도 14.6으로 올라가면서 새로운 JavaScript 표준 기능들이 함께 들어왔다. `Map.prototype.getOrInsert()` 같은 편의 API들이 런타임 레벨에서 지원된다. 그리고 몇 가지 주의해야 할 breaking change도 있다.

Node.js 26이 가져오는 변화를 실무 관점에서 정리해 본다.

## 본론

### Temporal API: 드디어 플래그 없이 쓸 수 있다

`Date` 객체는 JavaScript가 처음 만들어진 1995년에 설계됐다. 당시 기준으로는 충분했지만, 30년이 지난 지금 시점에서는 너무 많은 문제를 안고 있다:

- **가변(mutable) 객체**: `date.setMonth()`처럼 원본을 직접 수정하는 메서드들이 버그의 온상이 된다.
- **타임존 지원 미흡**: UTC와 로컬 타임존만 지원하며, 임의 타임존을 다루려면 서드파티 라이브러리가 필요하다.
- **달력 시스템**: 그레고리력만 지원하고 ISO 8601 외 다른 달력은 처리할 수 없다.
- **파싱 불일치**: `new Date('2026-05-08')` 같은 날짜 문자열 파싱이 브라우저·환경마다 동작이 다를 수 있다.

Temporal은 이 모든 문제를 처음부터 다시 설계한 API다. Node.js 26에서는 다음과 같이 플래그 없이 사용 가능하다:

```javascript
// Temporal.Now: 현재 시각을 다양한 형태로
const now = Temporal.Now.instant(); // 절대 시점 (Unix epoch 기반)
const localDateTime = Temporal.Now.plainDateTimeISO(); // 로컬 날짜+시각 (ISO 형식)
const inSeoul = Temporal.Now.zonedDateTimeISO('Asia/Seoul'); // 서울 타임존 기준

console.log(now.toString());
// → "2026-05-08T07:05:49.123456789Z"

console.log(inSeoul.toString());
// → "2026-05-08T16:05:49.123456789+09:00[Asia/Seoul]"
```

**타임존 기반 산술 연산**이 직관적으로 가능해진 것도 핵심이다:

```javascript
// 서울 기준 "지금으로부터 3일 후 오전 9시"
const seoulNow = Temporal.Now.zonedDateTimeISO('Asia/Seoul');
const threeDaysLater = seoulNow.add({ days: 3 }).with({ hour: 9, minute: 0, second: 0 });

console.log(threeDaysLater.toString());
// → "2026-05-11T09:00:00+09:00[Asia/Seoul]"
```

기존 `Date`로 이를 구현하려면 Unix timestamp를 직접 계산하거나 `moment-timezone` 같은 라이브러리를 써야 했다.

**불변(immutable) 설계**도 중요한 특징이다. Temporal의 모든 타입은 불변이며, 날짜를 변경하면 항상 새 객체가 반환된다:

```javascript
const date = Temporal.PlainDate.from('2026-05-08');
const nextWeek = date.add({ weeks: 1 });

console.log(date.toString());    // "2026-05-08" (원본 변경 없음)
console.log(nextWeek.toString()); // "2026-05-15"
```

주요 Temporal 타입들:

| 타입 | 설명 |
|------|------|
| `Temporal.Instant` | 절대 시점 (타임존 무관) |
| `Temporal.ZonedDateTime` | 타임존을 포함한 날짜+시각 |
| `Temporal.PlainDate` | 날짜만 (타임존 없음) |
| `Temporal.PlainTime` | 시각만 |
| `Temporal.PlainDateTime` | 날짜+시각 (타임존 없음) |
| `Temporal.Duration` | 기간(두 시점 사이의 차이) |

실무에서 Temporal이 가장 큰 가치를 발휘하는 영역은 **스케줄링, 예약 시스템, 국제화가 필요한 서비스**다. "서울 시간 기준 매일 오전 9시에 실행"처럼 타임존이 섞이는 로직을 `Date`로 구현하면 엣지 케이스가 끝도 없이 나온다. Temporal은 이 문제를 언어 표준 레벨에서 해결한다.

### V8 14.6: 새 JavaScript 기능들

Node.js 26이 탑재한 V8 14.6(Chromium 146 기반)은 몇 가지 유용한 새 JavaScript 기능을 가져왔다.

#### Map.prototype.getOrInsert() — Upsert API

```javascript
const cache = new Map();

// 기존 방식
function getOrCreate(key) {
  if (!cache.has(key)) {
    cache.set(key, computeExpensiveValue(key));
  }
  return cache.get(key);
}

// Node.js 26: getOrInsert
const value = cache.getOrInsert('myKey', computeExpensiveValue('myKey'));

// 또는 지연 계산이 필요하면 getOrInsertComputed
const value2 = cache.getOrInsertComputed('myKey', (k) => computeExpensiveValue(k));
```

`Map`과 `WeakMap` 모두에서 사용 가능하다. 캐싱 로직, 메모이제이션 패턴에서 보일러플레이트 코드를 크게 줄여준다.

#### Iterator.concat()

```javascript
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const set1 = new Set([7, 8]);

// Iterator.concat으로 여러 이터러블 순회
for (const item of Iterator.concat(arr1.values(), arr2.values(), set1.values())) {
  console.log(item); // 1, 2, 3, 4, 5, 6, 7, 8
}
```

배열·Set·Map 등 여러 이터러블을 별도의 배열 생성 없이 순차 처리할 수 있어, 메모리 효율적인 스트리밍 처리에 유용하다.

### Undici 8.0.2 업그레이드

Node.js의 내장 HTTP 클라이언트인 Undici가 8.0.2로 올라갔다. Undici는 `fetch()` API의 Node.js 구현체이기도 하다. 이번 업그레이드에서는 성능 개선과 호환성 수정이 주를 이룬다. `fetch()` API 사용 시 체감할 수 있는 변화는 크지 않지만, 내부적으로 연결 관리와 스트리밍 처리의 안정성이 향상됐다.

### Breaking Changes: 이것만 확인하면 된다

Node.js 26으로 업그레이드할 때 주의해야 할 주요 변경 사항들이다.

#### http.Server.prototype.writeHeader() 제거

```javascript
// ❌ 더 이상 사용 불가
res.writeHeader(200, { 'Content-Type': 'application/json' });

// ✅ 올바른 방법
res.writeHead(200, { 'Content-Type': 'application/json' });
```

`writeHeader()`는 오랫동안 deprecated 상태였다. 이번에 완전히 제거됐다. `writeHead()`로 교체하면 된다.

#### 레거시 스트림 모듈 완전 제거

다음 내부 모듈들이 완전히 제거됐다:

```javascript
// ❌ 제거됨
require('_stream_wrap');
require('_stream_readable');
require('_stream_writable');
require('_stream_duplex');
require('_stream_transform');
require('_stream_passthrough');
```

이 모듈들은 이전부터 `stream` 모듈을 통해 사용하도록 안내됐다:

```javascript
// ✅ 올바른 방법
const { Readable, Writable, Duplex, Transform, PassThrough } = require('stream');
```

대부분의 최신 코드베이스에서는 이미 `stream` 모듈을 사용하고 있을 것이다. 하지만 오래된 의존성 패키지 중 내부 모듈을 직접 참조하는 경우가 있을 수 있어 주의가 필요하다.

#### module.register() 런타임 Deprecation

ESM 커스텀 로더를 등록하는 `module.register()` API가 런타임 deprecation 경고를 발생시키기 시작한다. 아직 제거된 건 아니지만, 미래 버전에서 제거될 예정이므로 대안으로 마이그레이션을 시작해야 한다.

#### 빌드 환경 요구사항

- **GCC 13.2 이상** (소스 빌드 시)
- **Python 3.9 지원 종료** (Python 3.10 이상 필요)
- **Windows SDK 11** 버전 요구

직접 Node.js를 소스 빌드하는 환경이 아니라면 대부분 무관하다.

### LTS 전환 일정과 업그레이드 전략

Node.js 26은 2026년 10월에 LTS로 전환된다. 그 전까지는 "Current" 단계로, 적극적인 기능 추가와 패치가 이뤄진다.

현재 LTS 버전들의 지원 일정:

| 버전 | 상태 | 지원 종료 |
|------|------|---------|
| Node.js 22 | LTS (Active) | 2027년 4월 |
| Node.js 24 | LTS (현재 최신 LTS) | 2028년 4월 |
| Node.js 26 | Current → LTS (2026년 10월) | 2029년 4월 예정 |

프로덕션 환경에서는 LTS 버전이 안정적이다. 당장 Node.js 26으로 전환할 필요는 없지만, Temporal API를 포함한 신기능 개발이나 CI/CD 파이프라인 검증은 지금부터 시작해 두는 게 좋다. 10월 LTS 전환 시점에 검증 없이 급하게 올리면 예상치 못한 문제를 만날 수 있다.

### 업계 반응

Node.js 26 릴리스에서 커뮤니티의 반응은 Temporal API에 집중됐다. "수년간 기다려 온 변화"라는 평가와 함께, Node.js 공식 블로그의 릴리스 공지는 Hacker News에서 활발한 토론을 불러일으켰다.

일부 백엔드 개발자들은 "Temporal이 안정화되면 `date-fns`나 `luxon` 같은 라이브러리 의존성을 하나씩 제거할 수 있겠다"는 기대를 표현했다. 반면 "기존 코드베이스에서 `Date`와 `Temporal`이 혼재하는 과도기가 한동안 이어질 것"이라는 현실적인 지적도 있다. TypeScript 타입 정의의 완성도와 프레임워크들의 Temporal 지원 속도도 실질적인 도입 타이밍에 영향을 줄 요소다.

V8 14.6의 `Map.prototype.getOrInsert()`에 대해서는 "작지만 실용적인 추가"라는 평가가 많다. 캐시·메모이제이션 관련 코드에서 간결함을 높여주는 API이기 때문이다.

HelpNetSecurity는 "Node.js 26은 최신 JavaScript 기능의 이정표이자, 오랫동안 묵혀 있던 날짜 처리 문제에 대한 공식 해답"이라고 평가했다.

## 정리

- Node.js 26.0.0이 2026년 5월 5일 출시됐으며, 2026년 10월 LTS 전환 예정이다.
- **Temporal API가 플래그 없이 기본 활성화**됐다. 타임존 처리, 불변 설계, 달력 시스템 지원 등 `Date` 객체의 고질적 문제를 표준 API로 해결한다.
- V8 14.6 업그레이드로 `Map.prototype.getOrInsert()`, `Iterator.concat()` 등 편의 API가 추가됐다.
- Breaking change: `http.Server.prototype.writeHeader()` 제거, 레거시 스트림 내부 모듈 제거, `module.register()` 런타임 deprecation.
- 프로덕션 전환은 LTS 이후를 권장하나, 지금부터 Temporal API를 활용한 신규 코드 작성과 기존 코드 마이그레이션 검토를 시작하는 것이 좋다.
- `moment.js`나 `date-fns` 의존성의 점진적 제거를 장기 과제로 고려할 수 있다.

## Reference

- [Node.js 26.0.0 공식 릴리스 노트 — nodejs.org](https://nodejs.org/en/blog/release/v26.0.0)
- [Node.js 26 ships with Temporal API enabled by default — HelpNetSecurity](https://www.helpnetsecurity.com/2026/05/07/node-js-26-released/)
- [Node.js v26 Is Here: What Actually Changed — NodeSource](https://nodesource.com/blog/nodejs-v26-is-here)
- [Node.js 26 Released: What's New — InMotion Hosting](https://www.inmotionhosting.com/support/news/nodejs-v26-released/)
- [Temporal API — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal)
