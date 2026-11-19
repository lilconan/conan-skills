#!/usr/bin/env python3
"""Submits page URLs to search engines through IndexNow (Naver, Bing and others).

Usage:
  indexnow_submit.py https://<site> <key> [--filter REGEX] [--endpoint URL] [--dry-run]
  indexnow_submit.py https://<site> <key> --urls urls.txt

Reads the URL list from the site's live sitemap (robots.txt Sitemap: line, sitemap index
included) unless --urls is given, keeps the URLs matching --filter, checks that
https://<site>/<key>.txt serves exactly the key, then POSTs one JSON request.
HTTP 200 or 202 means the request was accepted, not that pages are indexed.
Prints a Markdown table (Korean) and exits 1 when the key file or the request fails.
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

NAVER = "https://searchadvisor.naver.com/indexnow"
UA = "conan-web-indexnow/1.0"


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (OSError, http.client.HTTPException) as e:
        return 0, str(e)


def sitemap_urls(site: str) -> list[str]:
    _, robots = fetch(site + "/robots.txt")
    queue = re.findall(r"(?im)^sitemap:\s*(\S+)", robots) or [site + "/sitemap.xml"]
    seen, urls = set(), []
    while queue:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        _, xml = fetch(sm)
        if re.search(r"<!DOCTYPE|<!ENTITY", xml):
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
        if "<sitemapindex" in xml:
            queue.extend(locs)
        else:
            urls.extend(locs)
    return list(dict.fromkeys(urls))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("site", help="https://<site> (no trailing slash needed)")
    p.add_argument("key", help="IndexNow key, also served at /<key>.txt")
    p.add_argument("--urls", help="file with one URL per line instead of the sitemap")
    p.add_argument("--filter", help="regex the URL must match, e.g. '/ko($|/)'")
    p.add_argument("--endpoint", default=NAVER, help=f"default {NAVER}")
    p.add_argument("--dry-run", action="store_true", help="list URLs, do not POST")
    a = p.parse_args()

    site = a.site.rstrip("/")
    host = urllib.parse.urlparse(site).netloc
    rows, ok = [], True

    code, body = fetch(f"{site}/{a.key}.txt")
    key_ok = code == 200 and body.strip() == a.key
    ok &= key_ok
    rows.append(
        (
            "키 파일",
            "통과" if key_ok else "고칠 것",
            f"/{a.key}.txt {code}"
            + ("" if key_ok else " / 내용이 키와 같지 않거나 아직 배포 전"),
        )
    )

    if a.urls:
        with open(a.urls, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = sitemap_urls(site)
    if a.filter:
        urls = [u for u in urls if re.search(a.filter, u)]
    urls = [u for u in urls if urllib.parse.urlparse(u).netloc == host]
    rows.append(
        (
            "주소 목록",
            "통과" if urls else "고칠 것",
            f"{len(urls)}개" + (f", 예: {urls[0]}" if urls else ""),
        )
    )
    ok &= bool(urls)

    if a.dry_run or not ok:
        rows.append(
            ("제출", "보류", "--dry-run" if a.dry_run else "위 문제를 먼저 고치세요")
        )
    else:
        payload = {
            "host": host,
            "key": a.key,
            "keyLocation": f"{site}/{a.key}.txt",
            "urlList": urls[:10000],
        }
        req = urllib.request.Request(
            a.endpoint,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": UA,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                status, text = r.status, r.read()[:200].decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            status, text = e.code, e.read()[:200].decode("utf-8", "replace")
        except (OSError, http.client.HTTPException) as e:
            status, text = 0, str(e)
        accepted = status in (200, 202)
        ok &= accepted
        rows.append(
            (
                "제출",
                "통과" if accepted else "고칠 것",
                f"{a.endpoint} → {status} {text.strip()}".strip()
                + (" (접수됨. 색인까지는 며칠 걸림)" if accepted else ""),
            )
        )

    print("| 항목 | 상태 | 내용 |")
    print("|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    if a.dry_run:
        print()
        print("\n".join(urls))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
