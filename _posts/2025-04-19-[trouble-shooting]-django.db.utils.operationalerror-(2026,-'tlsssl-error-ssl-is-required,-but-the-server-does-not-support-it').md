---
title: "[Trouble Shooting] django.db.utils.OperationalError: (2026, 'TLS/SSL error: SSL is required, but the server does not support it')"
date: 2025-04-19 17:59:30 +09:00
categories: [Error]
tag: [Troubleshooting]
---

포트폴리오 업데이트를 위해 이전에 했던 프로젝트들을 실행시켜보던 중, 아래와 같은 에러를 마주하게 되었습니다.

```
django.db.utils.OperationalError: (2026, 'TLS/SSL error: SSL is required, but the server does not support it')
```

먼저, 이 에러가 발생한 이유는 mysqlclient 버전이 2.2.4에서 2.2.5로 업그레이드되었기 때문인데요.

이 에러를 해결하기 위한 시도는 다음과 같습니다.

### 1. settings.py에서 database 설정에 OPTIONS 추가하기.

```
DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'ssl': None,
        },
    }
}
```

위와 같이 'OPTIONS'를 추가하여 ssl 모드를 비활성화시킵니다. 이 시도를 통해 많은 사람들이 해결되었다고 말하였으나, 저의 경우에는 정답이 아니었습니다.

### 2. mysqlclient 버전 다운그레이드

```
pip install "mysqlclient==2.2.4"
```

위의 명령어를 실행함으로써 mysqlclient의 버전을 강제로 다운그레이드시킵니다.

저는 2번의 방법을 통해 문제를 해결할 수 있었습니다.
