---
title: "[하루에 한번] 자료구조, 알고리즘 학습-1"
date: 2026-07-09 20:00:00 +09:00
categories: [자료구조]
tags: [자료구조]
encrypted: false
---

## 시간복잡도와 공간복잡도에 대해 설명해 주세요.
### Big-O, Big-Theta, Big-Omega에 대해 설명해 주세요.
 - Big-O : 최악의 경우를 상정한 시간복잡도 계산방법
 - Big-Theta
 - Big-Omega

### 다른 것을 사용하지 않고, Big-O를 사용하는 이유가 있을까요?
 - Big-O 표기법이 최악을 상정하는 만큼, 예외 상황을 통제할 수 있기 때문에 사용합니다.

### O(1)은 O(N^2)보다 무조건적으로 빠른가요?
 - 상수 시간이나 실제 구현 방식에 따라 작은 입력에서는 성립하지 않을 수 있습니다.

## 링크드 리스트에 대해 설명해 주세요.
### 일반 배열과 링크드 리스트를 비교해 주세요.
1. 데이터 저장 방식
 - 배열은 연속적인 메모리 공간에 데이터를 저장합니다.
 - 반면 링크드 리스트는 흩어져 있는 메모리 공간에 데이터를 저장하나, 다음 노드의 주소를 지니고 있습니다.

2. 삽입/삭제/접근에 대한 성능
 - 위와 같은 저장 방식의 차이점을 이유로 배열은 중간 데이터에 대한 삽입, 삭제가 어렵고 접근이 빠릅니다.
 - 반면 링크드 리스트는 중간 데이터에 대한 삽입, 삭제가 쉽고 접근이 느립니다. (= 처음부터 따라가야해서)

### 링크드 리스트를 사용해서 구현할 수 있는 다른 자료구조에 대해 설명해 주세요.
 - 스택, 큐, 데큐, 해시 테이블, 그래프, LRU 캐시, 원형 큐

## 스택과 큐에 대해서 설명해 주세요.
### 스택 2개로 큐를, 큐 2개로 스택을 만드는 방법과, 그 시간복잡도에 대해 설명해 주세요.
 - 첫번째 스택에 저장된 데이터를 pop()을 통해서 두번째 스택으로 옮긴 후 두번째 스택에서 pop()을 진행하면 FIFO 형태가 완성된다. 시간복잡도는 O(1).
 - 하나의 요소를 넣을 때마다 빈 큐에 넣고 기존에 저장된 데이터들을 뒤로 붙힌다. (그러면 빈 큐와 데이터가 저장된 큐 두 가지가 생성됨). 시간복잡도는 input은 O(N), output은 O(1).

### 시간복잡도를 유지하면서, 배열로 스택과 큐를 구현할 수 있을까요?
 - 배열의 끝까지 가면 다시 처음으로 돌아가는 원형 큐를 활용하면 됩니다.
 
```java
class CircularQueue {
    int[] arr;
    int front = 0;
    int rear = 0;
    int size = 0;

    CircularQueue(int capacity) {
        arr = new int[capacity];
    }

    void enqueue(int value) {
        if (size == arr.length) {
            System.out.println("큐가 가득 찼습니다.");
            return;
        }

        arr[rear] = value;
        rear = (rear + 1) % arr.length;
        size++;
    }

    int dequeue() {
        if (size == 0) {
            System.out.println("큐가 비었습니다.");
            return -1;
        }

        int value = arr[front];
        front = (front + 1) % arr.length;
        size--;

        return value;
    }
}
```

### Prefix, Infix, Postfix에 대해 설명하고, 이를 스택을 활용해서 계산하는 방법에 대해 설명해 주세요.
 - Prefix, Infix, Postfix는 각각 전위, 중위, 후위를 뜻하며 연산자의 위치에 따라 다르게 불립니다.

```python
# example
(3 + 4) * 5

# Prefix
* + 3 4 5

# Infix
(3 + 4) * 5

# Postfix
3 4 + 5 *
```

```java
import java.util.*;

public class Calculator {
    public static int calPrefix(String expression) {
        // * + 3 4 5
        Deque<Integer> deque = new ArrayDeque<>();
        String[] tokens = expression.trim().split("\\s+");

        for (int i = tokens.length - 1; i >= 0; i--) {
            Stirng token = tokens[i];
            if (isOp(token)) {
                int left = deque.pop();
                int right = deque.pop();
                int result = calc(left, right, token);

                deque.push(result);
            } else {
                deque.push(Integer.parseInt(token));
            }
        }
        return deque.pop();
    }

    public static int calPostfix(String expression) {
        // 3 4 + 5 *
        Deque<Integer> deque = new ArrayDeque<>();
        String[] tokens = expression.trim().split("\\s+");

        for (String token : tokens) {
            if (isOp(token)) {
                int right = deque.pop();
                int left = deque.pop();
                int result = calc(left, right, token);
                
                deque.push(result);
            } else {
                deque.push(Integer.parseInt(token));
            }
        }
        return deque.pop();
    }

    private static boolean isOp(String token) {
        return token.equals("+") || token.equals("-") || token.equals("*") || token.equals("/");
    }

    private static int calc(int left, int right, String op) {
        switch (op) {
            case "+":
                return left + right;
            case "-":
                return left - right;
            case "*":
                return left * right;
            case "/":
                return left / right;
            default:
                throw new IllegalArgumentException("Not Supply: " + op);
        }
    }
}

```

### Deque는 어떻게 구현할 수 있을까요?
 - Deque는 양 옆이 각각 출입구의 역할이 가능한 형태의 자료구조입니다.
 - 이는 여러 가지 방법(스택 2개, 큐 2개, 양방향 링크드 리스트 등)이 있지만 가장 권장되는 방법은 원형 배열을 활용한 구현입니다.


## 출처
[VSFe님의 Tech-Interview](https://github.com/VSFe/Tech-Interview)