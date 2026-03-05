from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / "settings.json"

DEFAULT_PROVIDER = "GEMINI"
DEFAULT_MODEL_BY_PROVIDER = {
    "GEMINI": "gemini-2.0-flash",
    "OPENAI": "gpt-4o-mini",
}

DEFAULT_CATEGORY_TAGS = {
    "Tip": ["Blog"],
    "Error": ["Troubleshooting"],
    "BE": ["Backend"],
    "CS": ["ComputerScience"],
}


@dataclass
class LLMSettings:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL_BY_PROVIDER[DEFAULT_PROVIDER]
    api_key: str = ""

    def normalized_provider(self) -> str:
        return (self.provider or DEFAULT_PROVIDER).strip().upper()

    def normalized_model(self) -> str:
        provider = self.normalized_provider()
        model = (self.model or "").strip()
        if model:
            return model
        return DEFAULT_MODEL_BY_PROVIDER.get(provider, DEFAULT_MODEL_BY_PROVIDER[DEFAULT_PROVIDER])


def _coerce_settings(raw: dict) -> LLMSettings:
    provider = str(raw.get("provider", DEFAULT_PROVIDER)).strip().upper() or DEFAULT_PROVIDER
    model = str(raw.get("model", "")).strip() or DEFAULT_MODEL_BY_PROVIDER.get(provider, DEFAULT_MODEL_BY_PROVIDER[DEFAULT_PROVIDER])
    api_key = str(raw.get("api_key", "")).strip()
    return LLMSettings(provider=provider, model=model, api_key=api_key)


def load_settings(path: Path = SETTINGS_PATH) -> LLMSettings:
    if not path.exists():
        return LLMSettings()
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        return LLMSettings()
    return _coerce_settings(raw)


def save_settings(settings: LLMSettings, path: Path = SETTINGS_PATH) -> None:
    data = asdict(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_tags(tags_raw: str | None, category: str | None = None) -> list[str]:
    if tags_raw:
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
        if tags:
            return tags
    if category and category in DEFAULT_CATEGORY_TAGS:
        return DEFAULT_CATEGORY_TAGS[category]
    return ["Blog"]
