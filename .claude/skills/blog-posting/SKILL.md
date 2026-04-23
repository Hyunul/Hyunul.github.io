---
name: blog-posting
description: Use when creating a new Jekyll post for the hyunul.github.io blog (user asks to "포스팅", "포스트 작성", "블로그 글 써", "write a post about X"), generating content from a topic/keyword, or migrating drafts into _posts/. Enforces the project's strict Front Matter contract and required section layout.
---

# Blog Posting (hyunul.github.io)

## Overview

This repo is a Jekyll blog (Chirpy theme) with a strict post format enforced by `blog_generator/generator.py:validate`. Any new post must satisfy the filename, Front Matter, and required-section contract — otherwise it fails validation in the LLM generator and renders incorrectly on the published site.

**Core principle:** The format guide at `2026-03-05-Blog_Post_Format_Guide.md`, the system prompt in `blog_generator/prompt_template.py`, and `BlogPostGenerator.validate` are **coupled**. When you write a post by hand, you must follow the same contract they enforce.

## When to Use

- User asks to write a new blog post on a topic (e.g. "X에 대한 포스팅 진행해", "블로그 글 하나 써줘")
- User asks to migrate/rewrite an existing draft into `_posts/`
- User asks you to generate multiple related posts in a batch
- You are adding Reference/Changelog-style notes that should live as a post

