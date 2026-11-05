# Astro 정적 사이트 점검

기준 프로젝트: SongToBars(`~/Documents/visual`, Astro, 영어·한국어 i18n).

## 설정

- `astro.config.mjs`에 `output: 'static'`이면 결과는 `dist/`다.
- `site:`가 사이트맵과 canonical의 기준 주소다. 설정 파일(`src/site.config.js` 등)에서 `process.env.SITE_URL || '<기본 주소>'`처럼 읽는 경우가 많다.
  - 기본값이 실제 배포 주소(`https://<project>.pages.dev`)라면 Cloudflare에서 변수를 비워도 문제없다.
  - 기본값이 localhost라면 Cloudflare 빌드(`CF_PAGES=1`)에서 값이 없을 때 실패하게 한다.
  - 도메인을 바꿀 때는 이 값을 바꾸고 다시 배포한다.
- `build: { format: 'file' }`이면 `about.html`이 만들어지고 Cloudflare가 `/about`으로 서비스한다. `trailingSlash: 'never'`와 함께 쓰면 주소 형태가 일관된다.
- 사이트맵은 `@astrojs/sitemap` 통합이 `sitemap-index.xml`과 `sitemap-0.xml`을 만든다. robots.txt의 `Sitemap:` 줄은 `sitemap-index.xml`을 가리켜야 한다. 404 페이지는 `filter`로 사이트맵에서 뺀다.
- i18n을 쓰면 사이트맵 통합의 `i18n` 옵션으로 hreflang 짝을 넣는다.

## 정적 파일과 라우트

- `public/`의 파일은 그대로 `dist/`에 복사된다. `_headers`와 고정 `ads.txt`는 `public/`에 둔다.
- 값에 따라 내용이 바뀌는 파일(robots.txt, ads.txt)은 `src/pages/robots.txt.ts`처럼 엔드포인트로 만들면 빌드 때 파일로 나온다.
- 애드센스 ID 같은 값이 설정 파일(`site.config.js`)에 직접 들어 있는 구조라면 Cloudflare 환경 변수 대신 코드를 고치고 다시 push하는 방식이다. 이 경우 환경 변수 표에는 `SITE_URL` 정도만 남는다.

## 분석·광고 스크립트

- 레이아웃(`BaseLayout.astro`)에서 `gaId`와 `adsenseClient`가 있을 때만 스크립트를 넣는 구조가 일반적이다.
- 동의 기본값(`gtag('consent', 'default', …)`)이 GA 조건 블록 안에만 있으면, 애드센스만 켰을 때 적용되지 않는다. GA와 애드센스 중 하나라도 켜져 있으면 들어가도록 조건을 분리한다.
- 서치 콘솔·네이버 인증 메타 태그 값도 설정 파일에 두고 값이 있을 때만 넣는다.

## 개발 서버

- `astro dev`와 `astro preview`가 같은 포트를 쓰도록 설정된 경우가 있으니 어느 쪽이 떠 있는지 확인한다.
