---
title: '[Algorithm] Dijsktra Algorithm'
categories: Algorithm
tags: Algorithm
---

## 문제

노드의 개수(N)와 출발 노드의 번호, 각 노드를 연결하는 경로 정보 및 그 경로의 이동 비용(W)가 주어졌을 때, 출발 노드에서 각 노드까지 가는 최소 비용을 구하시오. 경로가 존재하지 않는 노드의 경우 ‘not connected’라고 출력하시오.

## 입력

```
5 6
1
5 1 1
1 2 2
1 3 3
2 3 4
2 4 5
3 4 6
```

## 출력

```
1: 0
2: 2
3: 3
4: 7
5: not connected
```

## 코드

```python
import heapq

n, m = map(int, input().split())

k = int(input())
INF = 1e8

graph = [[] for _ in range(n+1)]

distance = [INF] * (n+1)

for _ in range(m):
    u, v, w = map(int, input().split())
    graph[u].append((v, w))


def dijkstra(start):
    q = []
    heapq.heappush(q, (0, start))
    distance[start] = 0

    while q:
        dist, now = heapq.heappop(q)

        if distance[now] < dist:
            continue

        for i in graph[now]:
            if dist+i[1] < distance[i[0]]:
                distance[i[0]] = dist+i[1]
                heapq.heappush(q, (dist+i[1], i[0]))

dijkstra(k)

distance.remove(INF)

for j in range(len(distance)):
    if distance[j] != INF:
        print(j+1, distance[j])
    else:
        print(j+1, "not connected")
```

## 설명

이 문제는 노드를 방문할 때마다 거리를 업데이트하는 방식으로 최단 경로를 찾는 "다익스트라 알고리즘" 문제이다. 이 문제는 파이썬의 유용한 라이브러리 중 하나인 heapq (우선순위 큐)를 활용하면 간단하게 풀 수 있다.

우선 순위가 가장 낮은 값을 뽑아서 기존에 입력되어 있는 값보다 크다면 무시하고, 작다면 업데이트하는 방식으로 최단 경로를 찾는다.

마지막에는 출력 결과를 맞춰주기 위해 첫 인덱스에 삽입해두었던 INF 값을 제거하고 출력 양식에 맞게 조정해준다.
