#!/usr/bin/env python3
"""Checks live pages for a GA4 tag and consent defaults placed before the ad/analytics scripts.

Usage: check_ga.py https://example.pages.dev --id G-XXXXXXXXXX [--path /about --path /privacy]

Prints a Markdown table (Korean) and exits 1 when the tag is missing or misplaced.
Only sends GET requests.
"""

import argparse
import http.client
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (check_ga.py)"
SCRIPT_SRC = r"<script[^>]*\ssrc=[\"'][^\"']*{0}|\\\\?\"src\\\\?\":\\\\?\"[^\"\\\\]*{0}"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode("utf-8", errors="replace")


def first(pattern: str, html: str) -> int:
    m = re.search(pattern, html)
    return m.start() if m else -1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("site")
    p.add_argument("--id", required=True, help="expected measurement id, e.g. G-ABC123")
    p.add_argument(
        "--path", action="append", default=[], help="extra paths to check (default: /)"
    )
    args = p.parse_args()
    base = args.site.rstrip("/")
    paths = ["/"] + [x if x.startswith("/") else "/" + x for x in args.path]

    print("| 페이지 | 측정 ID | 다른 ID | 동의 기본값 | 순서 | 판정 |")
    print("|---|---|---|---|---|---|")
    fail = False
    for path in paths:
        try:
            html = fetch(base + path)
        except (OSError, ValueError, http.client.HTTPException) as e:
            print(f"| {path} | - | - | - | - | 고칠 것: 열 수 없음 ({e}) |")
            fail = True
            continue
        ids = sorted(set(re.findall(r"G-[A-Z0-9]{6,12}", html)))
        has_id = args.id in ids
        others = [i for i in ids if i != args.id]
        consent = first(r"gtag\(\s*['\"]consent['\"]\s*,\s*['\"]default['\"]", html)
        # Where the scripts actually load: <script src=...> tags, or Next.js next/script entries in the
        # flight data ("src":"..."). <link rel="preload"> hints come first in Next.js pages but run nothing.
        tag = first(SCRIPT_SRC.format("googletagmanager\\.com/gtag/js"), html)
        ads = first(SCRIPT_SRC.format("adsbygoogle\\.js"), html)
        later = [x for x in (tag, ads) if x >= 0]
        if consent < 0:
            order = "동의 기본값 없음"
        elif not later:
            order = "-"
        elif consent < min(later):
            order = "앞에 있음"
        else:
            order = "뒤에 있음"
        problems = []
        if not has_id:
            problems.append("측정 ID 없음(배포 전이거나 변수 이름이 틀림)")
        if others:
            problems.append("다른 ID가 섞여 있음")
        if consent < 0:
            problems.append("동의 기본값 없음")
        elif order == "뒤에 있음":
            problems.append("동의 기본값이 GA·애드센스보다 뒤에 있음")
        verdict = "통과" if not problems else "고칠 것: " + ", ".join(problems)
        fail = fail or bool(problems)
        print(
            f"| {path} | {'있음' if has_id else '없음'} | {', '.join(others) or '-'} | "
            f"{'있음' if consent >= 0 else '없음'} | {order} | {verdict} |"
        )
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
