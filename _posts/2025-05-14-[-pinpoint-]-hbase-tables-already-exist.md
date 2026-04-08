---
title: "[ Pinpoint ] HBase Tables already exist"
date: 2025-05-14 09:19:59 +09:00
categories: [BE]
tag: [Pinpoint, Monitoring]
---

### 문제 상황

Docker 기반으로 Pinpoint의 환경 설정을 진행하던 중, 다음과 같은 문제 상황이 발생했다.

1. Pinpoint-Web의 WebUI는 정상적으로 나오나, Agent에 연결된 나의 App이 검색되지 않음.

2. 로그를 따라가보니, HBase에 다음과 같은 오류가 생겨서 Pinpoint-Web에서 읽어오지 못함.

```
Tables already exist
```

### 해결 방안

이는 Pinpoint-Docker 이미지를 실행시킨 후에 HBase 컨테이너에서 발생한 오류로, 원인은 기존에 존재하던 데이터와 충돌이다.

따라서 해결 방안은 기존에 존재하는 데이터를 삭제하고, hbase-create.hbase 파일을 실행시켜 제작자가 의도했던대로 돌려놓으면 된다.

### 환경

* Windows 10
* hbase-2.2.6
* Docker Desktop

### 해결 과정

먼저 HBase 컨테이너가 실행되면 어떤 흐름이 발생하는 지 파악하는 것이 우선이다.

pinpoint-hbase 컨테이너의 Inspect 내에 존재하는 Args를 보자.

![](https://blog.kakaocdn.net/dna/bpevX7/btsNXpckPUc/AAAAAAAAAAAAAAAAAAAAACUgf-kZi3kXJFMVRLfj_Vnf2a5jMzyrrPezgecsRoib/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=rXC0SfFeVIiSJvrlMzoyQxtzdRc%3D)

컨테이너가 실행되면 /usr/local/bin/initialize-hbase.sh 가 실행되는 것을 알 수 있다.

그럼 initialize-hbase.sh가 뭔지 봐야겠지?

![](https://blog.kakaocdn.net/dna/qr0qJ/btsNWr9zkoF/AAAAAAAAAAAAAAAAAAAAAG45uv7zxjc_RPGbWFkJe9QoGNWxYyJwpreL124Aka7j/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=IzYeZSEWN2IKNoWiWDukZqMomg8%3D)

얘는 start-base.sh와 configure-hbase.sh를 실행시키는 애구나.

즉, 컨테이너 실행 > start-hbase.sh && configure-hbase.sh가 되는거다.

start-hbase는 hbase를 시작하는 스크립트일테고, 이후에 실행되는 configure-hbase.sh와 check-table.sh가 무슨 스크립트인지 봐야한다.

![](https://blog.kakaocdn.net/dna/okd1x/btsNVejg9z9/AAAAAAAAAAAAAAAAAAAAAJpLxgvx-iS9GyRiKWCsFn3zOm2ZIOyVge1No0vc9PE9/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=ehL4lpCtcrV2kan5JJVcckhcQa4%3D)

먼저 configure.sh는 hbase의 테이블을 만드는 스크립트를 업데이트 스크립트로 치환하여 복사하는 스크립트인 것을 알 수 있다.

그럼 check-table.sh는?

![](https://blog.kakaocdn.net/dna/cOpsOS/btsNUOkTwH2/AAAAAAAAAAAAAAAAAAAAALo8oyCOVrK5KqaDTFCepJ7QfRISDJo83jdCPqX8cyFO/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=Bf9wnrxCA4yLSdOnxeKhPPxrIOY%3D)

보아하니, 테이블의 유무에 따라 테이블의 업데이트 및 생성하는 역할을 하는 스크립트인 것을 알았다.

그럼 테이블의 유무는 어떻게 보는데? 이것 또한 컨테이너의 Inspect 탭에서 확인이 가능하다. 바로 여기서 !!

![](https://blog.kakaocdn.net/dna/oPbJ5/btsNUOZuxd7/AAAAAAAAAAAAAAAAAAAAAOOf0ddewkj8oMlro32H0flTuMKIQafbs_JpTmkveEyF/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=d3PCEXK3EK0AKRQbgrPw9lmq1Lc%3D)

찾아가보면 다음과 같은 데이터들이 존재하는 것을 알 수 있다.

![](https://blog.kakaocdn.net/dna/dBocNi/btsNUOLVOB2/AAAAAAAAAAAAAAAAAAAAABUWIkXoSB0MmToa3sXsqP6ZEjMgIUZNHoFEDG6YdIHQ/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=BqtZxrxZUCyypdcz9GXtsln2DuM%3D)

그럼 얘네들을 삭제하고 다시 hbase-create.hbase 를 실행해주면 오류 해결 !

웹에서도 잘 나오는 것을 확인할 수 있다.

![](https://blog.kakaocdn.net/dna/4jOmA/btsNVIEftw5/AAAAAAAAAAAAAAAAAAAAAI20RmEQw0XRl8gTJIipH1baug4mFanT191fxJakdj-e/img.png?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=u0ugwrktrlNZFxSTWN%2FSRST9SWY%3D)

이제 정리를 해보자.

1. 컨테이너가 실행됨에 따라 스크립트들이 순차적으로 실행 ( initialize > check-table > create or update table )

2. 그러나 기존에 존재하던 데이터들과 충돌이 일어남으로써 흐름이 꼬임 ( 원인은 모르겠다... 감히 예상하지만 최신 버전에서 제작자의 휴먼 에러가 발생하지 않았을까... 싶다.. )

3. 그러니까 기존에 있던 HBase 테이블 데이터 삭제하고 테이블 생성 스크립트 다시 실행해주면 HBase 문제는 해결 !!

다음 글에서는 Pinpoint-Web에 Agent가 연결되지 않는 문제상황에 대해서 포스팅할 예정이다!
