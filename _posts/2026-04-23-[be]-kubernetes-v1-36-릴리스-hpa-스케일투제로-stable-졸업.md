---
title: "[BE] Kubernetes v1.36 릴리스 — 7년 기다린 HPA Scale-to-Zero 드디어 기본 활성화"
date: 2026-04-23 07:02:00 +09:00
categories: [BE]
tag: [Kubernetes, k8s, HPA, 컨테이너, 오케스트레이션]
---

## 서론

2026년 4월 22일, Kubernetes v1.36이 공식 출시됐다. 이번 릴리스에는 총 80개의 기능 개선이 담겼으며, 그 중 18개가 Stable로 졸업하고 18개가 Beta로 승격됐다. 새로운 Alpha 기능도 26개가 추가됐다.

v1.36은 "화려한 신기능"보다는 "오랫동안 기다려왔던 것들이 드디어 안정화됐다"는 성격이 강한 릴리스다. 가장 눈에 띄는 것은 두 가지다. 첫째, 2019년 v1.16에서 처음 제안된 이후 무려 7년을 Alpha/Beta에 머물러온 **HPA Scale-to-Zero** 기능이 v1.36부터 기본 활성화된다. 둘째, 루트리스 컨테이너를 Kubernetes 네이티브로 구현할 수 있는 **User Namespaces**가 Stable로 졸업한다.

동시에, `gitRepo` 볼륨 플러그인의 영구 비활성화, Ingress-NGINX 공식 지원 종료라는 크리티컬한 제거/지원 종료 항목도 포함되어 있어 프로덕션 운영 팀이라면 업그레이드 전에 꼼꼼히 점검해야 한다.

## 본론

### HPA Scale-to-Zero: 7년 만의 안정화

`HPAScaleToZero` 피처 게이트가 v1.36부터 기본 활성화(enabled by default)된다. Horizontal Pod Autoscaler(HPA)가 트래픽이 전혀 없을 때 파드를 0개까지 스케일 다운하고, 요청이 들어오면 다시 스케일 업할 수 있게 해주는 기능이다.

처음 제안된 건 2019년 Kubernetes v1.16이었다. 개념 자체는 단순하지만, 실제 구현에는 여러 복잡한 문제가 있었다. "0개 파드가 존재할 때 새 요청이 오면, HPA는 이를 어떻게 감지해 스케일-업 신호를 보낼 것인가?"라는 문제가 핵심이다. HPA 자체는 메트릭(CPU, 메모리, 커스텀 메트릭)을 기반으로 스케일링을 결정하는데, 파드가 0개면 수집할 메트릭 자체가 없다.

따라서 실제로 0 → 1 스케일업이 이루어지려면 외부 이벤트 기반 메트릭 어댑터가 필요하다. **KEDA(Kubernetes Event-Driven Autoscaling)**가 대표적인 파트너다. KEDA는 HTTP 요청, 메시지 큐 깊이, Cron 스케줄 등 외부 이벤트를 기반으로 0개 상태에서도 스케일업 신호를 생성할 수 있다.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 0  # v1.36부터 기본 지원
  maxReplicas: 10
  metrics:
  - type: External
    external:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "5"
```

비용 절감 효과는 환경에 따라 상당할 수 있다. DEV Community의 분석에 따르면, 야간이나 주말에 트래픽이 거의 없는 개발/스테이징 환경에서 HPA Scale-to-Zero를 적용하면 컴퓨팅 비용을 최대 70% 줄일 수 있다는 계산이 나온다. 프로덕션 환경에서도 비동기 배치 워크로드나 이벤트 기반 처리 파이프라인에는 충분히 적용 가능하다.

0 → 1 스케일업에 걸리는 콜드 스타트 시간(일반적으로 수 초~수십 초)이 사용자 경험에 영향을 주는 실시간 서비스에는 적합하지 않을 수 있다는 점도 유의해야 한다.

### User Namespaces: 루트리스 컨테이너의 네이티브 표준화

`hostUsers: false` 한 줄만 Pod spec에 추가하면, 컨테이너가 호스트 OS와 격리된 별도의 사용자 네임스페이스에서 실행된다. 컨테이너 내부에서 `root`(UID 0)로 동작하더라도, 호스트 OS 입장에서는 권한 없는 일반 사용자로 보이는 구조다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: rootless-pod
spec:
  hostUsers: false  # 사용자 네임스페이스 격리 활성화
  containers:
  - name: app
    image: my-app:latest
    securityContext:
      runAsUser: 0  # 컨테이너 내부에서는 root이지만
                    # 호스트에서는 권한 없는 사용자로 매핑
```

이 기능이 중요한 이유는 **컨테이너 탈출(container escape) 공격의 임팩트를 크게 줄여주기** 때문이다. 공격자가 컨테이너 취약점을 통해 컨테이너 탈출에 성공하더라도, 호스트에서 `root` 권한을 얻지 못한다. 컨테이너 내부의 `root`가 호스트에서 실제 권한 없는 UID로 매핑되어 있기 때문이다.

