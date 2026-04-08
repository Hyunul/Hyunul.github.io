---
title: "[Trouble Shooting] Git에 대용량 파일을 실수로 추가했을 때 해결 가이드 (feat. hprof)"
date: 2025-12-15 13:05:20 +09:00
categories: [Error]
tag: [Troubleshooting]
---

IntelliJ IDEA에서 OOM(Out Of Memory)이 발생하면 \*.hprof 힙 덤프 파일이 자동 생성될 수 있다.
이를 인지하지 못하고 git add 또는 git commit까지 진행하면, GitHub의 **100MB 파일 제한** 때문에 push가 실패한다.

아래는 \*\*상황별(분기별)\*\*로 바로 복붙해서 해결할 수 있도록 정리한 가이드다.

---

## 1️⃣ git add만 한 경우 (commit 전)

> 아직 commit을 하지 않았다면 **아주 간단하게 해결 가능**

### 1-1. 스테이징에서 파일 제거

```
git reset HEAD 경로/파일명.hprof
```

### 1-2. 실제 파일도 삭제 (권장)

```
rm 경로/파일명.hprof
```

### 1-3. 재발 방지용 .gitignore 추가

```
echo "*.hprof" >> .gitignore
git add .gitignore
git commit -m "Add hprof to gitignore"
```

✅ 이 경우 **Git 히스토리에 대용량 파일이 남지 않음**

---

## 2️⃣ git commit까지 한 경우 (push 전)

> 이미 commit에 포함되었기 때문에
> **Git 히스토리에서 완전히 제거**해야 함

### 2-1. 현재 커밋에 포함된 hprof 파일 확인

```
git show --stat
```

또는

```
git ls-files | grep hprof
```

---

### 2-2. git filter-repo 설치

```
pip install git-filter-repo
```

설치 확인

```
git filter-repo --help
```

---

### 2-3. hprof 파일을 모든 커밋에서 제거

```
git filter-repo --path 경로/파일명.hprof --invert-paths
```

의미:

* 해당 파일을 **Git 히스토리 전체에서 완전히 삭제**
* 커밋 기록이 재작성됨

---

### 2-4. 강제 push (필수)

```
git push origin --force
```

⚠️ 주의

* 협업 중인 저장소라면 팀원에게 반드시 공지
* 기존 히스토리를 기반으로 작업 중인 브랜치는 재정리 필요

---

### 2-5. 재발 방지 (.gitignore)

```
echo "*.hprof" >> .gitignore
git add .gitignore
git commit -m "Ignore hprof files"
```

---

## 3️⃣ 상황별 요약

상황해결 방법

|  |  |
| --- | --- |
| git add만 함 | git reset HEAD 파일 |
| git commit까지 함 | git filter-repo 사용 |
| push까지 함 | git filter-repo + force push |

---

## 4️⃣ 핵심 명령어만 정리

### add만 한 경우

```
git reset HEAD 파일명.hprof
rm 파일명.hprof
```

### commit까지 한 경우

```
pip install git-filter-repo
git filter-repo --path 파일명.hprof --invert-paths
git push origin --force
```

---

## 5️⃣ 마무리

용량 파일 문제는 **초기에 인지하면 간단한 이슈**이지만,
커밋 이후에는 히스토리 정리가 필요하다.

.gitignore에 \*.hprof를 추가해두는 것만으로도
같은 실수를 확실히 예방할 수 있다.
