---
name: register-search
description: 배포된 정적 웹사이트(Cloudflare Pages의 Next.js·Astro·Vite 사이트 등)를 검색엔진에 등록하는 스킬. 구글 서치 콘솔과 네이버 서치어드바이저의 HTML 태그 인증 값을 사이트 설정에 넣어 배포하고, 소유 확인과 사이트맵 제출을 하고, Bing 웹마스터 도구는 서치 콘솔에서 가져오고, 네이버 페이지 수집 요청은 IndexNow로 보낸다. 사용자가 "서치 콘솔", "구글 검색 등록", "네이버 검색 등록", "서치어드바이저", "웹마스터 도구", "Bing 등록", "사이트맵 제출", "검색에 안 나와", "색인", "인증 태그", "site-verification", "수집 요청", "IndexNow", "가져올 수 없음"을 말하거나, 새 사이트를 공개한 직후 검색 노출을 준비할 때, 도메인을 바꿔 다시 인증해야 할 때는 직접 언급하지 않아도 반드시 이 스킬을 쓴다.
metadata:
  version: 0.3.0
  updated: 2026-11-20
---

# register-search: 검색엔진에 사이트 등록하기

배포된 사이트를 구글, 네이버, Bing에 등록해 검색에 노출되게 하는 순서다. 인증 값 받기 → 사이트에 넣고 배포 → 소유 확인 → 사이트맵 제출 → Bing 가져오기 → (네이버 수집 요청은 IndexNow) → 기록으로 진행한다.
배포 자체는 `conan-web:deploy-cloudflare`, 분석 연결은 `conan-web:setup-analytics`가 맡는다.

## 기본 원칙

- **사용자에게 하는 말은 모두 한국어로 쓴다.** 진행 안내, 마무리 요약, 질문과 버튼 문구까지 전부다.
- **인증은 주소 단위다.** `https://<project>.pages.dev/`로 인증한 것은 나중에 자기 도메인으로 옮기면 다시 해야 한다. 그래서 인증 값은 한곳(사이트 설정)에 모아 두고, 어떤 주소로 인증했는지 주석과 `DEPLOY.md`에 남긴다.
- **권한을 넘기는 일은 미리 묻는다.** Bing이 구글 서치 콘솔을 읽도록 허용하는 것(OAuth)은 사용자 승인을 받고 진행한다. 허용 화면에 나온 범위(`webmasters.readonly` 등)를 사용자에게 그대로 알려 준다.
- **사용자가 직접 해야 하는 곳은 분명히 나눈다.** 네이버 서치어드바이저(searchadvisor.naver.com)는 **어떤 에이전트 브라우저로도 열리지 않는다.** 앱 안의 브라우저와 Claude in Chrome(웨일 같은 다른 Chromium 브라우저에 설치해도 마찬가지)이 모두 "safety restrictions"로 막는다. 다른 브라우저 도구로 우회하려 하지 말고, 네이버 단계는 사용자에게 무엇을 누르고 어떤 값을 알려 달라고 할지 정확히 안내한다.
- **사용자를 기다리기 전에 에이전트가 할 수 있는 대안을 먼저 낸다.** 네이버의 페이지 수집 요청은 IndexNow로 대신 보낼 수 있다([references/indexnow.md](references/indexnow.md)). 사용자가 할 수 없거나 미룬 단계를 완료로 표시하지 않고, 같은 확인 질문을 되풀이하지도 않는다. 할 수 있는 일과 사용자만 할 수 있는 일을 한 번에 정리해 보여 주고 기다린다.
- **브라우저 고르기:** 구글 서치 콘솔·Bing은 앱 안의 브라우저(로그인 유지)와 Claude in Chrome 어느 쪽이든 된다. 네이버는 둘 다 안 된다.
- **인증 메타 태그 값은 공개 값이다.** 저장소와 코드에 넣어도 된다.

## 0. 점검

1. 사이트가 배포되어 있고, `robots.txt`가 크롤러를 막지 않으며, 사이트맵이 실제 주소로 나오는지 [scripts/check_search.py](scripts/check_search.py)로 확인한다.
   ```bash
   python3 <skill-dir>/scripts/check_search.py https://<site>
   ```
   인증 태그(google·naver·msvalidate), robots의 `Sitemap:` 줄과 차단 여부, 사이트맵 응답·형식·주소, 검색엔진 크롤러(Googlebot·Yeti·bingbot)로 요청했을 때의 응답을 표로 보여 준다. 크롤러가 403이면 Cloudflare 봇 차단·WAF 설정을 먼저 본다. 사이트맵에 localhost가 있으면 먼저 `deploy-cloudflare` 스킬로 고친다(잘못된 주소를 제출하면 색인이 꼬인다).