v1.36 이전까지는 이를 구현하려면 `rootless` 모드를 지원하는 특수한 컨테이너 런타임 설정이나 서드파티 툴링이 필요했다. 이제 표준 Kubernetes API만으로 가능하다.

다만, 커널 및 컨테이너 런타임(containerd 2.0+, CRI-O 1.30+) 지원이 필요하다는 제약은 여전히 있다. 운영 중인 노드의 커널 버전과 런타임 버전을 먼저 확인해야 한다.

### OCI 볼륨 Stable 졸업

OCI(Open Container Initiative) 이미지를 컨테이너 볼륨으로 마운트하는 기능이 Stable로 졸업했다. Pod spec에서 OCI 이미지를 `volume`으로 선언하고, 이를 여러 컨테이너가 읽기 전용 파일시스템으로 공유할 수 있다.

```yaml
volumes:
- name: model-weights
  image:
    reference: registry.example.com/ml-models/bert-base:v2
    pullPolicy: IfNotPresent
containers:
- name: inference-server
  volumeMounts:
  - name: model-weights
    mountPath: /models
```

활용 사례로는 다음과 같은 패턴이 있다. ML 모델 웨이트나 공통 설정 파일을 메인 애플리케이션 이미지와 분리된 OCI 아티팩트로 관리하고, 필요한 Pod에서만 마운트하는 방식이다. 이미지 레이어 캐싱을 그대로 활용할 수 있어 배포 효율이 높아지고, 모델 버전 관리를 컨테이너 이미지 태그로 깔끔하게 할 수 있다는 장점도 있다.

### SELinux 마운트 최적화 Stable 졸업

v1.27 Beta 이후로 긴 여정을 거쳐, SELinux 보안 컨텍스트를 볼륨 마운트 시점에 적용하는 기능이 Stable로 졸업했다.

기존 방식에는 심각한 성능 문제가 있었다. 볼륨 내 파일 하나하나에 재귀적으로 SELinux 레이블을 붙이는 방식이었기 때문에, 볼륨에 파일이 수백만 개 있으면 Pod 기동 시간이 수십 분까지 늘어나는 일이 발생했다.

새 방식은 볼륨 자체를 마운트할 때 SELinux 마운트 옵션(`-o context=...`)으로 레이블을 한 번에 적용한다. 파일 개수에 무관하게 마운트 시점에 레이블 적용이 완료된다. Pod 시작 시간이 수분에서 수초로 단축되는 효과가 있다.

SELinux를 활성화한 RHEL/CentOS/Fedora 기반 노드에서 Kubernetes를 운영하는 팀이라면 이 개선의 효과를 체감할 수 있다.

### 주요 제거 및 지원 종료 항목

**1. gitRepo 볼륨 플러그인 영구 비활성화**

`gitRepo` 볼륨 타입이 v1.36부터 완전히 비활성화된다. 이 플러그인은 Pod 기동 시 내부적으로 `git clone`을 실행해 레포 내용을 볼륨으로 마운트하는 기능이었는데, 내부적으로 사용하는 `git` 바이너리의 취약점을 통해 호스트에서 임의 명령 실행이 가능하다는 보안 위험이 확인되어 제거됐다.

기존에 `gitRepo` 볼륨을 사용 중인 워크로드는 다음 두 가지 대안 중 하나로 마이그레이션해야 한다.

```yaml
# 대안 1: init container를 통한 git clone
initContainers:
- name: git-clone
  image: alpine/git:latest
  command: ['git', 'clone', 'https://github.com/example/repo.git', '/workspace']
  volumeMounts:
  - name: workspace
    mountPath: /workspace

# 대안 2: OCI 이미지 볼륨 (위에서 소개한 신기능 활용)
volumes:
- name: app-source
  image:
    reference: registry.example.com/my-repo-snapshot:latest
```

**2. Ingress-NGINX 공식 지원 종료**

Kubernetes SIG Security 위원회가 2026년 3월 24일, Ingress-NGINX를 공식 지원 종료(retirement)했다. 이후 보안 패치나 업데이트가 더 이상 제공되지 않는다.

Ingress-NGINX는 Kubernetes 생태계에서 가장 널리 쓰이던 인그레스 컨트롤러 중 하나였던 만큼, 이번 지원 종료는 많은 팀에 영향을 준다. 마이그레이션 대상으로 Gateway API 기반 구현체들이 권장된다.

- **Envoy Gateway**: Kubernetes Gateway API를 네이티브로 구현한 고성능 옵션
- **Cilium Gateway API**: eBPF 기반으로 고성능 네트워킹과 보안을 결합
- **Contour**: Project Contour가 관리하는 Envoy 기반 인그레스/게이트웨이 컨트롤러

보안 업데이트가 중단됐다는 점에서, Ingress-NGINX를 운영 중인 팀은 이 마이그레이션을 가능한 빨리 시작해야 한다.

**3. Service externalIPs 필드 Deprecated**

