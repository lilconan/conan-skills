---
name: register-search
description: 배포된 정적 웹사이트(Cloudflare Pages의 Next.js·Astro·Vite 사이트 등)를 검색엔진에 등록하는 스킬. 구글 서치 콘솔과 네이버 서치어드바이저의 HTML 태그 인증 값을 사이트 설정에 넣어 배포하고, 소유 확인과 사이트맵 제출을 하고, Bing 웹마스터 도구는 서치 콘솔에서 가져온다. 사용자가 "서치 콘솔", "구글 검색 등록", "네이버 검색 등록", "서치어드바이저", "웹마스터 도구", "Bing 등록", "사이트맵 제출", "검색에 안 나와", "색인", "인증 태그", "site-verification"을 말하거나, 새 사이트를 공개한 직후 검색 노출을 준비할 때, 도메인을 바꿔 다시 인증해야 할 때는 직접 언급하지 않아도 반드시 이 스킬을 쓴다.
metadata:
  version: 0.1.0
  updated: 2026-11-05
---

# register-search: 검색엔진에 사이트 등록하기

배포된 사이트를 구글, 네이버, Bing에 등록해 검색에 노출되게 하는 순서다. 인증 값 받기 → 사이트에 넣고 배포 → 소유 확인 → 사이트맵 제출 → Bing 가져오기 → 기록으로 진행한다.
배포 자체는 `conan-web:deploy-cloudflare`, 분석 연결은 `conan-web:setup-analytics`가 맡는다.

## 기본 원칙

- **사용자에게 하는 말은 모두 한국어로 쓴다.** 진행 안내, 마무리 요약, 질문과 버튼 문구까지 전부다.
- **인증은 주소 단위다.** `https://<project>.pages.dev/`로 인증한 것은 나중에 자기 도메인으로 옮기면 다시 해야 한다. 그래서 인증 값은 한곳(사이트 설정)에 모아 두고, 어떤 주소로 인증했는지 주석과 `DEPLOY.md`에 남긴다.
- **권한을 넘기는 일은 미리 묻는다.** Bing이 구글 서치 콘솔을 읽도록 허용하는 것(OAuth)은 사용자 승인을 받고 진행한다. 허용 화면에 나온 범위(`webmasters.readonly` 등)를 사용자에게 그대로 알려 준다.
- **사용자가 직접 해야 하는 곳은 분명히 나눈다.** Claude in Chrome은 네이버 사이트(searchadvisor.naver.com)를 안전 제한으로 열지 못한다. 네이버 단계는 사용자에게 무엇을 누르고 어떤 값을 알려 달라고 할지 정확히 안내한다.
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

Chrome 도구로 열 수 없으므로 사용자에게 아래를 안내하고 `content` 값을 받는다(AskUserQuestion으로 "값을 적어 줄게 / 나중에" 선택지를 주고, 값은 다음 메시지로 받는다).

> searchadvisor.naver.com → 웹마스터 도구 → 사이트 등록에 `https://<site>`를 넣고 "HTML 태그" 방식을 고르면 `<meta name="naver-site-verification" content="…">`가 나옵니다. content 값을 알려 주세요. 아직 "소유확인"은 누르지 마세요.

## 3. 인증 값 넣고 배포

1. 사이트 설정에 구글·네이버 값을 넣고 타입 검사·린트를 통과시킨다.
2. 개인정보처리방침은 바꿀 필요가 없다(인증 태그는 정보를 수집하지 않음).
3. `DEPLOY.md`에 어떤 주소로, 어느 계정으로 인증했는지 적는다.
4. 커밋하고, 사용자 승인을 받아 push한다(배포가 있어야 소유 확인이 된다). 배포가 끝나면 `check_search.py`로 실제 페이지에 두 태그가 나오는지 확인한다.

## 4. 소유 확인과 사이트맵 제출

1. **구글**: 열어 둔 확인 창에서 HTML 태그의 "확인" → "소유권이 확인됨"을 본다. 창을 닫았으면 속성으로 들어가 설정 → 소유권 확인에서 다시 한다. 그다음 왼쪽 **Sitemaps** → `robots.txt`의 `Sitemap:` 줄과 같은 경로(Next.js `sitemap.xml`, Astro `sitemap-index.xml`) 제출.
   - 홈 페이지(다국어면 각 언어 홈)는 상단 URL 검사에 주소를 넣고 **색인 생성 요청**을 한다. 첫 색인이 빨라진다.
   - 제출 직후 상태가 "가져올 수 없음"으로 나오는 경우가 많다. 사이트맵 파일이 200·`application/xml`·올바른 XML이면 몇 시간~하루 뒤 "성공"으로 바뀌므로 사용자에게 그렇게 설명한다.
2. **네이버**: 사용자에게 "소유확인"을 누르고, 요청 → 사이트맵 제출에 사이트맵 주소를 넣으라고 안내한다. 주소는 `robots.txt`의 `Sitemap:` 줄을 그대로 쓴다(Next.js는 `/sitemap.xml`, Astro는 `/sitemap-index.xml`이라 `/sitemap.xml`은 404). RSS가 있으면 RSS 제출도 함께.
3. **Bing**: [references/search-consoles.md](references/search-consoles.md)의 "Bing"을 따른다. 웹마스터 도구 → 사이트 추가 → **Google Search Console에서 가져오기** → 구글 계정 선택과 읽기 권한 허용(사용자 승인 필요) → 가져올 사이트 선택 → Import. 서치 콘솔에 제출한 사이트맵도 함께 넘어온다. Bing용 인증 태그(`msvalidate.01`)는 이 방식에선 필요 없다. 다만 가져온 사이트는 구글 인증에 기대므로, 구글 인증 태그를 지우거나 계정을 바꾸면 Bing 인증도 풀릴 수 있다. 오래 쓸 사이트면 Bing 설정 → 소유권 확인에서 `msvalidate.01` 값을 받아 같은 지도에 넣어 두라고 권한다(선택).

## 5. 기록과 보고

- `DEPLOY.md`에 검색엔진별 상태(인증 방식, 계정, 사이트맵 제출 여부)와 "도메인을 바꾸면 다시 인증" 메모를 남긴다.
- 검색 노출은 콘텐츠 양에도 달려 있다. 페이지가 하나뿐이거나 설명 메타 태그(`description`)가 없으면 함께 짚는다.
- 사용자에게 한국어로 보고한다: 구글·Bing은 완료 여부, 네이버는 사용자가 할 일, 사이트맵 상태와 "가져올 수 없음"의 의미, 색인까지 며칠~몇 주 걸린다는 점.
- 브라우저에서 연 탭은 닫는다.
