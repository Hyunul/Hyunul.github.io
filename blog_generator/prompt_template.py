from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMAT_GUIDE_PATH = PROJECT_ROOT / "2026-03-05-Blog_Post_Format_Guide.md"


def load_format_guide() -> str:
    if not FORMAT_GUIDE_PATH.exists():
        return ""
    return FORMAT_GUIDE_PATH.read_text(encoding="utf-8")


def build_system_prompt() -> str:
    guide = load_format_guide()
    return (
        "You are an expert technical blog writer for a Jekyll blog.\n"
        "Always output clean markdown in Korean and follow the required structure strictly.\n"
        "Required output structure:\n"
        "1) YAML Front Matter with keys: title, date, categories, tag\n"
        "2) Body sections: ## 서론, ## 본론, ## 정리, ## Reference\n"
        "3) date must include timezone +09:00\n"
        "4) tag key must be singular 'tag', not 'tags'\n\n"
        "Project formatting guide:\n"
        f"{guide}"
    )


def build_user_prompt(keywords: str, category: str, tags: list[str]) -> str:
    tags_text = ", ".join(tags)
    return (
        "다음 입력값으로 Jekyll 블로그 포스트를 작성해줘.\n"
        f"- 키워드: {keywords}\n"
        f"- 카테고리: {category}\n"
        f"- 태그: {tags_text}\n\n"
        "요구사항:\n"
        "- 실무 관점에서 이해 가능한 설명을 작성할 것\n"
        "- 필요시 코드 블록은 언어를 명시할 것\n"
        "- 마지막 Reference에는 최소 1개의 링크를 포함할 것\n"
        "- Front Matter와 본문 외의 설명 문장은 추가하지 말 것"
    )
