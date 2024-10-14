---
title: "[Java] 자바 생성자 개념 정리"
date: 2024-10-11 09:14:33 +09:00
categories: [Java]
tag: [Java, BE]
---

## **생성자란?**

생성자는 **객체를 생성하는 역할**을 하는 클래스의 구성요소이다. 객체를 생성할 때 사용하는 new 키워드가 바로 이 생성자를 호출하는 것이다.  
즉, 인스턴스 생성을 담당하는 것은 new 키워드이며, 생성자는 `인스턴스 변수들을 초기화`하는 데 사용되는 특수한 메서드이다.

> - **객체와 인스턴스**
>   - 큰 의미 차이를 가지지는 않지만, 엄밀히 말하면 객체는 모든 인스턴스를 포괄하는 넓은 의미를 가지고, 인스턴스는 해당 객체가 어떤 클래스로부터 생성된 것인지를 강조한다.

생성자는 메서드와 비슷한 구조를 가지고 있으나 조건이 붙는다.

- 생성자의 이름은 반드시 클래스의 이름과 같아야 한다.
- 생성자는 리턴 타입이 없으며, void 키워드를 사용하지 않는다.

```java
Car c = new Car(); // Car() 부분이 생성자

c.name = "abd";
c.speed = 100;
c.weight = 10;

// 생성자 사용 시
Car c1 = new Car("abc", 100, 10); //
```

### **기본 생성자**

기본 생성자는 매개변수가 없는 생성자를 의미한다. 자바 컴파일러는 생성자가 클래스 안에 존재하지 않을 경우, 기본 생성자를 자동으로 추가해준다.

### **매개변수가 있는 생성자**

매개변수가 있는 생성자는 매개변수를 통해 호출해야 하며, 호출 시 해당 값을 받아 인스턴스를 초기화하는 데 사용한다.  
`new 생성자(값)`과 같은 형태로 생성자 매개변수에 알맞은 값을 넣어 생성자를 호출하면 객체를 생성할 수 있다.

```java
public class Car {
    public static void main(String[] args) {
        Car c = new Car("abc", 100, 10)
    }
}

class Car {
    Car(String n, int s, int w) {
        this.name = n;
        this.speed = s;
        this.weight = w;
    }
}
```

## **인스턴스 예제 (정보처리기사 실기 2024년 1회 문제)**

```java
class classOne {
    int a, b;

    public classOne(int a, int b) {
        this.a = a;
        this.b = b;
    }

    public void print() {
        System.out.println(a + b);
    }

}
class classTwo extends classOne {
    int po = 3;

    public classTwo(int i) {
        super(i, i+1);
    }

    public void print() {
        System.out.println(po*po);
    }
}

public class main {
    public static void main(String[] args) {
        classOne one = new classTwo(10);
        one.print();
    }
}
```

### **클래스 구조**

1. classOne

- 두 개의 정수 a와 b를 멤버 변수로 가지고 있음.
- 생성자에서 a와 b를 초기화
- print 메서드는 a와 b의 합을 출력

2. classTwo

- classOne을 상속받음
- 추가로 po라는 변수를 정의하고 초기값을 3으로 설정
- 생성자에서 super(i, i+1)을 호출하여 classOne의 생성자를 호출하고 a를 i, b를 i+1로 설정
- print 메서드는 po의 제곱을 출력

3. main

- classTwo의 인스턴스를 classOne 타입으로 참조
- one.print() 호출

### **실행 과정**

1. classTwo의 생성자 호출

- super(i, i+1)가 호출되어 classOne의 생성자 실행, a = 10, b = 11로 초기화
  > - super() 메서드?
  >   - 상속받은 부모의 생성자를 호출하는 메서드.
  >   - 여기에서는 classTwo (자식 클래스)의 부모인 classOne의 생성자를 호출하여 a와 b를 각각 10, 11로 초기화시킨다.

2. one.print() 호출

- one은 classTwo 타입의 객체를 참조하지만, 참조 타입은 classOne
- 다형성이 작동하여 classTwo의 print 메서드가 호출됨.

`즉, 다시 말해 one은 classTwo의 인스턴스를 참조하므로, classTwo의 print 메서드가 호출되는 것이다.`
