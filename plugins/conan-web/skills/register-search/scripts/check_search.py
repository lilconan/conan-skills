#!/usr/bin/env python3
"""Checks a live site for search-engine verification tags, robots.txt and the sitemap.

Usage: check_search.py https://example.pages.dev [--sitemap sitemap-index.xml]

Prints a Markdown table (Korean) and exits 1 when something blocks registration.
Only sends GET requests.
"""

import argparse
import http.client
import re
import sys
import urllib.error
import urllib.request
import xml.dom.minidom
import xml.parsers.expat

UA = "Mozilla/5.0 (check_search.py)"
TAGS = {
    "google-site-verification": "구글 서치 콘솔",
    "naver-site-verification": "네이버 서치어드바이저",
    "msvalidate.01": "Bing(직접 인증할 때만)",
}


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return (
                res.status,
                res.headers.get("content-type", ""),
                res.read().decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("content-type", ""), ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("site")
    p.add_argument(
        "--sitemap", help="sitemap path; default: from robots.txt, else sitemap.xml"
    )
    args = p.parse_args()
    base = args.site.rstrip("/")
    host = re.sub(r"^https?://", "", base)
    rows, fail = [], False

    def add(item, status, detail):
        nonlocal fail
        fail = fail or status == "고칠 것"
        rows.append((item, status, detail))

    code, _, html = fetch(base + "/")
    if code != 200:
        add("홈 페이지", "고칠 것", f"응답 {code}")
    for name, label in TAGS.items():
        m = re.search(
            r'<meta[^>]*name="' + re.escape(name) + r'"[^>]*content="([^"]*)"', html
        ) or re.search(
            r'<meta[^>]*content="([^"]*)"[^>]*name="' + re.escape(name) + r'"', html
        )
        if m:
            add(f"인증 태그: {label}", "있음", m.group(1))
        else:
            add(
                f"인증 태그: {label}",
                "없음",
                "필요하면 사이트 설정에 넣고 배포"
                if name != "msvalidate.01"
                else "서치 콘솔에서 가져오면 필요 없음",
            )
    if re.search(r'<meta[^>]*name="robots"[^>]*content="[^"]*noindex', html):
        add("홈 noindex", "고칠 것", "홈 페이지에 noindex가 있음")

    code, _, robots = fetch(base + "/robots.txt")
    sitemap_url = None
    if code != 200:
        add("robots.txt", "고칠 것", f"응답 {code}")
    else:
        blocked = re.search(r"(?im)^disallow:\s*/\s*$", robots)
        sm = re.search(r"(?im)^sitemap:\s*(\S+)", robots)
        sitemap_url = sm.group(1) if sm else None
        detail = f"Sitemap: {sitemap_url}" if sitemap_url else "Sitemap 줄 없음"
        if blocked:
            add("robots.txt", "고칠 것", detail + " / 전체 차단(Disallow: /)")
        elif sitemap_url and host not in sitemap_url:
            add("robots.txt", "고칠 것", detail + " / 실제 주소가 아님")
        else:
            add("robots.txt", "통과" if sitemap_url else "확인 필요", detail)

    if args.sitemap:
        sitemap_url = base + "/" + args.sitemap.lstrip("/")
    sitemap_url = sitemap_url or base + "/sitemap.xml"
    code, ctype, body = fetch(sitemap_url)
    if code != 200:
        add("사이트맵", "고칠 것", f"{sitemap_url} 응답 {code}")
    else:
        try:
            # Sitemaps never need a DTD; refusing one keeps entity expansion out of the parser.
            if re.search(r"<!(DOCTYPE|ENTITY)", body, re.IGNORECASE):
                raise ValueError("DOCTYPE/ENTITY 선언이 있음")
            doc = xml.dom.minidom.parseString(body)
            locs = [
                n.firstChild.nodeValue.strip()
                for n in doc.getElementsByTagName("loc")
                if n.firstChild
            ]
            wrong = [u for u in locs if host not in u]
            if wrong:
                add("사이트맵", "고칠 것", f"다른 주소 {len(wrong)}개 (예: {wrong[0]})")
            else:
                add(
                    "사이트맵",
                    "통과",
                    f"{sitemap_url}, {ctype.split(';')[0]}, 주소 {len(locs)}개",
                )
        except (ValueError, xml.parsers.expat.ExpatError) as e:
            add("사이트맵", "고칠 것", f"XML이 올바르지 않음 ({e})")

    # Crawlers must not be blocked (bot protection, WAF rules) or the consoles cannot fetch anything.
    for bot, ua in (
        (
            "Googlebot",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        ),
        ("네이버 Yeti", "Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)"),
        (
            "bingbot",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        ),
    ):
        try:
            req = urllib.request.Request(base + "/", headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=20) as res:
                status = res.status
        except urllib.error.HTTPError as e:
            status = e.code
        except (OSError, http.client.HTTPException) as e:  # network errors
            status = str(e)
        add(
            f"크롤러 접근: {bot}",
            "통과" if status == 200 else "고칠 것",
            f"응답 {status}",
        )

    print("| 항목 | 상태 | 내용 |")
    print("|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
