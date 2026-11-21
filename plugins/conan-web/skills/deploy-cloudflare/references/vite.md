# Vite 정적 사이트 점검

기준: 프레임워크 없이 `index.html`과 `vite build`로 만드는 작은 도구 사이트. `package.json`도 빌드 도구도 없는 일반 HTML 사이트는 [plain-html.md](plain-html.md)를 본다.

## 설정

- 결과 폴더는 `vite.config.*`의 `build.outDir`이며 기본값은 `dist/`다. `dist/`는 `.gitignore`에 넣는다(Cloudflare가 소스에서 다시 빌드한다).
- 여러 페이지(소개, 개인정보처리방침 등)가 필요하면 `build.rolldownOptions.input`(Vite 8 이상. 7 이하는 `build.rollupOptions.input`)에 HTML 파일을 모두 넣어야 결과에 포함된다. Vite 8에서도 옛 이름이 당분간 동작하지만 deprecated다. 빠뜨린 페이지는 배포 후 404가 된다.
- `public/`의 파일은 그대로 결과 폴더 루트로 복사된다. 모델·데이터·`_headers`·`robots.txt`·고정 `ads.txt`는 `public/`에 둔다. **결과 폴더에만 있는 파일은 Cloudflare 빌드에서 사라진다.**
- 소스의 `index.html`이 `<script type="module" src="/main.js">`처럼 소스 파일을 직접 가리키는 것은 정상이다. 빌드 결과의 `index.html`은 해시가 붙은 `/assets/*.js`를 가리켜야 한다. 결과 폴더의 `index.html`이 소스와 똑같다면 빌드하지 않고 손으로 복사한 것이니 다시 빌드한다.

## 사이트 주소, 사이트맵, robots

- Vite는 사이트맵을 만들어 주지 않는다. 사이트 주소를 환경 변수(`VITE_SITE_URL` 또는 `SITE_URL`)로 받아 빌드 때 `sitemap.xml`과 `robots.txt`를 만드는 작은 스크립트나 플러그인(예: `vite-plugin-sitemap`)을 쓴다. 주소를 손으로 적은 사이트맵은 localhost가 남기 쉽다.
- 예: 빌드 때 `sitemap.xml`과 `robots.txt`를 만드는 플러그인. 페이지 목록(`PAGES`)은 `rolldownOptions.input`(7 이하는 `rollupOptions.input`)과 맞춘다. 빌드한 뒤 `dist/sitemap.xml`·`robots.txt`가 실제로 생겼는지 확인한다.
  ```js
  // vite.config.js
  const SITE_URL = (process.env.SITE_URL || "http://localhost:5173").replace(/\/$/, "");
  if (process.env.CF_PAGES === "1" && !process.env.SITE_URL) throw new Error("Set SITE_URL in Cloudflare Pages.");
  const PAGES = ["/", "/about", "/privacy", "/terms", "/contact"];

  const seoFiles = {
    name: "seo-files",
    generateBundle() {
      const urls = PAGES.map((p) => `<url><loc>${SITE_URL}${p === "/" ? "/" : p}</loc></url>`).join("");
      this.emitFile({ type: "asset", fileName: "sitemap.xml",
        source: `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>` });
      this.emitFile({ type: "asset", fileName: "robots.txt", source: `User-agent: *\nAllow: /\nSitemap: ${SITE_URL}/sitemap.xml\n` });
    },
  };

  export default { plugins: [seoFiles], build: { outDir: "dist" } };
  ```
  이렇게 만들면 `public/`에 사이트맵을 손으로 두지 않는다(두 군데에 있으면 어느 쪽이 쓰였는지 헷갈린다).
- 클라이언트 코드에서 쓰는 환경 변수는 `VITE_` 접두사가 있어야 `import.meta.env`로 들어간다.
- Cloudflare 빌드에서 사이트 주소가 없으면 실패하게 하려면 `vite.config.*` 맨 위에서 `process.env.CF_PAGES === "1"`이고 변수가 없을 때 `throw`한다.

## 분석·광고 스크립트

- `index.html`에 GA·애드센스 코드를 직접 넣는 경우가 많다. 그러면 모든 페이지(HTML 파일마다)에 같은 코드가 들어가야 하고, 동의 기본값이 GA 코드보다 앞에 있어야 한다. 페이지가 여러 개면 공통 부분을 Vite의 HTML 변환(`transformIndexHtml`)이나 빌드 스크립트로 넣어 빠뜨리지 않게 한다.
- 측정 ID가 `G-TEST…`, `G-XXXX`처럼 자리표시자로 보이면 실제 값을 확인한다.

## 캐시

- 빌드 결과의 `/assets/*`는 파일 이름에 해시가 붙으므로 `_headers`에서 1년 immutable로 캐시해도 된다. `public/`에서 복사한 큰 파일은 이름에 버전이 없으므로 [headers.md](headers.md)의 방법으로 주소에 버전을 넣는다.
