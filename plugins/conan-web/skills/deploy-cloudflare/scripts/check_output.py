#!/usr/bin/env python3
"""Checks a static build folder against Cloudflare Pages limits and launch basics.

Usage: check_output.py <out-or-dist> [--site-url https://example.pages.dev]

Checks file limits, robots/sitemap/ads.txt/_headers/404, localhost URLs and placeholder
values (fake contact emails, example ids) in published pages.
Prints a Markdown table (Korean) and exits 1 when something must be fixed.
Only reads files; it never modifies the folder.
"""
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
    parser.add_argument("--site-url", help="expected production URL, e.g. https://name.pages.dev")
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

    add("한도", "파일 수", "통과" if len(files) <= MAX_FILES else "고칠 것", f"{len(files)}개 (한도 {MAX_FILES})")
    over = [f for f in files if f[1] > MAX_BYTES]
    near = [f for f in files if WARN_BYTES < f[1] <= MAX_BYTES]
    biggest = f"가장 큰 파일 {files[0][0]} {human(files[0][1])}" if files else "파일 없음"
    if over:
        add("한도", "파일당 25MiB", "고칠 것", ", ".join(f"{p} {human(s)}" for p, s in over))
    else:
        add("한도", "파일당 25MiB", "통과", biggest + (f" (20MB 넘는 파일 {len(near)}개)" if near else ""))

    names = {p for p, _ in files}
    has_404 = "404.html" in names or "404/index.html" in names
    add("경로", "404 페이지", "통과" if has_404 else "확인 필요", "404.html" if has_404 else "없으면 Cloudflare 기본 404가 나옵니다")

    robots = read(os.path.join(root, "robots.txt"))
    if not robots:
        add("검색", "robots.txt", "고칠 것", "없음")
    else:
        sitemap_line = re.search(r"(?im)^sitemap:\s*(\S+)", robots)
        disallow_all = re.search(r"(?im)^disallow:\s*/\s*$", robots)
        detail = f"Sitemap: {sitemap_line.group(1)}" if sitemap_line else "Sitemap 줄 없음"
        local = re.search(r"localhost|127\.0\.0\.1", robots)
        status = "고칠 것" if disallow_all or local else ("통과" if sitemap_line else "확인 필요")
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
            add("검색", "사이트맵 주소", "고칠 것", f"localhost 주소 {len(bad)}개. 사이트 주소 변수를 넣고 다시 빌드하세요")
        elif args.site_url and hosts and hosts != [args.site_url.rstrip("/")]:
            add("검색", "사이트맵 주소", "고칠 것", f"{', '.join(hosts)} (기대: {args.site_url})")
        else:
            add("검색", "사이트맵 주소", "통과", f"{', '.join(sitemaps)}, 주소 {len(locs)}개, {', '.join(hosts) or '-'}")

    ads = read(os.path.join(root, "ads.txt"))
    if "ads.txt" not in names:
        add("애드센스", "ads.txt", "확인 필요", "없음. 승인 후 반드시 필요합니다")
    elif re.search(r"google\.com,\s*pub-\d+", ads):
        add("애드센스", "ads.txt", "통과", ads.strip().splitlines()[0][:80])
    else:
        add("애드센스", "ads.txt", "확인 필요", "광고 ID 없음(승인 전이면 정상)")

    # Placeholder values left in published pages (fake contact, sample ids).
    placeholder = re.compile(
        r"[\w.+-]+@[\w-]+\.example\b|\bexample\.(?:com|org)\b|ca-pub-X{4,}|\bG-X{4,}|\bG-TEST\w*|YOUR[_-]?(?:EMAIL|ID|SITE)",
        re.I,
    )
    found = {}
    for path, _ in files:
        if path.endswith((".html", ".txt", ".xml")):
            for m in placeholder.findall(read(os.path.join(root, path))):
                found.setdefault(m, set()).add(path)
    if found:
        detail = "; ".join(f"{v} ({len(p)}개 파일, 예: {sorted(p)[0]})" for v, p in sorted(found.items())[:5])
        add("공개 값", "자리표시자", "고칠 것", detail + ". 실제 값을 넣거나, 값이 없으면 빌드를 막거나 숨기세요")
    else:
        add("공개 값", "자리표시자", "통과", "가짜 이메일·예시 도메인·예시 광고/분석 ID 없음")

    headers = read(os.path.join(root, "_headers"))
    if not headers:
        add("캐시", "_headers", "확인 필요", "없음. 큰 파일이 있으면 references/headers.md 참고")
    else:
        immutable = re.findall(r"(?m)^(/\S+)\n(?:[ \t]+.*\n)*?[ \t]+Cache-Control:.*immutable", headers + "\n")
        add("캐시", "_headers", "통과", "immutable 경로: " + (", ".join(immutable) or "없음"))

    print("| 구분 | 항목 | 상태 | 내용 |")
    print("|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print()
    print("큰 파일 상위 5개: " + ", ".join(f"{p} {human(s)}" for p, s in files[:5]))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