2. 사이트 설정에서 인증 값을 넣을 곳을 정한다. 프레임워크별 방법은 [references/verification-tags.md](references/verification-tags.md)에 있다. 권장 구조는 `meta name → content` 지도 하나에 모든 검색엔진 값을 두고, 값이 빈 항목은 태그를 넣지 않는 방식이다.

## 1. 구글 서치 콘솔 (Claude in Chrome)

자세한 화면 순서는 [references/search-consoles.md](references/search-consoles.md)의 "구글"을 읽는다. 요약:

1. `https://search.google.com/search-console?authuser=<email>`로 들어간다. 다른 사이트가 이미 등록된 계정이 대개 맞다. 계정이 여러 개면 사용자에게 묻는다.
2. 속성 선택 목록 → 속성 추가 → 웹사이트 추가 → **URL 접두어**에 `https://<site>/`를 넣는다. `*.pages.dev`는 DNS를 직접 바꿀 수 없으므로 "도메인" 속성은 쓸 수 없다.
3. 확인 방법에서 **HTML 태그**를 펼쳐 `content` 값을 페이지 텍스트에서 뽑는다. 같은 구글 계정이면 사이트가 달라도 값이 같은 경우가 많다(그래도 그대로 넣는다).
4. 아직 "확인"은 누르지 않는다. 창은 열어 둔다(사이트에 태그가 올라간 뒤 누른다).

## 2. 네이버 서치어드바이저 (사용자가 직접)

브라우저 도구로 열 수 없으므로 사용자에게 아래를 안내하고 `content` 값을 받는다(AskUserQuestion으로 "값을 적어 줄게 / 나중에" 선택지를 주고, 값은 다음 메시지로 받는다). 사용자는 값 대신 `<meta name="naver-site-verification" content="…" />` 태그 전체를 붙여 넣기도 한다. 질문에 "태그 전체를 붙여 넣어도 된다"고 적고, 받은 태그에서 `content`만 뽑는다. 값을 기다리는 동안 다른 작업은 계속한다.

> searchadvisor.naver.com → 웹마스터 도구 → 사이트 등록에 `https://<site>`를 넣고 "HTML 태그" 방식을 고르면 `<meta name="naver-site-verification" content="…">`가 나옵니다. content 값을 알려 주세요. 아직 "소유확인"은 누르지 마세요.

## 3. 인증 값 넣고 배포

1. 사이트 설정에 구글·네이버 값을 넣고 타입 검사·린트를 통과시킨다.
2. 개인정보처리방침은 바꿀 필요가 없다(인증 태그는 정보를 수집하지 않음).
3. `DEPLOY.md`에 어떤 주소로, 어느 계정으로 인증했는지 적는다.
4. 커밋하고, 사용자 승인을 받아 push한다(배포가 있어야 소유 확인이 된다). 배포가 끝날 때까지 조건 반복문으로 기다린 뒤(GitHub check-run이 `completed`가 되고, 홈 HTML에 두 메타 태그가 모두 나올 때까지: `curl -s https://<site>/ | grep -o -E '<meta name="(google|naver)-site-verification" content="[^"]+"'`) `check_search.py`로 확인한다. 태그가 실제 페이지에 나오기 전에 서치 콘솔의 "확인"을 누르면 실패한다.

## 4. 소유 확인과 사이트맵 제출

1. **구글**: 열어 둔 확인 창에서 HTML 태그의 "확인" → "소유권이 확인됨"을 본다. 창을 닫았으면 속성으로 들어가 설정 → 소유권 확인에서 다시 한다. 그다음 왼쪽 **Sitemaps** → `robots.txt`의 `Sitemap:` 줄과 같은 경로(Next.js `sitemap.xml`, Astro `sitemap-index.xml`) 제출.
   - 홈 페이지(다국어면 각 언어 홈)는 상단 URL 검사에 주소를 넣고 **색인 생성 요청**을 한다. 첫 색인이 빨라진다.
   - 제출 뒤 상태가 "가져올 수 없음"으로 나오는 경우가 많고, **2주 넘게 그대로인 경우도 있다**(2026-11 PixelUp·SongToBars 모두 11월 5일 제출 뒤 20일까지 그대로였다). 하루 안에 바뀐다고 약속하지 않는다.
   - 다시 제출하기 전에 정말 막혔는지 확인한다: `curl -sI`로 200과 `application/xml`, XML로 읽히는지와 주소 수, robots.txt의 `Sitemap:` 줄, 그리고 Googlebot으로 요청했을 때의 응답(`curl -s -o /dev/null -A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' -w "%{http_code} %{content_type}\n" <sitemap-url>`). 모두 정상이면 다시 제출하고(제출 날짜가 바뀐다), 며칠 뒤 다시 보자고 안내한다. Astro는 하위 사이트맵(`sitemap-0.xml`)도 따로 제출해 둔다.
