# 검색엔진 콘솔 화면 순서

기준: 2026-11 PixelUp(pixelup-ai.pages.dev) 등록 때의 화면. 화면 문구가 바뀌면 비슷한 메뉴를 찾는다. Claude in Chrome 사용 전 `anthropic-skills:chrome-browser` 안내를 따른다. 버튼은 `find`로 찾아 `ref`로 누르는 쪽이 정확하다.

## 구글 서치 콘솔

1. `https://search.google.com/search-console?authuser=<email>` → 주소가 `/u/<n>/search-console?resource_id=…`로 바뀌면 그 계정에 등록된 속성이 있다.
2. 처음 뜨는 안내 풍선(신규 기능 소개)은 닫는다.
3. 왼쪽 위 속성 선택 목록 → **속성 추가** → "속성 유형 선택"에서 **웹사이트 추가**(Instagram·TikTok 등 다른 유형도 같은 창에 나온다).
4. **URL 접두어** 칸에 `https://<site>/` → 계속.
5. "소유권 확인" 창: 권장 방법은 HTML 파일이지만, **HTML 태그**를 펼친다. 값은 페이지 텍스트에서 뽑는다.
   ```js
   [...document.querySelectorAll('input,textarea,code,span,div')]
     .map(e => e.value || e.textContent || '')
     .find(s => s.includes('google-site-verification') && s.length < 200)
   ```
6. 배포 후 같은 창에서 HTML 태그 칸의 **확인** → "소유권이 확인됨" → 속성으로 이동.
7. 사이트맵: `https://search.google.com/u/<n>/search-console/sitemaps?resource_id=https%3A%2F%2F<site>%2F` → "새 사이트맵 추가"에 `sitemap.xml` → 제출 → "사이트맵이 제출됨". 표의 상태가 처음엔 "가져올 수 없음"이어도 정상인 경우가 많다.
   - 그래도 확인할 것: `curl -sI https://<site>/sitemap.xml`이 200이고 `content-type: application/xml`, 내용이 올바른 XML인지(`scripts/check_search.py`가 확인).

## 네이버 서치어드바이저 (사용자가 직접)

Claude in Chrome은 `searchadvisor.naver.com`을 "safety restrictions"로 열지 못한다. 사용자 안내 순서:

1. searchadvisor.naver.com → 로그인 → 웹마스터 도구 → 사이트 관리 → 사이트 등록에 `https://<site>` 입력.
2. 소유확인 방법에서 **HTML 태그** → `<meta name="naver-site-verification" content="…">`의 content 값을 알려 달라고 한다.
3. 배포 후: **소유확인** 버튼.
4. 요청 → **사이트맵 제출**에 `robots.txt`의 `Sitemap:` 주소(Next.js `…/sitemap.xml`, Astro `…/sitemap-index.xml`). RSS가 있으면 RSS 제출.
5. 검증 → **robots.txt**에서 수집 허용 상태를 볼 수 있다.

## Bing 웹마스터 도구

1. `https://www.bing.com/webmasters/home` → 이미 등록한 사이트가 있으면 왼쪽 위 사이트 목록 → **Add a site**.
2. "Select one of the methods": 왼쪽 **Google Search Console → Import**.
3. 설명 화면(가져오는 것은 인증된 사이트 목록과 사이트맵뿐, 보기 전용 권한) → **Continue**. 이 내용을 사용자에게 알리고 승인을 받은 뒤 진행한다.
4. 구글 계정 선택(서치 콘솔이 있는 계정) → 이미 허용한 적이 있으면 "bing.com에 다시 로그인하는 중" → 계속 → "bing.com에서 Google 계정에 대한 액세스를 요청" → 계속. 요청 범위는 `webmasters.readonly`, `userinfo.email`.
5. "Import from Google Search Console": 가져올 사이트를 체크(이미 Bing에 있는 사이트는 목록에 안 나옴) → **Import**.
6. 사이트 목록에 새 사이트가 보이면 끝. 서치 콘솔에 제출한 사이트맵도 함께 들어온다. 보고서는 최대 48시간 뒤에 채워진다.
