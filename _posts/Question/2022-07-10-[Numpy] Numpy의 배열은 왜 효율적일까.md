---
title:  "[Python] Numpy의 배열은 왜 효율적일까"
categories: Question
tags: Python Question
---

---

# 리스트보다 Numpy의 배열이 효율적인 이유

파이썬의 리스트와 Numpy의 배열은 여러 개의 값들을 저장할 수 있는 자료구조, 데이터를 수정하거나 추가 및 제거할 수 있는 기능을 가지고 있다는 점에서 공통점을 지니고 있다.

하지만 데이터 과학에서 파이썬의 리스트와 Numpy의 배열은 큰 차이를 보인다. 데이터를 처리할 때는 **리스트와 리스트 간의 다양한 연산을 요구**하게 되는데, 파이썬의 리스트는 이러한 기능이 부족하여 리스트를 연산하는 속도가 느린 반면에 Numpy는 고차원적인 수학 연산자와 함수를 지원하기 때문에 대용량의 배열과 행렬 연산을 빠르게 수행할 수 있다.

**아래의 표와 같이 Numpy의 배열은 주황색으로 표시된 파이썬의 리스트에 비해 처리속도가 매우 빠름을 알 수 있다.**

![png](/assets/images/Numpy&List.png)
출처 : [https://dkswnkk.tistory.com/%E3%85%81](https://dkswnkk.tistory.com/%E3%85%81)

---

# Numpy의 배열이 파이썬의 리스트보다 빠른 이유

1. Numpy는 저급 언어인 C언어로 구현되어 있다.
2. Numpy는 한 task를 subtask로 나눠 병렬적으로 처리한다.
3. 주소값 저장이 아닌 실제 값을 메모리에 가지고 있기 때문에 메모리에 값이 연속적으로 저장되어 있고 이로 인하여 속도가 빠르다.

![png](/assets/images/Numpy&List%20memory.png)
출처 : [https://velog.io/@ganta/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EA%B8%B0%EC%B4%886](https://velog.io/@ganta/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EA%B8%B0%EC%B4%886)