2. **네이버**: 사용자에게 "소유확인"을 누르고, 요청 → 사이트맵 제출에 사이트맵 주소를 넣으라고 안내한다. 주소는 `robots.txt`의 `Sitemap:` 줄을 그대로 쓴다(Next.js는 `/sitemap.xml`, Astro는 `/sitemap-index.xml`이라 `/sitemap.xml`은 404). 입력란의 회색 글자는 안내 문구이므로 **전체 주소**(`https://<site>/sitemap.xml`)를 넣으라고 알려 준다. RSS가 있으면 RSS도 함께 제출하게 한다.
   - 이미 등록된 사이트맵은 다시 제출할 필요가 없다. 네이버는 등록된 사이트맵을 주기적으로 다시 읽으므로, 사이트맵 **주소가 바뀌었을 때만** 다시 제출한다. 사용자가 "다시 제출해야 해?"라고 물으면 목록에 이미 있는지 먼저 확인하게 하고, 있으면 할 일이 없다고 답한다. "이미 등록된 사이트맵"이라는 안내도 정상이다.
   - 페이지 수집 요청은 사용자가 주소를 하나씩 넣는 대신 IndexNow로 보낸다([references/indexnow.md](references/indexnow.md), `scripts/indexnow_submit.py`).
   - 사용자가 작업 도중에 "소유확인하고 사이트맵도 제출했어"처럼 알려 오면 그것을 완료로 받아 바로 `DEPLOY.md`에 날짜와 함께 적는다. 브라우저로 다시 확인하려 하지 않는다(열 수 없다).
3. **Bing**: [references/search-consoles.md](references/search-consoles.md)의 "Bing"을 따른다. 웹마스터 도구 → 사이트 추가 → **Google Search Console에서 가져오기** → 구글 계정 선택과 읽기 권한 허용(사용자 승인 필요) → 가져올 사이트 선택 → Import. 서치 콘솔에 제출한 사이트맵도 함께 넘어온다. Bing용 인증 태그(`msvalidate.01`)는 이 방식에선 필요 없다. 다만 가져온 사이트는 구글 인증에 기대므로, 구글 인증 태그를 지우거나 계정을 바꾸면 Bing 인증도 풀릴 수 있다. 오래 쓸 사이트면 Bing 설정 → 소유권 확인에서 `msvalidate.01` 값을 받아 같은 지도에 넣어 두라고 권한다(선택).

## 언어를 추가하거나 주소 구조를 바꾼 뒤

- `check_search.py`의 html lang·hreflang·사이트맵 언어 대체 링크 줄이 기대대로인지 본다(기준은 `deploy-cloudflare`의 `references/i18n.md`).
- URL 접두어 속성은 하위 경로(`/ko/` 등)를 함께 포함하므로 새로 인증할 필요는 없다. 사이트맵 **주소**가 그대로면 다시 제출하지 않아도 된다. 구글 서치 콘솔은 같은 주소를 다시 제출해도 해가 없고 다시 읽는 시점이 당겨질 수 있으므로 원하면 다시 제출한다. 네이버는 등록되어 있으면 그대로 둔다. 주소가 바뀌었으면 두 곳 모두 새 주소를 제출한다.
- 새 언어의 주소는 IndexNow로 네이버(와 Bing)에 알린다. 구글은 서치 콘솔 URL 검사에서 각 언어 홈의 색인 생성을 요청한다.
- 번역 페이지를 새로 추가했다면 빌드 결과에서 확인한다: 사이트맵에 새 주소가 있고 언어 대체 링크(`xhtml:link`)가 짝을 이루는지, 새 페이지의 `<html lang>`이 그 언어인지, 번역이 있는 글끼리만 hreflang으로 짝지어져 있는지(번역 없는 글에는 hreflang을 넣지 않는다).

## 5. 기록과 보고

- `DEPLOY.md`에 검색엔진별 상태(인증 방식, 계정, 사이트맵 제출 여부)와 "도메인을 바꾸면 다시 인증" 메모를 남긴다.
- 검색 노출은 콘텐츠 양에도 달려 있다. 페이지가 하나뿐이거나 설명 메타 태그(`description`)가 없으면 함께 짚는다.
- 사용자에게 한국어로 보고한다: 구글·Bing은 완료 여부, 네이버는 사용자가 할 일과 IndexNow로 대신 보낸 것, 사이트맵 상태와 "가져올 수 없음"의 의미, 색인까지 며칠~몇 주 걸린다는 점.
- 사용자만 할 수 있는 남은 일(네이버 사이트맵 제출 등)은 `DEPLOY.md`나 메모리에 "남은 일"로 적어 다음 대화에서 이어 간다.
- 구조화 데이터를 바꿨다면 구글 리치 결과 테스트로 실제 주소를 확인한다([references/search-consoles.md](references/search-consoles.md) "리치 결과 테스트").
- 브라우저에서 연 탭은 닫는다.
