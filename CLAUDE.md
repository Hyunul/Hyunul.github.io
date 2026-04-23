# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Hybrid repository that combines:

1. **A Jekyll blog** (`hyunul.github.io`) built on the [Chirpy theme](https://github.com/cotes2020/jekyll-theme-chirpy), deployed to GitHub Pages via `.github/workflows/pages-deploy.yml`.
2. **An LLM-powered blog post generator** — a Flask web app (`web/`) plus a Python package (`blog_generator/`) that calls Gemini or OpenAI to generate new Jekyll posts, save them to `_posts/`, and auto-commit + push.
3. **A Tistory → Jekyll crawler** (`blog_generator/tistory_crawler.py`) that migrates posts from `https://hyunul.tistory.com/`.

## Commands

### Jekyll site (Ruby)

```bash
bundle install           # install theme + html-proofer
bundle exec jekyll s     # local dev server (default: http://127.0.0.1:4000)
bundle exec jekyll b     # production build -> _site/
bundle exec htmlproofer _site --disable-external   # same check as CI
```

CI builds with Ruby 3.3. `JEKYLL_ENV=production` is required for production-only compression (`_config.yml` `compress_html` ignores `development`).

### Blog generator (Python / Flask)

```bash
pip install -r requirements.txt
python web/app.py        # Flask dev server on http://127.0.0.1:5000
```

Flow: `/` enter keywords → `/generate` calls the configured LLM → preview page → `/save` writes `_posts/YYYY-MM-DD-<slug>.md`, then `git add/commit/push` on the current branch (see `web/app.py:_commit_and_push_post`). LLM provider + API key are configured at `/settings` and persisted to `settings.json` (gitignored).

### Tistory crawler

```bash
python -m blog_generator.tistory_crawler --dry-run                  # preview
python -m blog_generator.tistory_crawler --start 1 --end 78         # full crawl
python -m blog_generator.tistory_crawler --download-images          # also fetch images
```

Writes to `_posts/` and skips titles that already exist (see `load_existing_titles`).

## Architecture

### Blog posting workflow

When a task involves creating, generating, or migrating a post into `_posts/` (including automated/routine posting runs like "자동 포스팅 N개"), invoke the **`blog-posting`** skill at `.claude/skills/blog-posting/SKILL.md` before writing the file. The skill encodes the Front Matter contract, required section order, filename rules, and category/tag conventions that must be satisfied for `BlogPostGenerator.validate` to accept the post. Do not draft posts from memory — the `tag` (singular) vs `tags` (plural) trap and the required `## 서론 / ## 본론 / ## 정리 / ## Reference` layout are the most common defect sources.

### Post authoring contract (strictly enforced)

Both the LLM generator and the Tistory crawler produce posts that must conform to the rules documented in [2026-03-05-Blog_Post_Format_Guide.md](2026-03-05-Blog_Post_Format_Guide.md). Key invariants that `BlogPostGenerator.validate` checks (`blog_generator/generator.py`):

- Filename: `_posts/YYYY-MM-DD-<slug>.md`
- Front Matter: `title`, `date` (with `+09:00`), `categories`, `tag` — note the key is singular **`tag`**, not `tags`.
- Required body sections: `## 서론`, `## 본론`, `## 정리`, `## Reference`.
- `date` must match the filename date; the generator rewrites `date` to KST *now* before saving (`_ensure_today_date`).

If you change the required sections or Front Matter fields, update the guide, the system prompt (`blog_generator/prompt_template.py`), and `BlogPostGenerator.validate` together — they are coupled.

### Blog generator package (`blog_generator/`)

- `config.py` — `LLMSettings` dataclass, load/save to `settings.json`, default model per provider (`GEMINI` → `gemini-2.0-flash`, `OPENAI` → `gpt-4o-mini`), and `DEFAULT_CATEGORY_TAGS` used as fallback tags.
- `prompt_template.py` — loads the format guide and builds system + user prompts. The format guide file is the source of truth fed into the LLM.
- `generator.py` — `BlogPostGenerator.generate/validate/save`. Both Gemini and OpenAI code paths normalize the response (strip fenced ```markdown blocks, force today's KST date) before validation and write.
- `tistory_crawler.py` — standalone; does not depend on `LLMSettings`. Uses JSON-LD + `window.T.entryInfo` + meta-tag fallbacks to extract metadata, `markdownify` for HTML→MD conversion, and maps Tistory categories to Jekyll categories via `CATEGORY_MAP`.

### Web app (`web/`)

Thin Flask wrapper. `app.py` also executes Git: on `/save` it `git add` the new post, `git commit` with a message derived from the Front Matter title, and `git push` to the current branch. Any change to the save flow must keep this three-step sequence correct — a failed push still leaves the file written and committed locally.

### Jekyll specifics

- `_plugins/posts-lastmod-hook.rb` sets `last_modified_at` from `git log` — GitHub Actions must check out with `fetch-depth: 0` (already configured).
- `_config.yml` `exclude` omits `web/` from the Jekyll build, so the Flask app does not bleed into the published site.
- `permalink` for posts is `/posts/:title/`. Don't change without updating internal links.
- Comments use Giscus (`hyunul/hyunul.github.io`, category `General`).

## Conventions observed in existing posts

- Titles use bracket prefixes: `[spring]`, `[trouble-shooting]`, `[ai]`, `[security]`, `[Blog]`, `[Error]`, etc.
- Filenames may contain Korean characters and brackets (e.g. `2025-04-17-[spring]-로그는-왜-남기나요.md`). This is expected — the slugifier deliberately preserves non-ASCII.
- Images live under `assets/images/<slug>/` and are referenced via `<img>` tags rather than Markdown image syntax.
