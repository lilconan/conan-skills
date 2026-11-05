# Next.js 정적 내보내기 점검

기준 프로젝트: PixelUp(`~/image_upscale`, Next.js 15 App Router).

## 설정

- `next.config.ts`에 `output: "export"`가 있어야 결과가 `out/`에 파일로 나온다. `images: { unoptimized: true }`도 필요하다(이미지 최적화 서버가 없음).
- Cloudflare 빌드에서 사이트 주소가 없으면 일부러 실패시키는 예:
  ```ts
  if (process.env.CF_PAGES === "1" && !process.env.NEXT_PUBLIC_SITE_URL) {
    throw new Error("Set NEXT_PUBLIC_SITE_URL in the Cloudflare Pages build settings.");
  }
  ```
- `NEXT_PUBLIC_*` 값은 빌드할 때 페이지에 들어간다. Cloudflare에서 값을 바꾸면 다시 배포해야 반영된다.
- 빌드 결과에 넣을 값(버전 등)은 `next.config.ts`의 `env`로 넘길 수 있다. Web Worker 코드에도 들어간다.

## 정적 내보내기에서 깨지는 것

- 서버가 필요한 기능은 빌드가 실패하거나 배포 후 동작하지 않는다: `app/api/*` 라우트 핸들러(정적이 아닌 것), 서버 액션, `cookies()`·`headers()`, 미들웨어, ISR(`revalidate`), 이미지 최적화.
- `robots.ts`, `sitemap.ts`, 그 밖의 라우트 핸들러(예: `ads.txt/route.ts`)는 `export const dynamic = "force-static"`이 있어야 파일로 만들어진다.
- 동적 경로(`[slug]`)는 `generateStaticParams`가 있어야 한다.
- `/sitemap` 페이지는 `sitemap.xml` 메타데이터 라우트와 충돌한다. HTML 사이트맵은 `/site-map` 같은 다른 이름을 쓴다.

## 경로

- 페이지는 `about.html`처럼 만들어지고, Cloudflare Pages가 `/about`으로 서비스한다. 사이트맵의 주소도 확장자 없는 형태가 맞다.
- 404는 `out/404.html`이 있으면 Cloudflare가 자동으로 쓴다.

## 개발 서버와 빌드

- `npm run build`와 `npm run dev`가 같은 `.next` 폴더를 쓴다. 빌드한 뒤에는 개발 서버를 다시 켠다.
- `tsc`가 옛 `.next/types` 때문에 오류를 내면 `.next`를 지우고 다시 실행한다.
- Turbopack이 일부 패키지에서 실패하면 webpack 빌드를 쓴다.

## 웹 워커·큰 런타임

- webpack으로 묶기 어려운 런타임(예: onnxruntime-web)은 `public/<name>/<version>/`에 복사하고 `import(/* webpackIgnore: true */ url)`로 불러온다. 경로에 버전을 넣어야 캐시 헤더를 길게 줄 수 있다([headers.md](headers.md)).
