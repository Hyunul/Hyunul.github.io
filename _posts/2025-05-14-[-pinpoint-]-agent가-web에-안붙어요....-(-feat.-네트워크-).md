---
title: "[ Pinpoint ] Agent가 Web에 안붙어요.... ( feat. 네트워크 )"
date: 2025-05-14 09:39:38 +09:00
categories: [BE]
tag: [Pinpoint, Monitoring]
---

### 문제 상황

Pinpoint-Docker의 모든 세팅을 완료한 뒤에 가벼운 발걸음으로 Pinpoint-Web에 접속한 순간 이게 무슨 일이람...

어플리케이션을 찾을 수 없다고 하네 ?!!

![](https://blog.kakaocdn.net/dna/cpf4Oc/btsNXBjmbk8/AAAAAAAAAAAAAAAAAAAAAF7lvgabK6l9v_1IKDZnrEzMvy4dtI_P3J8KzGKnpVhE/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=78L85JFmx70%2ByAVdzPGrm78zyCs%3D)

### 해결 과정

무엇이 문제일까... 고민을 해봤는데 어떻게 봐도 네트워크 설정이 문제인 것 같았다.

현재 상황은 다음과 같다.

![](https://blog.kakaocdn.net/dna/Hxwcl/btsNVIc7MuK/AAAAAAAAAAAAAAAAAAAAANvIemQUND4ZDusU0D_IyOVx8hUEFNe87kwlloVL_yMx/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=laCyf8s2oB%2FbdaODLKA77L3H1BI%3D)

다른 컨테이너에서 Agent와 Pinpoint를 구동중이었고,

![](https://blog.kakaocdn.net/dna/bjLCEy/btsNVDbWbnc/AAAAAAAAAAAAAAAAAAAAAP5x4euwvKsxUqR0DdbSQzKy8dGVRUYAX2xzokgd0cN3/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=MYl6NAdjkqex%2FOacMGJ93fJPFYE%3D)

grpc 콜렉터의 ip를 로컬 호스트(기본 값)로 준 상태였다.

Agent 쪽에서 Pinpoint 쪽 주소를 모르니까 어플리케이션 연동이 되지 않았던 것이었다.

### 해결 방안

따라서 grpc 콜렉터의 ip를 수정해주면 되는데, 무엇으로 수정하면 될까?

나는 다음과 같은 방법으로 문제를 해결했다.

도커가 무슨 형태로 ip를 나눠쓸까하면서 이번에도 어김없이 등장한 Docker Desktop의 Inpect.

![](https://blog.kakaocdn.net/dna/etdHdM/btsNWtzwg9d/AAAAAAAAAAAAAAAAAAAAALi6acRLCrZeyWsapboSVk3bE7apvFcs7p6cEWLHQD4c/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=DWKK2uN5EQGYXZ0dP2JJv4WeoiE%3D)

네 브릿지라고 하네요.

그럼 주저없이 cmd 창을 켜서 "ipconfig" 입력 !!

![](https://blog.kakaocdn.net/dna/BmQTO/btsNWFT6L02/AAAAAAAAAAAAAAAAAAAAAFXGmV-_muotBj0xAriujR2W321BI7TxivPhFnAATTjk/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=lV9DtYF2nJvvpYohtR393yxDyts%3D)

여기에서 IPv4 주소를 입력해주면 된다!!

![](https://blog.kakaocdn.net/dna/0ao0R/btsNWj4YWj1/AAAAAAAAAAAAAAAAAAAAAAZKBjVtlCvtoek8rxhxAZz5h8r7AD_36sbQBjH8g7gF/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=%2FqtFc7%2FnqgOWg%2FtG%2BD4q2VjGtN8%3D)

그럼 위와 같이 내 어플리케이션이 리스트업 되는 것을 볼 수 있다!!
