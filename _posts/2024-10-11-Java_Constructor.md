---
title: "[Java] 생성자 개념, 종류, 동작 방식 정리"
date: 2024-10-11 09:14:33 +09:00
categories: [Java]
tag: [Java, Constructor, OOP]
---

## 생성자란?

생성자는 객체를 생성할 때 호출되어 인스턴스의 상태를 초기화하는 특별한 메서드다.
`new` 키워드로 객체를 만들 때 실제로 함께 호출되는 것이 바로 생성자다.

즉, 인스턴스 생성을 시작하는 것은 `new`이고, 생성자는 그 과정에서 `인스턴스 변수들을 초기화`하는 역할을 맡는다.

> **객체와 인스턴스**
>
> 두 용어는 비슷하게 쓰이지만, 보통 객체는 더 넓은 개념이고 인스턴스는 특정 클래스로부터 생성된 객체라는 점을 강조할 때 사용한다.

생성자는 일반 메서드와 비슷해 보이지만 다음 조건이 있다.

- 생성자 이름은 클래스 이름과 같아야 한다.
- 반환 타입을 적지 않으며 `void`도 사용하지 않는다.

```java
class Car {
    String name;
    int speed;
    int weight;

    Car() {
    }

    Car(String name, int speed, int weight) {
        this.name = name;
        this.speed = speed;
        this.weight = weight;
    }
}

Car c = new Car(); // 기본 생성자 호출
Car c1 = new Car("abc", 100, 10); // 매개변수가 있는 생성자 호출
```

### 기본 생성자

기본 생성자는 매개변수가 없는 생성자를 의미한다.
자바 컴파일러는 클래스 내부에 생성자가 하나도 없으면 기본 생성자를 자동으로 추가해준다.

### 매개변수가 있는 생성자

매개변수가 있는 생성자는 호출할 때 필요한 값을 전달받아 인스턴스를 초기화한다.
따라서 객체를 생성하는 시점에 필요한 값을 함께 넘기고 싶을 때 자주 사용한다.

## 예제 (정보처리기사 실기 2024년 1회 문제)

```java
class ClassOne {
    int a, b;

    public ClassOne(int a, int b) {
        this.a = a;
        this.b = b;
    }

    public void print() {
        System.out.println(a + b);
    }
}

class ClassTwo extends ClassOne {
    int po = 3;

    public ClassTwo(int i) {
        super(i, i + 1);
    }

    @Override
    public void print() {
        System.out.println(po * po);
    }
}

public class Main {
    public static void main(String[] args) {
        ClassOne one = new ClassTwo(10);
        one.print();
    }
}
```

### 클래스 구조

1. `ClassOne`

- 정수형 필드 `a`, `b`를 가진다.
- 생성자에서 `a`, `b`를 초기화한다.
- `print()`는 `a + b`를 출력한다.

2. `ClassTwo`

- `ClassOne`을 상속한다.
- `po`라는 필드를 추가로 가지며 기본값은 `3`이다.
- 생성자에서 `super(i, i + 1)`을 호출해 부모 생성자를 실행한다.
- `print()`를 오버라이딩해서 `po * po`를 출력한다.

3. `Main`

- `ClassTwo` 객체를 `ClassOne` 타입으로 참조한다.
- 이후 `one.print()`를 호출한다.

### 실행 과정

1. `new ClassTwo(10)`이 실행되면 먼저 `ClassTwo` 생성자가 호출된다.
2. 생성자 내부의 `super(i, i + 1)`에 의해 부모 클래스 `ClassOne`의 생성자가 먼저 실행된다.
3. 이때 `a = 10`, `b = 11`로 초기화된다.
4. 이후 `one.print()`를 호출하면, 참조 타입이 아니라 실제 객체 타입을 기준으로 메서드가 선택된다.
5. 따라서 다형성에 의해 `ClassTwo`의 `print()`가 실행되고 결과는 `9`가 된다.

`즉, 부모 타입으로 참조하더라도 실제 객체가 자식 클래스라면 오버라이딩된 메서드가 호출된다.`
