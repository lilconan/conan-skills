# 인증 메타 태그를 사이트에 넣는 방법

모든 검색엔진 값을 `meta name → content` 지도 하나로 두고, 값이 빈 항목은 태그를 넣지 않는다. 검색엔진이 늘어도 한 줄만 추가하면 된다. 인증은 주소 단위라는 주석을 함께 단다.

## Next.js (App Router, PixelUp 기준)

```ts
// lib/site.ts
// Search-engine HTML-tag verification: meta name -> content, rendered on every page; empty values are skipped.
// Verification is per address (https://<site>); after a domain change, verify again and replace these.
siteVerification: {
  "google-site-verification": "<google content>", // Search Console (Bing imports it)
  "naver-site-verification": "<naver content>",
} as Record<string, string>,
```

```ts
// app/layout.tsx 의 metadata
verification: { other: Object.fromEntries(Object.entries(SITE.siteVerification).filter(([, v]) => v)) },
```

`metadata.verification.other`의 각 항목은 `<meta name="<key>" content="<value>">`로 모든 페이지 `<head>`에 들어간다(정적 내보내기에서도 HTML에 직접 들어감). `verification.google`을 써도 되지만 지도 하나로 두는 편이 관리가 쉽다.

## Astro (SongToBars 기준)

```js
// src/site.config.js
siteVerification: {
  'google-site-verification': '<google content>', // Search Console
  'naver-site-verification': '<naver content>', // 네이버 서치어드바이저
},
```

```astro
<!-- BaseLayout.astro <head> -->
{Object.entries(SITE.siteVerification).filter(([, v]) => v).map(([name, v]) => <meta name={name} content={v} />)}
```

## Vite / 일반 HTML

모든 HTML 파일의 `<head>`에 직접 넣거나, `vite.config.js`의 `transformIndexHtml` 훅에서 지도를 돌며 태그를 넣는다. 여러 HTML 파일이 있으면 훅 방식이 빠뜨리지 않는다.

```js
transformIndexHtml(html) {
  const tags = Object.entries(VERIFY).filter(([, v]) => v)
    .map(([name, v]) => `<meta name="${name}" content="${v}">`).join("");
  return html.replace("</head>", `${tags}</head>`);
}
```

## 확인

```bash
curl -s https://<site>/ | grep -o -E '<meta name="[a-z.0-9-]*(site-verification|msvalidate)[^>]*>'
```
