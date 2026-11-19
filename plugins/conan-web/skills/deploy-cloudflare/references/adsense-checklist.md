# 애드센스·분석 준비 점검표

애드센스 심사는 "실제 콘텐츠가 있는, 운영자가 분명한 사이트"인지를 본다. 아래 항목은 심사에서 자주 문제가 되는 것과, 두 프로젝트에서 실제로 놓쳤던 것이다.

| 항목 | 확인 방법 | 왜 필요한가 |
|---|---|---|
| 자기 도메인 | 사이트 주소가 `*.pages.dev` 같은 남의 도메인이 아닌지 | 애드센스는 소유한 도메인 단위로 사이트를 등록한다. 공용 하위 도메인은 등록이 막히거나 승인이 어렵다(정책은 신청 전에 다시 확인) |
| 개인정보처리방침 | 페이지 존재, 푸터 링크 | 애드센스 정책상 필수. 광고 쿠키와 제3자 광고 업체 고지 문구가 있어야 한다 |
| 방침 내용과 실제 수집 일치 | GA 이벤트 목록(`track()` 호출, 위임 리스너)과 방침의 수집 항목 표 비교. 호스팅 업체(Cloudflare) 기재 | 실제와 다르면 신뢰와 법적 문제 |
| 약관, 소개, 문의 | 페이지 존재, 운영자 이름·연락처 표시 | 운영자가 분명해야 심사를 통과하기 쉽다 |
| 연락처가 비어 있을 때 | 이메일 값이 없으면 줄을 숨기는지, 빈 `mailto:`가 남지 않는지 | 빈 연락처는 심사와 신뢰에 불리 |
| 자리표시자 기본값 | 설정 파일에 `contact@….example`, `○○ 운영자` 같은 기본값이 있는지, 빌드 결과에 남았는지(`check_output.py`) | 변수를 빠뜨린 배포에 가짜 연락처가 공개됨. Cloudflare 빌드(`CF_PAGES=1`)에서 비면 실패시키거나 숨긴다 |
| HTML 사이트맵과 XML 사이트맵 | `/site-map` 같은 페이지, `sitemap.xml`(또는 `sitemap-index.xml`) | 탐색과 색인 |
| robots.txt | 전체 허용, `Sitemap:` 줄이 실제 주소 | 크롤러 차단 방지 |
| ads.txt | ID가 있으면 `google.com, pub-…, DIRECT, f08c47fec0942fa0`, 없으면 주석 한 줄. 코드만 보지 말고 실제 주소가 200인지 확인(`curl -s -o /dev/null -w "%{http_code}" <site>/ads.txt`). SongToBars(Astro)는 파일이 없어 404였다 | 심사와 승인 후 수익 손실 방지. 정적 사이트는 404를 낼 수 없으므로 주석 파일이라도 둔다 |
| 애드센스 게시자 ID를 넣는 시점 | 사이트 등록과 **심사 요청 전에** ID를 환경 변수에 넣고 다시 배포했는지. `DEPLOY.md`에 "승인 후에 넣는다"고 적혀 있으면 고친다 | 심사 중 구글이 사이트의 광고 코드와 `ads.txt`를 확인한다. 승인 뒤에 넣으면 심사가 진행되지 않는다 |
| 동의 기본값 위치 | `gtag('consent','default', …)`가 GA와 애드센스 **어느 쪽만 켜도** 들어가는지, 광고·분석 스크립트보다 **앞에** 있는지. EEA·영국·스위스는 denied | 유럽 방문자 규정. 방침에 "동의 전에는 저장하지 않는다"고 썼다면 그대로 동작해야 함 |
| 동의 기본값 내용 | 지역 외(한국 등) 기본값이 의도와 맞는지. 지역 외에서도 `ad_storage`·`ad_personalization`이 denied면 맞춤 광고가 꺼짐 | 수익 감소, "맞춤 광고를 한다"는 방침 문구와 불일치. 의도인지 사용자에게 확인 |
| 유럽 동의 메시지 | 애드센스에 사이트를 추가한 뒤 "개인정보 보호 및 메시지"에서 GDPR 메시지를 만들었는지(늦어도 승인 직후, 광고가 나가기 전) | 기본값만으로는 유럽 방문자에게 광고 쿠키를 쓸 수 없음. 방침에 동의 메시지를 언급했다면 실제로 켜야 함 |
| 광고 스크립트 조건 | 애드센스 ID가 있을 때만 `adsbygoogle.js`를 넣는지 | ID 없이 넣으면 콘솔 오류 |
| 제목과 공유 카드 | 페이지마다 `<title>`이 정확히 하나이고 `og:title`·`twitter:title`과 같은지, `og:image`·`twitter:image`(+`og:image:width`·`height`·`alt`)가 있는지, `/og.png`가 200 `image/png` 1200×630인지(`check_output.py`가 HTML 쪽을 확인) | 홈에 제목이 빠지면 검색 결과와 탭에 이름이 안 나온다. `twitter:card`가 `summary_large_image`인데 이미지가 없으면 공유 카드가 빈 틀로 나온다. 카카오톡은 미리보기를 캐시하므로, 이미지를 고친 뒤에도 옛 카드가 나오면 카카오 공유 디버거에서 캐시를 지우라고 사용자에게 알린다(에이전트는 확인할 수 없다) |
| 아이콘과 매니페스트 | `favicon.ico`(링크는 `sizes="any"`, SVG 아이콘과 함께), `apple-touch-icon.png` 180px(배경색을 채운 이미지. iOS는 투명 부분을 검게 칠함), `manifest.json`(name, short_name, start_url, display, 배경·테마색, 192·512 아이콘). 실제 주소에서 각각 200과 올바른 형식(`image/png`, `application/json`, `image/vnd.microsoft.icon`)인지 | 홈 화면 추가·북마크·크롤러에서 아이콘이 빈다. 서비스 워커나 설치 배너는 만들지 않는다(우선순위 낮음). 공유 이미지와 아이콘 PNG는 로고에서 만드는 스크립트를 저장소에 두면(예: `scripts/make-og.py`, `scripts/make-icons.py`) 다시 만들기 쉽다 |
| 구조화 데이터 | 아래 "구조화 데이터 점검" | 검색 결과 표시와 오류 경고 |
| 모바일 폭 | 375px 폭에서 모든 공개 페이지(홈, 정책, 가이드, 사이트맵)에 가로 넘침이 없는지. 브라우저를 모바일 크기로 바꾸고 `document.documentElement.scrollWidth > innerWidth`를 확인한 뒤 크기를 되돌린다 | 모바일 사용성은 심사와 검색 순위에 반영된다. PixelUp은 헤더 아이콘이 13px 넘쳤다 |
| 이미지 크기 지정 | 본문 이미지(샘플 비교 등)에 `width`·`height`(또는 `aspect-ratio`)가 있는지, 첫 화면 아래 이미지는 `loading="lazy"`인지 | 레이아웃 밀림(CLS) 방지 |
| 콘텐츠 | 가이드·설명 글이 충분한지, 직접 쓴 글인지, 샘플 이미지·폰트·모델의 라이선스. 홈도 언어마다 본문 단어 수(`document.body.innerText`), `h1`이 하나인지, `h2` 목록을 잰다. 설명 절을 더해도 도구가 첫 화면(1920×1080)에 남는지 확인한다 | 얇은 콘텐츠와 저작권 문제는 대표적인 거절 사유 |
| 없어진 기능의 설명 | 처리 방식·호스팅·엔진을 바꾼 뒤에는 모든 언어의 가이드·FAQ·약관·방침에서 더는 없는 기능(서버 업로드, 로그인, 클라우드 엔진, 보관 시간, 옛 크기 한도 등)을 검색해 고친다 | 실제와 다른 설명은 부정확한 콘텐츠다. PixelUp은 서버판에서 브라우저판으로 바꾼 뒤 가이드에 얼굴 보정·클라우드 엔진 설명이, 약관에 보관 시간 설명이 남아 있었다 |
| 오픈소스 고지 | 브라우저로 내려보내는 것 전부: `package.json`의 `dependencies`(번들에 들어가는 라이브러리), 웹폰트, 모델·런타임·데이터. 각 라이선스와 저작권자를 소개 페이지 등에 고지 | BSD·MIT·Apache는 저작권 고지 의무, MPL-2.0은 소스 위치 안내, LGPL은 고지와 교체 가능성 안내, OFL(폰트)은 저작권·라이선스 고지. 모르는 라이선스는 원문을 확인 |
| 서치 콘솔 인증 | 인증 메타 태그 값 설정, 사이트맵 제출 | 색인 확인 |
| 이미지·파일 이름 등 민감 정보 | 분석 이벤트에 이미지 내용·파일 이름이 들어가지 않는지 | 개인정보 |

