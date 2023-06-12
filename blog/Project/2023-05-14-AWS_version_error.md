---
title: '[Error] node: /lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)'
categories: Error
tags: Error
---

제작한 웹페이지를 AWS에 배포하려고 하니 다음과 같은 에러가 발생했다.

```
node: /lib64/libm.so.6: version `GLIBC_2.27' not found (required by node)
```

찾아본 결과, 위의 에러는 Linux2에서 node 버전 18.0.0을 사용할 때 발생하는 에러라고 한다.
즉, node 버전 18을 지원하지 않는 것이다.

따라서 이 문제를 해결하기 위해서는 node의 버전을 낮춰줘야 하므로 다음과 같은 명령어를 사용해서 해결할 수 있다.

```
nvm use 17
```
