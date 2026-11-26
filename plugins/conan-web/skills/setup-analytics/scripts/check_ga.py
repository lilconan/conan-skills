#!/usr/bin/env python3
"""Checks live pages for a GA4 tag and consent defaults placed before the ad/analytics scripts.

Also reads what the consent defaults say outside the regional (EEA/UK/CH) call: an
ad_storage 'denied' default without a region list turns off personalized ads everywhere,
which two projects shipped by mistake. That case is reported as 확인 필요.

Sites that add the tag from JavaScript (a plain-HTML site whose module calls gtag and creates the
gtag/js <script> at run time) have nothing in the HTML. When the HTML lacks the measurement id, the
script follows same-origin scripts (<script src>, inline modules, and their static/dynamic imports,
up to MAX_JS_FILES files) and checks the file that holds the id instead. The "찾은 곳" column says which.

Usage: check_ga.py https://example.pages.dev --id G-XXXXXXXXXX [--path /about --path /privacy]

Prints a Markdown table (Korean) and exits 1 when the tag is missing or misplaced.
Only sends GET requests.
"""

from __future__ import annotations

import argparse
import http.client
import re
import sys
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (check_ga.py)"
SCRIPT_SRC = r"<script[^>]*\ssrc=[\"'][^\"']*{0}|\\\\?\"src\\\\?\":\\\\?\"[^\"\\\\]*{0}"
MAX_JS_FILES = 30
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
SRC_ATTR = re.compile(r"\ssrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
IMPORT = re.compile(
    r"\bimport\s*(?:[\w*{}\s,]+\s*from\s*)?[\"']([^\"']+)[\"']"  # import x from "./a.js" / import "./a.js"
    r"|\bexport\s*[\w*{}\s,]+\s*from\s*[\"']([^\"']+)[\"']"  # export { x } from "./a.js"
    r"|\bimport\(\s*[\"']([^\"']+)[\"']\s*\)"  # import("./a.js")
)


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.read().decode("utf-8", errors="replace")


def same_origin_scripts(page_url: str, html: str) -> list[tuple[str, str]]:
    """Returns (name, text) for inline scripts and same-origin script files the page loads, following imports."""
    origin = urllib.parse.urlsplit(page_url)[:2]
    found: list[tuple[str, str]] = []
    queue: list[tuple[str, str]] = []  # (base url to resolve against, specifier)
    for attrs, body in SCRIPT_TAG.findall(html):
        m = SRC_ATTR.search(attrs)
        if m:
            queue.append((page_url, m.group(1)))
        elif body.strip():
            found.append(("인라인 스크립트", body))
            queue += [(page_url, x) for x in imports_of(body)]
    seen: set[str] = set()
    while queue and len(seen) < MAX_JS_FILES:
        base, spec = queue.pop(0)
        url = urllib.parse.urljoin(base, spec).split("#")[0]
        if urllib.parse.urlsplit(url)[:2] != origin or url in seen:
            continue  # other sites (CDNs, the gtag loader itself) are not this site's code
        seen.add(url)
        try:
            text = fetch(url)
        except (OSError, ValueError, http.client.HTTPException):
            continue
        found.append((urllib.parse.urlsplit(url).path, text))
        queue += [(url, x) for x in imports_of(text)]
    return found


def imports_of(js: str) -> list[str]:
    return [a or b or c for a, b, c in IMPORT.findall(js)]


def first(pattern: str, html: str) -> int:
    m = re.search(pattern, html)
    return m.start() if m else -1


def consent_outside_region(html: str) -> str:
    """Summarizes the ad_storage default that applies outside the region-limited call."""
    calls = re.findall(
        r"gtag\(\s*['\"]consent['\"]\s*,\s*['\"]default['\"]\s*,\s*\{(.*?)\}\s*\)",
        html,
        re.DOTALL,
    )
    if not calls:
        return "-"
    # Keys may be bare (ad_storage: 'denied') or quoted ("ad_storage":"denied").
    general = [c for c in calls if not re.search(r"\bregion['\"]?\s*:", c)]
    regional = [c for c in calls if c not in general]
    for c in general:
        m = re.search(r"ad_storage['\"]?\s*:\s*['\"](\w+)['\"]", c)
        if m:
            return "허용" if m.group(1) == "granted" else "거부"
    return "지정 안 함(허용으로 동작)" if regional else "-"


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

    print(
        "| 페이지 | 찾은 곳 | 측정 ID | 다른 ID | 동의 기본값 | 순서 | 지역 밖 광고 저장 | 판정 |"
    )
    print("|---|---|---|---|---|---|---|---|")
    fail = False
    for path in paths:
        try:
            html = fetch(base + path)
        except (OSError, ValueError, http.client.HTTPException) as e:
            print(f"| {path} | - | - | - | - | - | - | 고칠 것: 열 수 없음 ({e}) |")
            fail = True
            continue
        where = "HTML"
        text = html
        script_src = SCRIPT_SRC
        if args.id not in html:
            # The tag may be added by JavaScript: look in the page's own scripts and use the file with the id
            for name, js in same_origin_scripts(base + path, html):
                if args.id in js:
                    where, text = f"JS: {name}", js
                    # In JS the loader is created at run time (s.src = "...gtag/js?id=..."), so any mention counts
                    script_src = r"{0}"
                    break
        ids = sorted(set(re.findall(r"G-[A-Z0-9]{6,12}", text)))
        has_id = args.id in ids
        others = [i for i in ids if i != args.id]
        consent = first(r"gtag\(\s*['\"]consent['\"]\s*,\s*['\"]default['\"]", text)
        # Where the scripts actually load: <script src=...> tags, or Next.js next/script entries in the
        # flight data ("src":"..."). <link rel="preload"> hints come first in Next.js pages but run nothing.
        tag = first(script_src.format("googletagmanager\\.com/gtag/js"), text)
        ads = first(script_src.format("adsbygoogle\\.js"), text)
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
            problems.append(
                "측정 ID 없음(배포 전이거나 변수 이름이 틀림, HTML과 이 사이트의 JS 파일 모두에서 못 찾음)"
            )
        if others:
            problems.append("다른 ID가 섞여 있음")
        if consent < 0:
            problems.append("동의 기본값 없음")
        elif order == "뒤에 있음":
            problems.append("동의 기본값이 GA·애드센스보다 뒤에 있음")
        outside = consent_outside_region(text)
        verdict = "통과" if not problems else "고칠 것: " + ", ".join(problems)
        if not problems and outside == "거부":
            verdict = (
                "확인 필요: 유럽·영국·스위스 밖에서도 광고 쿠키를 거부함"
                "(맞춤 광고가 꺼짐. 의도인지, 개인정보처리방침과 맞는지 확인)"
            )
        fail = fail or bool(problems)
        print(
            f"| {path} | {where if has_id else '-'} | {'있음' if has_id else '없음'} | {', '.join(others) or '-'} | "
            f"{'있음' if consent >= 0 else '없음'} | {order} | {outside} | {verdict} |"
        )
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