## 동의 기본값 예시

GA와 애드센스 중 **하나라도** 켜져 있으면 넣고, 두 스크립트보다 **앞에** 둔다. 유럽 밖 기본값은 사이트 정책에 맞춰 정한다(아래는 유럽 밖에서 광고 쿠키를 허용하는 예. 맞춤 광고를 쓰지 않을 거라면 `denied`로 두고 방침에도 그렇게 쓴다).

```html
<!-- (GA_ID || ADSENSE_ID)일 때만, <head>에서 GA·애드센스 스크립트보다 먼저 -->
<script>
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { dataLayer.push(arguments); };
  gtag('consent', 'default', {
    analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    region: ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT',
             'NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH'],
  });
  gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted' });
</script>
<!-- 그다음에 GA(gtag.js + config), 애드센스(adsbygoogle.js) -->
```

- Next.js(App Router): 별도 컴포넌트로 만들어 레이아웃에서 `(gaId || adsenseId) &&` 조건으로 GA·애드센스보다 먼저 렌더링한다(PixelUp `components/Analytics.tsx`의 `ConsentDefaults`).
- Astro: `BaseLayout.astro`의 `<head>`에서 `{(SITE.gaId || SITE.adsenseClient) && <script is:inline>…</script>}`를 광고·분석 스크립트보다 위에 둔다.
- 일반 HTML(Vite): 모든 HTML 파일의 `<head>` 맨 앞에 넣는다.

