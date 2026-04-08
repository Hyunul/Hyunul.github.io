"""Tistory 블로그 크롤러 - Jekyll 포스트 변환기"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE_URL = "https://hyunul.tistory.com/{post_id}"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# Tistory 카테고리 → Jekyll 카테고리 매핑
CATEGORY_MAP: dict[str, str] = {
    "개발": "BE",
    "트러블 슈팅": "Error",
    "취준": "Career",
    "CS": "CS",
    "일상": "Life",
    "알고리즘": "CS",
}

# 카테고리별 기본 태그 (포스트에 태그가 없을 때, 제목에서 추출 시도 후 fallback)
CATEGORY_TAGS: dict[str, list[str]] = {
    "BE": ["Backend"],
    "Error": ["Troubleshooting"],
    "CS": ["ComputerScience"],
    "Career": ["Career"],
    "Life": ["Life"],
    "알고리즘": ["Algorithm"],
}

# 제목 대괄호 접두사 → 태그 매핑 (제목에서 태그 추출)
TITLE_PREFIX_TAGS: dict[str, list[str]] = {
    "spring": ["Spring", "Backend"],
    "trouble shooting": ["Troubleshooting"],
    "pinpoint": ["Pinpoint", "Monitoring"],
    "성능 테스트": ["Performance", "Testing"],
    "algorithm": ["Algorithm"],
}


@dataclass
class TistoryPost:
    post_id: int
    title: str
    date_published: str
    category: str
    tags: list[str] = field(default_factory=list)
    html_content: str = ""


@dataclass
class CrawlStats:
    crawled: int = 0
    skipped_404: int = 0
    skipped_duplicate: int = 0
    saved: int = 0
    errors: int = 0


def fetch_post(post_id: int) -> TistoryPost | None:
    """포스트 페이지를 가져와 메타데이터와 본문을 추출"""
    url = BASE_URL.format(post_id=post_id)
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [오류] 포스트 {post_id} 요청 실패: {e}")
        return None

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # 메타데이터 추출
    title = _extract_title(soup)
    date_published = _extract_date(soup, resp.text)
    category = _extract_category(soup, resp.text)
    tags = _extract_tags(soup)

    if not title:
        print(f"  [경고] 포스트 {post_id}: 제목을 찾을 수 없음")
        return None

    # 본문 HTML 추출
    html_content = _extract_content_html(soup)

    return TistoryPost(
        post_id=post_id,
        title=title,
        date_published=date_published,
        category=category,
        tags=tags,
        html_content=html_content,
    )


def _extract_title(soup: BeautifulSoup) -> str:
    """JSON-LD 또는 og:title에서 제목 추출"""
    # JSON-LD에서 추출
    ld_json = _parse_json_ld(soup)
    if ld_json and "headline" in ld_json:
        return ld_json["headline"].strip()

    # og:title 메타태그
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    # <title> 태그 fallback
    title_tag = soup.find("title")
    if title_tag:
        # Tistory 제목에서 블로그 이름 제거
        raw = title_tag.get_text().strip()
        return raw.split(" :: ")[0].strip() if " :: " in raw else raw

    return ""


def _extract_date(soup: BeautifulSoup, page_text: str) -> str:
    """날짜 추출 (ISO 8601 형식 반환)"""
    # JSON-LD에서 datePublished
    ld_json = _parse_json_ld(soup)
    if ld_json and "datePublished" in ld_json:
        return ld_json["datePublished"]

    # window.T.entryInfo에서 추출
    entry_info = _parse_entry_info(page_text)
    if entry_info and "publishedTime" in entry_info:
        return entry_info["publishedTime"]

    # meta 태그 fallback
    date_meta = soup.find("meta", property="article:published_time")
    if date_meta and date_meta.get("content"):
        return date_meta["content"]

    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")


def _extract_category(soup: BeautifulSoup, page_text: str) -> str:
    """카테고리 추출"""
    # window.T.entryInfo에서 categoryLabel
    entry_info = _parse_entry_info(page_text)
    if entry_info and entry_info.get("categoryLabel"):
        return entry_info["categoryLabel"]

    # 카테고리 링크에서 추출
    cat_link = soup.find("a", href=re.compile(r"/category/"))
    if cat_link:
        return cat_link.get_text().strip()

    return ""


def _extract_tags(soup: BeautifulSoup) -> list[str]:
    """포스트 전용 태그 추출 (사이트 전체 태그 제외)"""
    tags = []

    # Tistory 포스트 태그 영역: 본문 하단의 태그 링크들
    # /tag/ 경로를 포함하는 링크 중, 본문 영역 근처에 있는 것만 수집
    # 사이드바의 태그 클라우드와 구분하기 위해 article 또는 본문 컨테이너 내에서만 탐색
    article = soup.find("article") or soup.find("div", class_="entry-content")
    if article:
        for a_tag in article.find_all("a", href=re.compile(r"/tag/")):
            tag_text = a_tag.get_text().strip()
            if tag_text and tag_text != "태그":
                tags.append(tag_text)

    # 본문 영역에서 못 찾으면, post-tag 또는 article-tag 클래스 탐색
    if not tags:
        for cls in ["post-tag", "article-tag", "tagTrail"]:
            tag_area = soup.find("div", class_=cls)
            if tag_area:
                for a_tag in tag_area.find_all("a"):
                    tag_text = a_tag.get_text().strip()
                    if tag_text and tag_text != "태그":
                        tags.append(tag_text)
                if tags:
                    break

    return tags


def _extract_content_html(soup: BeautifulSoup) -> str:
    """본문 HTML 추출"""
    # Tistory 본문 셀렉터 (우선순위 순)
    selectors = [
        ("div", {"class": "tt_article_userfont"}),
        ("div", {"class": "contents_style"}),
        ("div", {"class": "entry-content"}),
        ("div", {"class": "article_view"}),
        ("article", {}),
    ]
    for tag_name, attrs in selectors:
        el = soup.find(tag_name, attrs)
        if el:
            return str(el)

    return ""


def _parse_json_ld(soup: BeautifulSoup) -> dict | None:
    """JSON-LD 스키마 파싱"""
    script = soup.find("script", type="application/ld+json")
    if not script or not script.string:
        return None
    try:
        data = json.loads(script.string)
        # @graph 배열인 경우
        if isinstance(data, dict) and "@graph" in data:
            for item in data["@graph"]:
                if item.get("@type") == "BlogPosting":
                    return item
        if isinstance(data, dict) and data.get("@type") == "BlogPosting":
            return data
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def _parse_entry_info(page_text: str) -> dict | None:
    """window.T.entryInfo 파싱"""
    match = re.search(r"window\.T\.entryInfo\s*=\s*(\{.*?\});", page_text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except (json.JSONDecodeError, TypeError):
        return None


def convert_to_markdown(post: TistoryPost) -> str:
    """HTML 본문을 Markdown으로 변환"""
    if not post.html_content:
        return ""

    # markdownify로 변환
    markdown = md(
        post.html_content,
        heading_style="ATX",
        strip=["script", "style"],
        code_language="",
    )

    # 후처리
    # 과도한 빈 줄 정리 (3줄 이상 → 2줄)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    # 각 줄의 trailing whitespace 제거
    markdown = "\n".join(line.rstrip() for line in markdown.split("\n"))
    # 앞뒤 공백 정리
    markdown = markdown.strip()

    return markdown


def build_frontmatter(post: TistoryPost) -> str:
    """Jekyll 프론트매터 생성"""
    # 날짜 파싱
    date_str = _format_jekyll_date(post.date_published)

    # 카테고리 매핑
    mapped_category = CATEGORY_MAP.get(post.category, post.category or "Blog")

    # 제목 포맷 - 이미 대괄호 접두사가 있으면 유지
    title = post.title
    if not re.match(r"^\[.*?\]", title):
        title = f"[{mapped_category}] {title}"

    # 태그 결정: 포스트 태그 → 제목 접두사 기반 → 카테고리 기반 fallback
    tags = post.tags
    if not tags:
        # 제목 대괄호 접두사에서 태그 추출 시도
        prefix_match = re.match(r"^\[\s*(.+?)\s*\]", post.title)
        if prefix_match:
            prefix = prefix_match.group(1).lower().strip()
            tags = TITLE_PREFIX_TAGS.get(prefix, [])
        if not tags:
            tags = CATEGORY_TAGS.get(post.category, CATEGORY_TAGS.get(mapped_category, ["Blog"]))

    # 태그 포맷팅
    tags_str = ", ".join(tags)

    return (
        f"---\n"
        f'title: "{_escape_yaml_string(title)}"\n'
        f"date: {date_str}\n"
        f"categories: [{mapped_category}]\n"
        f"tag: [{tags_str}]\n"
        f"---\n"
    )


def _format_jekyll_date(iso_date: str) -> str:
    """ISO 8601 날짜를 Jekyll 형식으로 변환"""
    # 2025-12-15T13:05:20+09:00 → 2025-12-15 13:05:20 +09:00
    # 다양한 형식 지원
    iso_date = iso_date.strip()

    # ISO 8601 with T separator
    match = re.match(
        r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})([+-]\d{2}:\d{2})?", iso_date
    )
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        tz_part = match.group(3) or "+09:00"
        return f"{date_part} {time_part} {tz_part}"

    # 날짜만 있는 경우
    match = re.match(r"(\d{4}-\d{2}-\d{2})", iso_date)
    if match:
        return f"{match.group(1)} 00:00:00 +09:00"

    return f"{iso_date} +09:00"


def _escape_yaml_string(text: str) -> str:
    """YAML 문자열 이스케이프"""
    return text.replace('"', '\\"')


def generate_filename(post: TistoryPost) -> str:
    """Jekyll 포스트 파일명 생성"""
    # 날짜 추출
    match = re.match(r"(\d{4}-\d{2}-\d{2})", post.date_published)
    date_prefix = match.group(1) if match else datetime.now().strftime("%Y-%m-%d")

    # 슬러그 생성
    slug = _slugify(post.title)

    return f"{date_prefix}-{slug}.md"


def _slugify(text: str) -> str:
    """제목을 파일명용 슬러그로 변환"""
    slug = text.strip().lower()
    # 대괄호 접두사 유지 (예: [be] → [be])
    slug = re.sub(r"\s+", "-", slug)
    # 파일명에 부적합한 문자 제거 (한국어, 영문, 숫자, 하이픈, 대괄호는 유지)
    slug = re.sub(r'[\\/:*?"<>|]+', "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "untitled"


def load_existing_titles() -> set[str]:
    """기존 포스트 제목 목록 로드"""
    titles = set()
    if not POSTS_DIR.exists():
        return titles

    title_re = re.compile(r'^title:\s*["\']?(.*?)["\']?\s*$', re.MULTILINE)
    for f in POSTS_DIR.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            match = title_re.search(content[:500])
            if match:
                titles.add(match.group(1).strip().lower())
        except OSError:
            continue

    return titles


def download_images(post: TistoryPost, slug: str) -> dict[str, str]:
    """이미지 다운로드 및 URL 매핑 반환"""
    url_map: dict[str, str] = {}
    soup = BeautifulSoup(post.html_content, "html.parser")
    images = soup.find_all("img")
    if not images:
        return url_map

    img_dir = IMAGES_DIR / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    for idx, img in enumerate(images, 1):
        src = img.get("src") or img.get("data-src") or ""
        if not src or src.startswith("data:"):
            continue

        # 확장자 추출
        ext = Path(src.split("?")[0]).suffix or ".png"
        local_name = f"img_{idx:02d}{ext}"
        local_path = img_dir / local_name

        try:
            img_resp = requests.get(src, timeout=15)
            img_resp.raise_for_status()
            local_path.write_bytes(img_resp.content)
            rel_path = f"/assets/images/{slug}/{local_name}"
            url_map[src] = rel_path
        except requests.RequestException:
            continue

    return url_map


def crawl(
    start: int = 1,
    end: int = 78,
    dry_run: bool = False,
    dl_images: bool = False,
    delay: float = 1.0,
) -> CrawlStats:
    """메인 크롤링 로직"""
    stats = CrawlStats()
    existing_titles = load_existing_titles()

    print(f"크롤링 시작: 포스트 {start}~{end}")
    print(f"기존 포스트 수: {len(existing_titles)}개")
    print(f"모드: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 50)

    for post_id in range(start, end + 1):
        print(f"[{post_id}/{end}] ", end="", flush=True)

        post = fetch_post(post_id)
        if post is None:
            stats.skipped_404 += 1
            print("404 (건너뜀)")
            continue

        stats.crawled += 1

        # 중복 확인
        if post.title.strip().lower() in existing_titles:
            stats.skipped_duplicate += 1
            print(f"중복 건너뜀: {post.title}")
            continue

        # 변환
        markdown_content = convert_to_markdown(post)
        frontmatter = build_frontmatter(post)
        filename = generate_filename(post)

        # 이미지 다운로드
        if dl_images and not dry_run:
            slug = _slugify(post.title)
            url_map = download_images(post, slug)
            for orig, local in url_map.items():
                markdown_content = markdown_content.replace(orig, local)

        full_content = frontmatter + "\n" + markdown_content + "\n"

        if dry_run:
            print(f"[DRY] {filename} | {post.title} | {post.category}")
        else:
            out_path = POSTS_DIR / filename
            out_path.write_text(full_content, encoding="utf-8")
            stats.saved += 1
            print(f"저장: {filename}")

        # 요청 간 딜레이
        if post_id < end:
            time.sleep(delay)

    # 결과 요약
    print("\n" + "=" * 50)
    print("크롤링 완료!")
    print(f"  수집: {stats.crawled}개")
    print(f"  저장: {stats.saved}개")
    print(f"  404 건너뜀: {stats.skipped_404}개")
    print(f"  중복 건너뜀: {stats.skipped_duplicate}개")
    print(f"  오류: {stats.errors}개")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Tistory 블로그 크롤러")
    parser.add_argument("--start", type=int, default=1, help="시작 포스트 번호 (기본: 1)")
    parser.add_argument("--end", type=int, default=78, help="종료 포스트 번호 (기본: 78)")
    parser.add_argument("--dry-run", action="store_true", help="저장 없이 미리보기")
    parser.add_argument("--download-images", action="store_true", help="이미지 로컬 다운로드")
    parser.add_argument("--delay", type=float, default=1.0, help="요청 간 딜레이 초 (기본: 1.0)")
    args = parser.parse_args()

    crawl(
        start=args.start,
        end=args.end,
        dry_run=args.dry_run,
        dl_images=args.download_images,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
