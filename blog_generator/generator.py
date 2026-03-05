from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from importlib import metadata
from pathlib import Path

from .config import LLMSettings
from .prompt_template import build_system_prompt, build_user_prompt

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

FRONT_MATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r"^title:\s*['\"]?(.*?)['\"]?\s*$", re.MULTILINE)
DATE_RE = re.compile(r"^date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s+.*$", re.MULTILINE)
DATE_LINE_RE = re.compile(r"^date:\s*.*$", re.MULTILINE)


@dataclass
class SaveResult:
    path: Path
    warnings: list[str]


class BlogPostGenerator:
    def __init__(self, settings: LLMSettings, project_root: Path | None = None) -> None:
        self.settings = settings
        self.project_root = project_root or Path(__file__).resolve().parent.parent
        self.posts_dir = self.project_root / "_posts"

    def generate(self, keywords: str, category: str, tags: list[str]) -> str:
        provider = self.settings.normalized_provider()
        model = self.settings.normalized_model()
        api_key = self.settings.api_key.strip()
        if not api_key:
            raise ValueError("API 키가 비어 있습니다. /settings에서 설정해 주세요.")

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(keywords, category, tags)

        if provider == "OPENAI":
            content = self._generate_openai(model, api_key, system_prompt, user_prompt)
            return self._ensure_today_date(self._normalize_generated_markdown(content))
        if provider == "GEMINI":
            content = self._generate_gemini(model, api_key, system_prompt, user_prompt)
            return self._ensure_today_date(self._normalize_generated_markdown(content))
        raise ValueError(f"지원하지 않는 provider입니다: {provider}")

    def _generate_openai(self, model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
        if OpenAI is None:
            raise RuntimeError("openai 패키지가 설치되지 않았습니다.")
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = getattr(response, "output_text", "").strip()
        if not text:
            raise RuntimeError("OpenAI 응답에서 본문 텍스트를 가져오지 못했습니다.")
        return text

    def _generate_gemini(self, model: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
        if genai is None:
            raise RuntimeError("google-generativeai 패키지가 설치되지 않았습니다.")
        if not hasattr(genai, "GenerativeModel"):
            try:
                version = metadata.version("google-generativeai")
            except metadata.PackageNotFoundError:
                version = "unknown"
            raise RuntimeError(
                "현재 설치된 google-generativeai 버전이 Gemini 모델 API를 지원하지 않습니다. "
                f"(detected: {version}) "
                "Python 3.10+ 가상환경에서 google-generativeai를 업데이트하거나, "
                "Settings에서 Provider를 OPENAI로 변경해 주세요."
            )
        genai.configure(api_key=api_key)
        llm = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)
        response = llm.generate_content(user_prompt)
        text = getattr(response, "text", "")
        if not text:
            raise RuntimeError("Gemini 응답에서 본문 텍스트를 가져오지 못했습니다.")
        return text.strip()

    def validate(self, content: str, filename_date: str | None = None) -> list[str]:
        content = self._ensure_today_date(self._normalize_generated_markdown(content))
        errors: list[str] = []

        front_matter_match = FRONT_MATTER_RE.search(content)
        if not front_matter_match:
            return ["Front Matter가 없습니다."]
        front_matter = front_matter_match.group(1)

        for field in ["title", "date", "categories", "tag"]:
            if re.search(rf"^{field}:\s*.+$", front_matter, re.MULTILINE) is None:
                errors.append(f"Front Matter 필드 누락: {field}")

        if filename_date:
            date_match = DATE_RE.search(front_matter)
            if not date_match:
                errors.append("date 형식 검증 실패")
            elif date_match.group(1) != filename_date:
                errors.append(f"date({date_match.group(1)})와 파일명 날짜({filename_date})가 다릅니다.")

        for section in ["## 서론", "## 본론", "## 정리", "## Reference"]:
            if section not in content:
                errors.append(f"필수 섹션 누락: {section}")

        return errors

    def save(self, content: str, title_slug: str | None = None) -> SaveResult:
        content = self._ensure_today_date(self._normalize_generated_markdown(content))
        today = self._kst_now().strftime("%Y-%m-%d")
        errors = self.validate(content, filename_date=today)
        if errors:
            raise ValueError("\n".join(errors))

        slug = self._slugify(title_slug or self._extract_title(content))
        filename = f"{today}-{slug}.md"
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.posts_dir / filename
        out_path.write_text(content, encoding="utf-8")
        return SaveResult(path=out_path, warnings=[])

    def _extract_title(self, content: str) -> str:
        content = self._ensure_today_date(self._normalize_generated_markdown(content))
        front_matter_match = FRONT_MATTER_RE.search(content)
        if not front_matter_match:
            return "generated-post"
        title_match = TITLE_RE.search(front_matter_match.group(1))
        if not title_match:
            return "generated-post"
        return title_match.group(1).strip() or "generated-post"

    def _slugify(self, text: str) -> str:
        slug = text.strip().lower()
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"[\\/:*?\"<>|]+", "", slug)
        slug = re.sub(r"-{2,}", "-", slug).strip("-")
        return slug or "generated-post"

    def _normalize_generated_markdown(self, content: str) -> str:
        normalized = (content or "").replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").strip()
        fenced_match = re.match(r"^```(?:markdown|md)?\s*\n([\s\S]*?)\n```$", normalized, re.IGNORECASE)
        if fenced_match:
            normalized = fenced_match.group(1).strip()
        return normalized

    def _ensure_today_date(self, content: str) -> str:
        front_matter_match = FRONT_MATTER_RE.search(content)
        if not front_matter_match:
            return content
        front_matter = front_matter_match.group(1)
        today_line = f"date: {self._kst_now().strftime('%Y-%m-%d %H:%M:%S +09:00')}"
        if DATE_LINE_RE.search(front_matter):
            front_matter = DATE_LINE_RE.sub(today_line, front_matter)
        else:
            front_matter = f"{front_matter}\n{today_line}"
        return f"---\n{front_matter}\n---\n{content[front_matter_match.end():].lstrip()}"

    def _kst_now(self) -> datetime:
        return datetime.now(timezone(timedelta(hours=9)))
