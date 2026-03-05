from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from blog_generator.config import (  # noqa: E402
    DEFAULT_CATEGORY_TAGS,
    LLMSettings,
    load_settings,
    parse_tags,
    save_settings,
)
from blog_generator.generator import BlogPostGenerator  # noqa: E402

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
app.secret_key = "dev-secret-change-me"
TITLE_RE = re.compile(r"^title:\s*['\"]?(.*?)['\"]?\s*$", re.MULTILINE)


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _commit_and_push_post(post_path: Path, commit_message: str) -> str:
    rel_post_path = post_path.relative_to(PROJECT_ROOT).as_posix()

    add_result = _run_git(["add", "--", rel_post_path])
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git add failed")

    commit_result = _run_git(["commit", "-m", commit_message, "--", rel_post_path])
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or commit_result.stdout.strip() or "git commit failed")

    branch_result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if branch_result.returncode != 0:
        raise RuntimeError(branch_result.stderr.strip() or "git rev-parse failed")
    branch = (branch_result.stdout or "").strip()
    if not branch:
        raise RuntimeError("current branch is empty")

    push_result = _run_git(["push", "origin", branch])
    if push_result.returncode != 0:
        raise RuntimeError(push_result.stderr.strip() or push_result.stdout.strip() or "git push failed")

    return branch


def _build_commit_message(content: str, category: str, keywords: str, post_path: Path) -> str:
    title_match = TITLE_RE.search(content or "")
    if title_match and title_match.group(1).strip():
        return f"Add post: {title_match.group(1).strip()}"

    topic = (keywords or "").strip()
    if not topic:
        stem = post_path.stem
        if re.match(r"^\d{4}-\d{2}-\d{2}-", stem):
            topic = stem[11:].replace("-", " ").strip()
        else:
            topic = stem.replace("-", " ").strip()

    category_text = (category or "").strip()
    if category_text:
        return f"Add {category_text} post: {topic or 'new article'}"
    return f"Add post: {topic or 'new article'}"


@app.get("/")
def index():
    return render_template(
        "index.html",
        categories=sorted(DEFAULT_CATEGORY_TAGS.keys()),
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    current = load_settings()
    if request.method == "POST":
        provider = (request.form.get("provider") or "GEMINI").strip().upper()
        model = (request.form.get("model") or "").strip()
        api_key = (request.form.get("api_key") or "").strip()
        new_settings = LLMSettings(provider=provider, model=model, api_key=api_key)
        save_settings(new_settings)
        flash("LLM 설정이 저장되었습니다.", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", settings=current)


@app.post("/generate")
def generate():
    keywords = (request.form.get("keywords") or "").strip()
    category = (request.form.get("category") or "Tip").strip()
    tags_raw = (request.form.get("tags") or "").strip()
    tags = parse_tags(tags_raw, category=category)

    if not keywords:
        flash("키워드를 입력해 주세요.", "error")
        return redirect(url_for("index"))

    generator = BlogPostGenerator(load_settings(), project_root=PROJECT_ROOT)
    try:
        content = generator.generate(keywords=keywords, category=category, tags=tags)
    except Exception as e:
        flash(f"생성 실패: {e}", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        content=content,
        keywords=keywords,
        category=category,
        tags=", ".join(tags),
    )


@app.post("/save")
def save():
    content = request.form.get("content") or ""
    title_slug = (request.form.get("title_slug") or "").strip()
    if not content.strip():
        flash("저장할 본문이 비어 있습니다.", "error")
        return redirect(url_for("index"))

    generator = BlogPostGenerator(load_settings(), project_root=PROJECT_ROOT)
    try:
        result = generator.save(content=content, title_slug=title_slug or None)
    except Exception as e:
        flash(f"저장 실패: {e}", "error")
        return render_template(
            "result.html",
            content=content,
            keywords=request.form.get("keywords", ""),
            category=request.form.get("category", ""),
            tags=request.form.get("tags", ""),
        )

    commit_message = _build_commit_message(
        content=content,
        category=request.form.get("category", ""),
        keywords=request.form.get("keywords", ""),
        post_path=result.path,
    )
    try:
        branch = _commit_and_push_post(post_path=result.path, commit_message=commit_message)
    except Exception as e:
        flash(f"저장은 완료되었지만 Git 커밋/푸시 실패: {e}", "error")
        return render_template(
            "result.html",
            content=content,
            keywords=request.form.get("keywords", ""),
            category=request.form.get("category", ""),
            tags=request.form.get("tags", ""),
        )

    flash(f"저장/커밋/푸시 완료: {result.path.name} (branch: {branch}, message: {commit_message})", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
