# Cloudflare Pages 캐시 헤더(`_headers`)

공식 문서: https://developers.cloudflare.com/pages/configuration/headers/

`_headers` 파일을 빌드 결과 폴더의 루트에 둔다. Next.js, Astro, Vite 모두 `public/_headers`에 두면 결과 폴더로 복사된다. 헤더는 Cloudflare에서만 적용되고 로컬 정적 서버에서는 무시된다.

## 규칙

- Pages는 기본적으로 모든 파일을 매번 재검증한다. 그래서 헤더를 안 넣어도 틀린 동작은 없지만, 큰 파일(모델, wasm)이 재방문 때마다 재검증 요청을 보낸다.
- **주소가 내용과 함께 바뀌는 파일만 `max-age=31536000, immutable`을 준다.**
  - Next.js `/_next/static/*`, Astro `/_astro/*`, Vite `/assets/*`: 파일 이름에 해시가 있다.
  - 직접 복사한 런타임: `/ort/<version>/*`처럼 버전 폴더에 둔다.
  - 버전 없는 이름의 큰 파일: 요청할 때 `?v=<sha256 앞 16자>`를 붙인다. Pages는 정적 파일의 쿼리를 무시하고 같은 파일을 주지만, 브라우저 캐시는 주소 단위라 버전이 바뀌면 새로 받는다.
- 어떤 버전을 쓸지 알려 주는 파일(manifest.json 등)은 `no-cache`로 둔다.
- 한 주소가 여러 규칙에 맞으면 헤더가 합쳐진다. 앞 규칙의 값을 지우려면 `! Header-Name` 줄을 쓴다.
- HTML 페이지는 기본값(재검증)을 그대로 둔다. 길게 캐시하면 배포 뒤에도 옛 페이지가 보인다.

## 템플릿

```
# Cloudflare Pages response headers (https://developers.cloudflare.com/pages/configuration/headers/).
# Pages revalidates every file by default; files whose URL changes with their content are cached for good.

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

# Hashed build output (Next.js: /_next/static/*, Astro: /_astro/*, Vite: /assets/*).
/_next/static/*
  Cache-Control: public, max-age=31536000, immutable

# Large files whose URL carries a version (folder or ?v=<hash>).
/<runtime>/*
  Cache-Control: public, max-age=31536000, immutable

# The manifest says which version is current, so it is always revalidated.
/<data>/manifest.json
  ! Cache-Control
  Cache-Control: no-cache
```

## 확인

- 배포 전: 결과 폴더에 `_headers`가 들어갔는지(`ls out/_headers`), 코드가 실제로 버전 붙은 주소로 요청하는지(빌드된 JS에서 버전 문자열 검색).
- 배포 후: `curl -sI https://<site>/<versioned-file> | grep -i cache-control`.
- CSP는 GA·애드센스 도메인이 많아 쉽게 깨지므로 이 단계에서는 넣지 않는다. 넣으려면 따로 시험한다.
