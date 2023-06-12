---
title: '[Algorithm] Extended Euclidean'
categories: Algorithm
tags: Algorithm
---

## 문제

```html
ax+by = c 라는 정수 해를 갖는 방정식에 대해 a, b, c를 입력받았을 때 그 해 (x, y)를 구하시오.
```

## 입력

```html
9 15 12
```

## 출력

```html
8, -4
```

## 코드

```python
import math as m

def uclid(a, b):
    uclid_list = []

    while b > 0:
        uclid_list.append(a//b)
        a, b = b, a%b

    uclid_list = list(reversed(uclid_list))
    return uclid_list

a, b, d = map(int, input().split())
c = m.gcd(a, b)

x_prime = 1
y_prime = 0

for i in range(len(uclid(a,b))):
    x = y_prime
    y = x_prime - (y_prime * uclid(a,b)[i])

    x_prime = x
    y_prime = y

x = x* (d//c)
y = y* (d//c)

print(x, y)
```

## 설명

먼저 유클리드 호제법의 과정에서 만들어지는 몫들을 구하기 위해서 유클리스 호제법을 구현하였다.

그리고 유클리드 호제법의 과정에서 만들어지는 몫들을 역순으로 정렬하여 리스트에 저장하여 반환하는 함수를 만들었다.

함수 외부에서는 입력을 받고 math 라이브러리로 최대공약수를 구하였다.

x_prime과 y_prime을 설정해주고 for문을 통해 x와 y를 구하였다.

최종적으로 x와 y에 d를 최대공약수로 나눈 몫을 곱해주었다.

## 후기

유클리드 호제법에 대해 알고 있다면 구현에는 문제가 없는 난이도였다.
