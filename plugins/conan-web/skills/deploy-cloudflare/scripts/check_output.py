#!/usr/bin/env python3
"""Checks a static build folder against Cloudflare Pages limits and launch basics.

Usage: check_output.py <out-or-dist> [--site-url https://example.pages.dev]

Checks file limits, robots/sitemap/ads.txt/_headers/404, localhost URLs, placeholder
values (fake contact emails, example ids) in published pages, page titles and share
metadata, home-screen icons, and internal links that point at missing files.
Prints a Markdown table (Korean) and exits 1 when something must be fixed.
Only reads files; it never modifies the folder.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

MAX_FILES = 20_000
MAX_BYTES = 25 * 1024 * 1024
WARN_BYTES = 20 * 1024 * 1024


def human(n: int) -> str:
    return f"{n / 1024 / 1024:.1f}MB"


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument(
        "--site-url", help="expected production URL, e.g. https://name.pages.dev"
    )
    args = parser.parse_args()
    root = args.folder.rstrip("/")
    if not os.path.isdir(root):
        print(f"폴더가 없습니다: {root}. 먼저 빌드하세요.")
        return 1

    files = []
    for dirpath, _, names in os.walk(root):
        for name in names:
            path = os.path.join(dirpath, name)
            files.append((os.path.relpath(path, root), os.path.getsize(path)))
    files.sort(key=lambda f: -f[1])

    rows = []  # (구분, 항목, 상태, 내용)
    fail = False

    def add(group, item, status, detail):
        nonlocal fail
        if status == "고칠 것":
            fail = True
        rows.append((group, item, status, detail))

    add(
        "한도",
        "파일 수",
        "통과" if len(files) <= MAX_FILES else "고칠 것",
        f"{len(files)}개 (한도 {MAX_FILES})",
    )
    over = [f for f in files if f[1] > MAX_BYTES]
    near = [f for f in files if WARN_BYTES < f[1] <= MAX_BYTES]
    biggest = (
        f"가장 큰 파일 {files[0][0]} {human(files[0][1])}" if files else "파일 없음"
    )
    if over:
        add(
            "한도",
            "파일당 25MiB",
            "고칠 것",
            ", ".join(f"{p} {human(s)}" for p, s in over),
        )
    else:
        add(
            "한도",
            "파일당 25MiB",
            "통과",
            biggest + (f" (20MB 넘는 파일 {len(near)}개)" if near else ""),
        )

    names = {p for p, _ in files}
    has_404 = "404.html" in names or "404/index.html" in names
    add(
        "경로",
        "404 페이지",
        "통과" if has_404 else "확인 필요",
        "404.html" if has_404 else "없으면 Cloudflare 기본 404가 나옵니다",
    )

    robots = read(os.path.join(root, "robots.txt"))
    if not robots:
        add("검색", "robots.txt", "고칠 것", "없음")
    else:
        sitemap_line = re.search(r"(?im)^sitemap:\s*(\S+)", robots)
        disallow_all = re.search(r"(?im)^disallow:\s*/\s*$", robots)
        detail = (
            f"Sitemap: {sitemap_line.group(1)}" if sitemap_line else "Sitemap 줄 없음"
        )
        local = re.search(r"localhost|127\.0\.0\.1", robots)
        status = (
            "고칠 것"
            if disallow_all or local
            else ("통과" if sitemap_line else "확인 필요")
        )
        if disallow_all:
            detail += " / 전체 차단(Disallow: /)"
        if local:
            detail += " / localhost 주소. 사이트 주소 변수를 넣고 다시 빌드하세요"
        add("검색", "robots.txt", status, detail)

    sitemaps = sorted(p for p in names if re.fullmatch(r"sitemap[^/]*\.xml", p))
    if not sitemaps:
        add("검색", "sitemap.xml", "고칠 것", "없음")
    else:
        text = "".join(read(os.path.join(root, p)) for p in sitemaps)
        locs = re.findall(r"<loc>([^<]+)</loc>", text)
        bad = [u for u in locs if re.search(r"localhost|127\.0\.0\.1", u)]
        hosts = sorted({re.sub(r"^(https?://[^/]+).*", r"\1", u) for u in locs})
        if bad:
            add(
                "검색",
                "사이트맵 주소",
                "고칠 것",
                f"localhost 주소 {len(bad)}개. 사이트 주소 변수를 넣고 다시 빌드하세요",
            )
        elif args.site_url and hosts and hosts != [args.site_url.rstrip("/")]:
            add(
                "검색",
                "사이트맵 주소",
                "고칠 것",
                f"{', '.join(hosts)} (기대: {args.site_url})",
            )
        else:
            add(
                "검색",
                "사이트맵 주소",
                "통과",
                f"{', '.join(sitemaps)}, 주소 {len(locs)}개, {', '.join(hosts) or '-'}",
            )

    ads = read(os.path.join(root, "ads.txt"))
    if "ads.txt" not in names:
        add(
            "애드센스",
            "ads.txt",
            "확인 필요",
            "없음. 정적 사이트는 404가 나가므로 주석 한 줄이라도 두고, 게시자 ID는 심사 요청 전에 넣으세요",
        )
    elif re.search(r"google\.com,\s*pub-\d+", ads):
        add("애드센스", "ads.txt", "통과", ads.strip().splitlines()[0][:80])
    else:
        add(
            "애드센스",
            "ads.txt",
            "확인 필요",
            "광고 ID 없음. 애드센스 심사를 요청하기 전에 게시자 ID를 넣고 다시 배포하세요",
        )

    # Placeholder values left in published pages (fake contact, sample ids).
    placeholder = re.compile(
        r"[\w.+-]+@[\w-]+\.example\b|\bexample\.(?:com|org)\b|ca-pub-X{4,}|\bG-X{4,}|\bG-TEST\w*|YOUR[_-]?(?:EMAIL|ID|SITE)",
        re.IGNORECASE,
    )
    found = {}
    for path, _ in files:
        if path.endswith((".html", ".txt", ".xml")):
            for m in placeholder.findall(read(os.path.join(root, path))):
                found.setdefault(m, set()).add(path)
    if found:
        detail = "; ".join(
            f"{v} ({len(p)}개 파일, 예: {min(p)})" for v, p in sorted(found.items())[:5]
        )
        add(
            "공개 값",
            "자리표시자",
            "고칠 것",
            detail + ". 실제 값을 넣거나, 값이 없으면 빌드를 막거나 숨기세요",
        )
    else:
        add(
            "공개 값",
            "자리표시자",
            "통과",
            "가짜 이메일·예시 도메인·예시 광고/분석 ID 없음",
        )

    headers = read(os.path.join(root, "_headers"))
    if not headers:
        add(
            "캐시",
            "_headers",
            "확인 필요",
            "없음. 큰 파일이 있으면 references/headers.md 참고",
        )
    else:
        immutable = re.findall(
            r"(?m)^(/\S+)\n(?:[ \t]+.*\n)*?[ \t]+Cache-Control:.*immutable",
            headers + "\n",
        )
        add(
            "캐시",
            "_headers",
            "통과",
            "immutable 경로: " + (", ".join(immutable) or "없음"),
        )

    # Pages: titles, share metadata, internal links.
    pages = [
        p
        for p in names
        if p.endswith(".html")
        and not re.search(r"(^|/)(404|_not-found|500)(/index)?\.html$", p)
        and not re.fullmatch(r"google[0-9a-f]+\.html", p)
    ]
    if not pages:
        add(
            "페이지",
            "HTML 페이지",
            "고칠 것",
            "0개. 빌드가 실패했거나 다른 폴더를 검사하고 있습니다",
        )
    else:
        add("페이지", "HTML 페이지", "통과", f"{len(pages)}개")

    def meta(html: str, key: str) -> str | None:
        m = re.search(
            r"<meta[^>]+(?:property|name)=\""
            + re.escape(key)
            + r"\"[^>]*content=\"([^\"]*)\"",
            html,
        ) or re.search(
            r"<meta[^>]+content=\"([^\"]*)\"[^>]*(?:property|name)=\""
            + re.escape(key)
            + r"\"",
            html,
        )
        return m.group(1) if m else None

    bad_title, title_mismatch, no_og_image, no_tw_image, missing_image = (
        [],
        [],
        [],
        [],
        set(),
    )
    links = {}  # internal path -> first page that links to it
    for page in sorted(pages):
        html = read(os.path.join(root, page))
        titles = re.findall(r"<title[^>]*>([^<]*)</title>", html)
        if len(titles) != 1 or not titles[0].strip():
            bad_title.append(page)
        else:
            title = titles[0].strip()
            for key in ("og:title", "twitter:title"):
                value = meta(html, key)
                if value is not None and value.strip() != title:
                    title_mismatch.append(f"{page} {key}")
        og_image = meta(html, "og:image")
        if not og_image:
            no_og_image.append(page)
        else:
            path = re.sub(r"^https?://[^/]+", "", og_image).split("?")[0].lstrip("/")
            if path and path not in names:
                missing_image.add(path)
        if not meta(html, "twitter:image"):
            no_tw_image.append(page)
        for href in re.findall(r"\shref=\"(/[^\"#?]*)", html):
            if href.startswith(("//", "/cdn-cgi/")):
                continue
            links.setdefault(href, page)

    def sample(items: list[str]) -> str:
        return ", ".join(items[:3]) + (
            f" 외 {len(items) - 3}개" if len(items) > 3 else ""
        )

    if pages:
        add(
            "메타",
            "<title>",
            "고칠 것" if bad_title else "통과",
            f"없거나 여러 개: {sample(bad_title)}"
            if bad_title
            else "모든 페이지에 하나씩",
        )
        add(
            "메타",
            "og·twitter 제목",
            "확인 필요" if title_mismatch else "통과",
            f"<title>과 다름: {sample(title_mismatch)}"
            if title_mismatch
            else "<title>과 같음",
        )
        if no_og_image or no_tw_image or missing_image:
            parts = []
            if no_og_image:
                parts.append(
                    f"og:image 없음 {len(no_og_image)}개(예: {no_og_image[0]})"
                )
            if no_tw_image:
                parts.append(
                    f"twitter:image 없음 {len(no_tw_image)}개(예: {no_tw_image[0]})"
                )
            if missing_image:
                parts.append("가리키는 파일 없음: " + ", ".join(sorted(missing_image)))
            add(
                "메타",
                "공유 이미지",
                "고칠 것" if missing_image else "확인 필요",
                "; ".join(parts),
            )
        else:
            add("메타", "공유 이미지", "통과", "모든 페이지에 og:image·twitter:image")

    icons = {
        "favicon.ico": "favicon.ico" in names,
        "apple-touch-icon.png": "apple-touch-icon.png" in names,
        "manifest": bool(
            {"manifest.json", "manifest.webmanifest", "site.webmanifest"} & names
        ),
    }
    absent = [k for k, ok in icons.items() if not ok]
    add(
        "아이콘",
        "favicon·터치 아이콘·매니페스트",
        "확인 필요" if absent else "통과",
        ("없음: " + ", ".join(absent)) if absent else "모두 있음",
    )

    def resolves(href: str) -> bool:
        path = href.lstrip("/")
        if not path:
            return "index.html" in names
        path = path.rstrip("/")
        return any(c in names for c in (path, path + ".html", path + "/index.html"))

    broken = sorted((h, p) for h, p in links.items() if not resolves(h))
    if pages:
        add(
            "경로",
            "내부 링크",
            "고칠 것" if broken else "통과",
            (
                "파일 없음: " + sample([f"{h} ({p}에서)" for h, p in broken])
                if broken
                else f"주소 {len(links)}개 모두 파일 있음"
            ),
        )

    print("| 구분 | 항목 | 상태 | 내용 |")
    print("|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print()
    print("큰 파일 상위 5개: " + ", ".join(f"{p} {human(s)}" for p, s in files[:5]))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
