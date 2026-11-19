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
- `trailingSlash: true`는 켜지 않는다. 켜면 페이지가 `about/index.html`이 되어 `/about/`으로 서비스되는데, 사이트맵·canonical은 확장자 없는 `/about`을 쓰므로 주소가 어긋난다. 기본값이면 `about.html`이 되고 Cloudflare Pages가 `/about`으로 서비스한다.
- `package.json`의 `start`(`next start`) 스크립트와 서버 전용 패키지는 정적 내보내기에서 쓸 수 없으므로 지운다.

## 정적 내보내기에서 깨지는 것

- 서버가 필요한 기능은 빌드가 실패하거나 배포 후 동작하지 않는다: `app/api/*` 라우트 핸들러(정적이 아닌 것), 서버 액션, `cookies()`·`headers()`, 미들웨어, ISR(`revalidate`), 이미지 최적화.
- `robots.ts`, `sitemap.ts`, 그 밖의 라우트 핸들러(예: `ads.txt/route.ts`)는 `export const dynamic = "force-static"`이 있어야 파일로 만들어진다.
- 동적 경로(`[slug]`)는 `generateStaticParams`가 있어야 한다.
- 빌드 출력의 경로 표에서 `ƒ`(Dynamic) 표시가 하나라도 있으면 정적 내보내기가 되지 않는 서버 기능이 남아 있다는 뜻이다. Cloudflare Pages(정적)로 진행하지 말고 사용자에게 알린다(SKILL.md 0단계).
- `/sitemap` 페이지는 `sitemap.xml` 메타데이터 라우트와 충돌한다. HTML 사이트맵은 `/site-map` 같은 다른 이름을 쓴다.

## 경로

- 페이지는 `about.html`처럼 만들어지고, Cloudflare Pages가 `/about`으로 서비스한다. 사이트맵의 주소도 확장자 없는 형태가 맞다.
- 404는 `out/404.html`이 있으면 Cloudflare가 자동으로 쓴다.

## 제목과 공유 메타

- 루트 레이아웃의 `metadata.title.template`(`"%s | 브랜드"`)은 **같은 경로 단위의 페이지(대개 홈)에는 적용되지 않는다.** PixelUp에서는 홈 두 곳(`/`, `/ko`)에 `<title>`이 아예 없었고, `og:title`은 브랜드 이름만 나왔다. 메타데이터 도우미 함수에서 모든 페이지에 완성된 제목(`"페이지 | 브랜드"`)을 직접 넣는 쪽이 안전하다.
- `openGraph`와 `twitter`의 `title`·`images`를 페이지마다 같은 값으로 채운다. 페이지 메타데이터에서 `openGraph`를 덮어쓰면 레이아웃의 `images`가 함께 사라지므로, 도우미 함수가 이미지까지 매번 넣게 한다.
- 빌드 뒤 `check_output.py`가 모든 HTML의 `<title>` 개수와 `og:title`·`twitter:title`·`og:image`·`twitter:image`를 확인한다.

## 개발 서버와 빌드

- `npm run build`와 `npm run dev`가 같은 `.next` 폴더를 쓴다. 빌드한 뒤에는 개발 서버를 다시 켠다. 다시 켠 개발 서버가 일부 페이지를 옛 렌더링으로 내보낼 수 있으니, 바뀐 내용은 브라우저보다 `curl -s localhost:3000/<path> | grep -c <새 문구>`로 먼저 확인한다.
- `tsc`가 옛 `.next/types` 때문에 오류를 내면 `.next`를 지우고 다시 실행한다.
- `.next`나 `out`을 지우기 전에 **개발 서버(미리보기 포함)를 먼저 멈춘다.** 서버가 계속 `.next`에 쓰고 있으면 `rm -rf .next`가 "Directory not empty"로 반쯤만 지워진다. 멈춘 뒤 1초쯤 기다려 지우고, `ls .next`로 비었는지 확인한다.
- 빌드 결과를 검사하기 전에 빌드 종료 코드를 출력하고 `out/`에 파일이 있는지 확인한다. 빌드 출력을 `>/dev/null`로 버린 채 실패하면 `out/`이 비고, 그 위에서 돈 검사 스크립트가 "페이지 0개, 문제 0개"로 통과처럼 보인다.
- **Cloudflare와 같은 조건으로 시험 빌드하기:** Next.js는 `.env.local`을 자동으로 읽기 때문에, 로컬 빌드는 Cloudflare에 넣지 않은 변수까지 채운 채 성공할 수 있다. 시험 빌드 전에 `.env.local`을 작업 폴더 밖(스크래치 폴더)으로 옮기고 `.next`를 지운 뒤, Cloudflare에 넣을 변수만 붙여 빌드한다(예: `NEXT_PUBLIC_SITE_URL=https://<project>.pages.dev NEXT_PUBLIC_GA_ID=G-TEST000000 npm run build`). 끝나면 `.env.local`을 제자리로 돌려놓는다.
- Turbopack이 일부 패키지에서 실패하면 webpack 빌드를 쓴다.

## 웹 워커·큰 런타임

- webpack으로 묶기 어려운 런타임(예: onnxruntime-web)은 `public/<name>/<version>/`에 복사하고 `import(/* webpackIgnore: true */ url)`로 불러온다. 경로에 버전을 넣어야 캐시 헤더를 길게 줄 수 있다([headers.md](headers.md)).
- 이렇게 복사한 파일은 대개 `.gitignore`에 들어 있다. 그러면 Cloudflare Git 빌드에서도 만들어지도록 복사 스크립트를 `predev`와 **`prebuild`** npm 훅에서 돌려야 한다(PixelUp `scripts/copy-ort.mjs`). 빌드 뒤 `out/<name>/`에 파일이 있는지, 25MiB를 넘는 파일이 없는지(`find out -size +24M`) 확인한다.
- 복사한 압축 런타임은 ESLint 대상에서 뺀다(`eslint.config.mjs`의 ignores에 `public/<name>/**`). 빼지 않으면 `npm run lint`가 남의 파일에서 수백 개의 문제를 보고한다.