## 점검 요령

- 오픈소스 목록은 `package.json`의 `dependencies`를 기준으로 `node_modules/<pkg>/package.json`의 `license`와 `LICENSE` 파일을 확인한다. `@fontsource*` 같은 폰트 패키지, 직접 넣은 모델·wasm 파일도 빠뜨리지 않는다. `devDependencies`는 브라우저로 나가지 않으면 고지 대상이 아니다.
- GA 이벤트 목록은 코드에서 `track(`, `gtag('event'`를 검색해 모은다. 오류 메시지 일부나 클릭 위치처럼 이벤트 값으로 보내는 내용도 방침에 적혀 있는지 본다. 방침의 표와 `DEPLOY.md`의 이벤트 표가 함께 맞는지도 본다.
- 동의 기본값은 빌드 결과에서 확인하는 것이 가장 확실하다. 세 가지 조합으로 빌드해 본다(임시 ID는 커밋하지 않는다).
  - 애드센스 ID만(`NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-0000000000000000`): `grep -c ad_storage out/index.html`이 1 이상이고, 동의 기본값이 `adsbygoogle.js`보다 앞에 있다.
  - GA ID만: 동의 기본값이 있고 `gtag/js`보다 앞에 있다.
  - 둘 다 없음: `ad_storage`가 0개다.
  배포 뒤에는 `setup-analytics`의 `check_ga.py`로 실제 페이지를 확인한다(애드센스만 켠 조합은 실제 사이트에서 시험할 수 없으므로 빌드에서 본다).
- 정책 시행일은 공개 전이라면 공개일로 맞춰도 된다. 이미 공개된 뒤 바꾸는 경우에는 방침에 적은 사전 고지 기간을 지킨다.

## 구조화 데이터 점검

- 홈: `WebApplication`(또는 `WebSite`)에 `inLanguage`를 언어별로 넣는다. FAQ가 있으면 화면 문구와 같은 데이터에서 `FAQPage`를 만든다.
- 가이드 목록: `CollectionPage` + `ItemList`(화면과 같은 순서) + `BreadcrumbList`.
- 가이드 글: `Article` + `BreadcrumbList`. `Article`의 선택 항목도 처음부터 채운다: `image`(공유 이미지), `author`·`publisher`(`Organization`과 `url`), `datePublished`·`dateModified`는 시간대가 있는 전체 시각(`2026-10-20T00:00:00+09:00`). 비워 두면 리치 결과 테스트에 "중요하지 않은 문제"가 쌓인다.
- 사용법 페이지: `TechArticle` + `BreadcrumbList`. `HowTo`는 구글이 더는 표시하지 않으므로 쓰지 않는다.
- `FAQPage`의 질문과 답은 화면에 보이는 문구와 **글자까지 같아야** 한다. 문구를 데이터 파일 하나에 두고 페이지와 JSON-LD가 함께 읽게 하고, 빌드 결과에서 JSON-LD의 질문·답이 본문에 그대로 있는지 스크립트로 확인한다. 같은 질문을 여러 페이지에 표시하지 않는다.
- FAQ 리치 결과는 2023년부터 정부·보건 사이트에만 표시된다. 일반 사이트에서 `FAQPage`가 "유효"인데 리치 결과로 안 나오는 것은 정상이고, 외부 지시서가 FAQ 데이터를 우선순위 높게 요구하면 이 점을 알린다.
- 메타나 JSON-LD를 고친 뒤에는 바꾸지 않은 페이지가 그대로인지 확인한다. 빌드 결과와 실제 사이트에서 페이지 종류별 `@type` 목록과 `<title>`을 뽑아 비교한다(SKILL.md 6단계).
- 실제 주소는 구글 리치 결과 테스트(`https://search.google.com/test/rich-results?url=<인코딩한 주소>`)로 확인한다. 자세한 사용법은 `register-search`의 `references/search-consoles.md`에 있다.