**Do NOT use for:**
- Editing Jekyll config or theme files (`_config.yml`, `_layouts/`, `_includes/`)
- Updating the format guide itself — that's a coupled change; update generator + prompt + this skill together
- Drafts outside `_posts/` (those don't render)

## Filename Rules

```
_posts/YYYY-MM-DD-<slug>.md
```

- **Date** = today in KST (Asia/Seoul). Never use a past date — the generator rewrites `date` to "now KST"; do the same by hand.
- **Slug** may contain Korean, brackets, hyphens. Convention in this repo: `[카테고리]-핵심-주제-키워드` — all-lowercase, hyphen-separated, Korean allowed.
- Existing examples:
  - `_posts/2026-04-23-[security]-lovable-bola-취약점-프로젝트-데이터-48일-노출.md`
  - `_posts/2025-04-17-[spring]-로그는-왜-남기나요.md`

## Front Matter Contract

```yaml
---
title: "[카테고리] 글 제목"
date: YYYY-MM-DD HH:MM:SS +09:00
categories: [단일카테고리]
tag: [태그1, 태그2, 태그3]
---
```

Invariants (checked by `BlogPostGenerator.validate`):

| Field | Rule |
| --- | --- |
| `title` | Must include a bracket prefix like `[Spring]`, `[BE]`, `[Error]`, `[Blog]`, `[AI]`, `[security]` |
| `date` | Must include `+09:00` offset; date portion **must match filename date** |
| `categories` | YAML list, typically exactly 1 item — pick from `BE`, `Tip`, `Error`, `CS`, `AI`, `security`, `network`, `deployment` |
| `tag` | **Singular key `tag`, not `tags`.** YAML list. 3–6 specific tags. |

**Common mistake — the `tag` vs `tags` trap.** Chirpy's default is `tags`, but this blog overrides it to `tag`. Writing `tags:` silently drops all tags on render.

## Required Body Sections

Exactly these four H2 headings, in this order:

```markdown
## 서론

배경과 문제 상황. 왜 이 글을 쓰게 됐는가.

## 본론

핵심 개념 → 동작 원리 → 예시 코드/설정 → 주의점.
필요시 `###` 하위 섹션으로 나눈다.

## 정리

핵심만 bullet로 요약. 실무 적용 포인트.

## Reference

- [제목](https://...)
- [제목](https://...)
```

`BlogPostGenerator.validate` rejects a post missing any of `## 서론`, `## 본론`, `## 정리`, `## Reference`. Don't rename them, don't translate them.

## Style Conventions (observed across existing posts)

- **Tone:** 친근한 해설투, "~했다", "~이다" 기본. 설교조 회피.
- **Code blocks** must specify language: ` ```java `, ` ```yaml `, ` ```bash `, ` ```text ` 등.
- **Inline emphasis:** 핵심 키워드는 백틱, 중요 개념은 `**굵게**`. 이모지는 쓰지 않는다.
- **Tables** for comparison / quick reference.
- **Images** live under `assets/images/<slug>/` and are embedded with `<img>` tags (not Markdown `![]()`).
- **Length:** 대부분 1,500–3,500 단어. 보안/신규 CVE/릴리스 노트는 짧아도 됨. 튜토리얼성 글은 길게.
- **References:** 공식 문서 + 신뢰도 높은 1·2차 자료 위주. 3–6개 권장.

## Workflow

1. **Pick the category prefix** from the title. Look at the filenames of the last ~10 posts (`ls _posts/ | tail`) to match tone and naming.
2. **Resolve today's date in KST.** If unsure, use the `currentDate` value in the CLAUDE.md context block.
3. **Draft the Front Matter first** — title, date, categories, tag. Sanity-check the `tag` key spelling.
4. **Write the four required sections.** Don't skip any; an empty `## Reference` is better than a missing one, but aim for 3+ real citations.
5. **For factual/news posts**, verify key claims (dates, version numbers, CVE IDs) via WebSearch / Context7 before writing. Hallucinated version numbers are the #1 defect source in this blog.
6. **Write the file** at `_posts/YYYY-MM-DD-<slug>.md`. Do NOT commit/push unless explicitly asked — the Flask app does that via `/save`, and the user often reviews before pushing.
7. **Self-check** against the checklist below.

## Pre-Save Checklist

- [ ] Filename date == Front Matter `date` date
- [ ] `+09:00` offset present
- [ ] `tag:` (singular), not `tags:`
- [ ] Title has a `[bracket]` prefix
- [ ] All four required H2 sections present in order
- [ ] Code blocks have language tags
- [ ] No emoji unless user asked
- [ ] Reference section has real, clickable URLs

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Using `tags:` in Front Matter | Change to `tag:` — this blog overrides the Chirpy default |
| Past or future date to "look consistent" | Always today's KST date; the generator rewrites it anyway |
| Missing `## Reference` section | Add it even if empty — validator rejects otherwise |
| Translating section names (e.g. `## Intro`) | Must be Korean: `서론 / 본론 / 정리 / Reference` (last one stays English) |
| Markdown image syntax `![]()` | Convention here is `<img src="./assets/images/<slug>/..." alt="...">` |
| Adding a 5th required section (e.g. `## 배경`) | Use `###` subsections under `## 본론` instead |
| Auto-committing and pushing without asking | Only the Flask `/save` route should git-push; when writing by hand, stop at the file write |

## Quick Reference: Bracket Prefixes → Categories

| Prefix | Category | Example topics |
| --- | --- | --- |
| `[Spring]`, `[BE]` | `BE` | 스프링, JPA, 트랜잭션, 백엔드 아키텍처 |
| `[AI]` | `AI` | LLM, Claude, 에이전트, 프롬프트 |
| `[security]` | `security` | CVE, 취약점, 인증/인가 설계 |
| `[network]` | `network` | HTTP, CORS, 프록시 |
| `[deployment]` | `deployment` | Docker, K8s, CI/CD |
| `[Error]`, `[trouble-shooting]` | `Error` | 장애 회고, 디버깅 기록 |
| `[Blog]`, `[Tip]` | `Tip` | 블로그 메타, 일반 팁 |
| `[CS]` | `CS` | 자료구조, 알고리즘, OS |

## Template (copy-paste starting point)

```markdown
---
title: "[카테고리] 한 줄 제목"
date: 2026-04-23 15:00:00 +09:00
categories: [BE]
tag: [키워드1, 키워드2, 키워드3]
---

## 서론

왜 이 글을 쓰는가. 어떤 문제/배경에서 출발했는가. (2–4문단)

## 본론

### 소제목 1

핵심 개념과 동작 원리.

​```java
// 예시 코드
​```

### 소제목 2

주의할 점, 오해하기 쉬운 부분.

## 정리

- 핵심 요점 1
- 핵심 요점 2
- 실무 적용 시 주의할 점

## Reference

- [공식 문서](https://example.com)
- [관련 블로그/논문](https://example.com)
```

## Related

- Format guide source of truth: `2026-03-05-Blog_Post_Format_Guide.md`
- Validator: `blog_generator/generator.py` → `BlogPostGenerator.validate`
- LLM system prompt: `blog_generator/prompt_template.py`
- Flask save flow: `web/app.py` → `_commit_and_push_post`