Service spec의 `externalIPs` 필드가 v1.36부터 deprecated 처리됐다. 완전 제거는 v1.43에서 이루어질 예정이다. 대안으로는 `LoadBalancer` 타입 서비스 또는 Gateway API 사용이 권장된다.

### 업그레이드 전 점검 체크리스트

Cloudsmith와 PerfectScale 블로그는 v1.36으로 업그레이드하기 전 다음 항목을 점검하라고 권고했다.

1. `gitRepo` 볼륨 타입 사용 여부 확인 → init container 또는 OCI 볼륨 방식으로 마이그레이션
2. Ingress-NGINX 사용 중인 경우 → Gateway API 기반 대체 컨트롤러로 이전 계획 수립
3. Service 리소스의 `externalIPs` 필드 사용 여부 확인 → LoadBalancer 또는 Gateway API로 대안 검토
4. User Namespaces 기능 활용을 원한다면 커널 버전 및 containerd/CRI-O 버전 호환성 사전 확인
5. SELinux 활성화 노드에서 Pod 시작 성능 이슈를 겪고 있었다면, 이번 업그레이드 후 개선 여부 모니터링

```bash
# gitRepo 볼륨 사용 중인 Pod 확인
kubectl get pods --all-namespaces -o json | \
  jq '.items[] | select(.spec.volumes[]?.gitRepo != null) | .metadata.name'

# externalIPs 사용 중인 Service 확인
kubectl get svc --all-namespaces -o json | \
  jq '.items[] | select(.spec.externalIPs != null and (.spec.externalIPs | length > 0)) | .metadata.name'
```

### 커뮤니티 반응

Hacker News와 Kubernetes 공식 슬랙 커뮤니티에서는 이번 릴리스를 두고 "조용하지만 실용적인 업데이트"라는 평가가 이어졌다. 특히 HPA Scale-to-Zero의 안정화를 두고 "KEDA와 함께 쓰면 드디어 서버리스 수준의 비용 효율을 Kubernetes 위에서 달성할 수 있다"는 기대감이 개발자들 사이에서 표현됐다.

반면 Ingress-NGINX 지원 종료에 대해서는 우려의 목소리도 컸다. 커뮤니티의 많은 레거시 클러스터가 Ingress-NGINX에 의존하고 있어 마이그레이션 부담이 상당하다는 점, 그리고 Gateway API 기반 대안들이 Ingress-NGINX만큼 성숙하지 않다는 점이 주요 우려 사항으로 언급됐다.

## 정리

Kubernetes v1.36은 오랜 약속들을 드디어 이행한 릴리스다. HPA Scale-to-Zero, User Namespaces, OCI 볼륨, SELinux 마운트 최적화 — 네 가지 모두 수년간 Alpha 또는 Beta에 머물다 이번에 Stable로 졸업했다. 프로덕션 클러스터 운영자 입장에서는 이제 서드파티 의존 없이 네이티브 Kubernetes API만으로 더 많은 것을 할 수 있게 됐다.

한편, `gitRepo` 볼륨 제거와 Ingress-NGINX 지원 종료는 즉각적인 마이그레이션이 필요한 항목이다. 특히 Ingress-NGINX를 기반으로 운영 중인 팀이라면 보안 업데이트가 중단됐다는 사실을 심각하게 받아들이고 Gateway API로의 이전을 서둘러야 한다. 업그레이드가 계획 중이라면 위의 체크리스트를 기준으로 사전 점검부터 시작하는 걸 권한다.

## Reference

- [Kubernetes v1.36 Sneak Peek - kubernetes.io](https://kubernetes.io/blog/2026/03/30/kubernetes-v1-36-sneak-peek/)
- [Kubernetes v1.36 Release Highlights Discussion - kubernetes/sig-release GitHub](https://github.com/kubernetes/sig-release/discussions/2958)
- [Kubernetes 1.36 Release: New Features, Beta & Stable Changes - PerfectScale](https://www.perfectscale.io/blog/kubernetes-v1-36-sneak-peek)
- [Kubernetes 1.36 – What you need to know - Cloudsmith](https://cloudsmith.com/blog/kubernetes-1-36-what-you-need-to-know)
- [Kubernetes 1.36 Scale-to-Zero: Cut Your K8s Bill by 70% With One Config Change - DEV Community](https://dev.to/benriemer/kubernetes-136-scale-to-zero-cut-your-k8s-bill-by-70-with-one-config-change-45b6)
- [Complete Guide to Kubernetes 1.36 - DEV Community](https://dev.to/x4nent/complete-guide-to-kubernetes-136-dra-ga-oci-volumesource-mutatingadmissionpolicy-and-2h8b)
- [Kubernetes 1.36: 7 Features That Will Change How You Deploy - Medium](https://medium.com/@rameshavutu/kubernetes-1-36-d9ece5b727e8)
- [What to Expect From Kubernetes 1.36 - Cloud Native Now](https://cloudnativenow.com/features/what-to-expect-from-kubernetes-1-36/)
