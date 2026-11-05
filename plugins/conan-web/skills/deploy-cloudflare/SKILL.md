---
name: deploy-cloudflare
description: 브라우저에서 처리하는 정적 웹 서비스(Next.js 정적 내보내기, Astro 등)를 GitHub 비공개 저장소와 Cloudflare Pages로 배포하고, 배포 전후를 점검하는 스킬. 배포 전 점검(정적 빌드, 파일 수·25MB 한도, 사이트 주소 환경 변수), 애드센스·GA4 준비(정책 페이지, robots·sitemap·ads.txt, 동의 기본값), 캐시 헤더(_headers), GitHub push, Cloudflare 연결(대시보드 Git 연결 또는 wrangler), 배포 후 확인(실제 주소 응답, 헤더, 서치 콘솔)까지 다룬다. 사용자가 "배포", "배포 점검", "출시", "Cloudflare", "pages.dev", "사이트 올리기", "애드센스 신청 전 점검", "_headers", "wrangler"를 말하거나, 새 정적 사이트를 공개하려 할 때, 배포 후 사이트가 제대로 뜨는지 확인하려 할 때는 직접 언급하지 않아도 반드시 이 스킬을 쓴다.
metadata:
  version: 0.1.0
  updated: 2026-11-05
---

# deploy-cloudflare: 정적 웹 서비스 배포와 점검

서버 없이 브라우저에서 동작하는 정적 사이트를 **GitHub(비공개) → Cloudflare Pages**로 내보내는 과정이다.
대상 프로젝트는 대개 애드센스 수익화를 준비하는 콘텐츠 사이트다(예: PixelUp은 Next.js, SongToBars는 Astro).
매번 같은 단계를 처음부터 떠올리다 보면 동의 기본값, 캐시 헤더, 25MB 한도처럼 한 번씩 놓친 항목이 다시 빠진다. 이 스킬은 그런 누락을 막기 위한 점검표이자 진행 순서다.

## 기본 원칙

- **사용자에게 하는 말은 모두 한국어로 쓴다.** 짧은 진행 안내도 마찬가지다. 사용자가 한국어 사용자이고, 영어가 섞이면 크게 불편해한다.
- **되돌리기 어려운 일은 매번 확인한다.** GitHub 저장소 만들기, push, 태그 push, `wrangler pages deploy`는 실행 전에 무엇을 어디로 보내는지 말하고 승인을 받는다. 한 번 받은 승인을 다음 push에 쓰지 않는다.
- **사용자만 할 수 있는 일은 분명히 나눈다.** 가입, 로그인(`wrangler login` 포함), 대시보드 조작, 비밀값 입력은 사용자가 한다. 대신 무엇을 어디에 넣는지 표로 정리해 준다.
- **비밀값은 저장소에 넣지 않는다.** GA 측정 ID나 애드센스 ID는 공개되는 값이라 코드에 있어도 되지만, API 토큰·계정 키는 절대 커밋하지 않는다.
- **이미 확인한 것은 다시 지적하지 않는다.** 프로젝트에 `DEPLOY.md`나 체크리스트가 있으면 먼저 읽고, 이미 해결된 항목은 "확인함"으로만 짧게 적는다. 실제로 남은 일이 묻히지 않게 하려는 것이다.

## 진행 순서

사용자가 요청한 범위만 진행한다. "배포 점검해 줘"면 1~3단계를 점검해 보고하고, "배포해 줘"면 끝까지 가되 4·5단계에서 승인을 받는다. "배포 끝났어, 확인해 줘"면 6단계만 한다.

### 0. 프로젝트 파악

1. 프레임워크와 빌드 결과 폴더를 확인한다.
   - Next.js: `next.config.*`에 `output: "export"`가 있으면 결과는 `out/`이다. 자세한 점검은 [references/nextjs.md](references/nextjs.md)를 읽는다.
   - Astro: `astro.config.*`에서 `output: 'static'`을 확인하며 결과는 `dist/`다. [references/astro.md](references/astro.md)를 읽는다.
   - Vite(일반 HTML·JS 사이트): `vite.config.*`의 `build.outDir`(기본 `dist/`)를 확인한다. 사이트맵·robots를 직접 만들어야 하는 경우가 많다. [references/vite.md](references/vite.md)를 읽는다.
   - 그 밖의 프레임워크: 정적 결과 폴더와 사이트 주소를 넣는 방법만 찾으면 같은 순서로 진행할 수 있다.
2. 프로젝트의 `DEPLOY.md`, `CLAUDE.md`, `README.md`에서 배포 관련 내용(프로젝트 이름, 주소, 환경 변수, 예외 사항)을 읽는다. `DEPLOY.md`가 없으면 마지막에 [references/deploy-md-template.md](references/deploy-md-template.md)로 만들어 주겠다고 제안한다. 프로젝트마다 다른 값은 스킬이 아니라 그 프로젝트의 `DEPLOY.md`에 남겨야 다음 배포 때 다시 조사하지 않아도 된다.
3. `git remote -v`와 `gh repo view --json visibility`로 저장소 연결 상태를 확인한다.

### 1. 배포 전 점검 (빌드와 Cloudflare 한도)

1. 빌드를 실행한다(`npm run build`). 개발 서버가 같은 빌드 폴더를 쓰는 프레임워크(Next.js의 `.next`)는 빌드 뒤 개발 서버를 다시 켜야 한다고 알려 준다.
2. 결과 폴더를 [scripts/check_output.py](scripts/check_output.py)로 검사한다.
   ```bash
   python3 <skill-dir>/scripts/check_output.py <out-or-dist> [--site-url https://<project>.pages.dev]
   ```
   이 스크립트는 Cloudflare Pages 무료 한도(파일 2만 개, 파일당 25MiB), `robots.txt`·`sitemap*.xml`·`ads.txt`·`_headers`·404 페이지 유무, 사이트맵과 robots에 `localhost`가 남았는지, 페이지에 자리표시자 값(`@….example` 이메일, `example.com`, `ca-pub-XXXX`, `G-XXXX`)이 남았는지를 확인해 표로 출력한다.
   로컬 빌드는 보통 사이트 주소 변수 없이 돌기 때문에 localhost가 나오는 것이 정상일 수 있다. 실제 배포와 같은 결과를 보려면 주소 변수를 붙여 빌드한다(예: `NEXT_PUBLIC_SITE_URL=https://<project>.pages.dev npm run build`). 그렇게 하지 않았다면 localhost 항목은 "Cloudflare에 변수를 넣으면 해결됨"으로 보고하고, 변수 없이 빌드가 실패하게 되어 있는지(3번)를 함께 확인한다.
3. **사이트 주소와 공개 값:** 사이트맵·canonical·robots가 쓰는 주소를 환경 변수로 받는지 확인한다. 기본값이 `localhost`이면 Cloudflare 빌드에서 그 변수가 비었을 때 빌드가 실패하게 해 두는 것이 안전하다. 실패하지 않으면 검색엔진에 localhost 주소가 제출된다. Cloudflare Pages 빌드에는 `CF_PAGES=1`이 설정되므로 이것으로 구분할 수 있다.
   문의 이메일, 운영자 이름처럼 **페이지에 공개되는 값도 같은 기준으로 본다.** 설정 파일에 `contact@<name>.example`, `<서비스> 운영자` 같은 기본값이 있으면, 변수를 빠뜨린 배포에 가짜 연락처가 그대로 나간다. 그런 값도 `CF_PAGES=1`에서 비어 있으면 빌드를 실패시키거나, 값이 없을 때 그 줄을 숨기도록 권한다. 가짜 연락처는 애드센스 심사와 개인정보 보호법 모두에 불리하다.
4. **결과 폴더에만 있는 파일:** Cloudflare Git 연결은 저장소의 소스에서 새로 빌드한다. 그래서 결과 폴더(`dist/`, `out/`)에만 있고 소스(`public/` 등)나 빌드 과정에서 만들어지지 않는 파일은 배포에서 사라진다. 결과 폴더를 손으로 고친 흔적이 있거나, 결과 폴더의 정적 파일이 `public/`에 없으면 고칠 것으로 보고한다. 결과 폴더는 `.gitignore`에 넣는다.
5. **25MB를 넘는 파일:** 모델이나 큰 데이터는 20MiB 단위로 나누고, 나눈 목록과 SHA-256을 manifest에 적은 뒤 브라우저에서 이어 붙이는 방식으로 해결한다(PixelUp의 `scripts/onnx/build_models.py`와 워커의 `loadModelBytes` 참고).

### 2. 애드센스·분석 준비 점검

[references/adsense-checklist.md](references/adsense-checklist.md)의 표를 따라 점검한다. 핵심만 요약하면 아래와 같다.

- 정책 페이지(개인정보처리방침, 약관, 소개, 문의)와 HTML 사이트맵이 있고 푸터에서 연결되는지
- 개인정보처리방침이 실제로 수집하는 항목(GA 이벤트, 호스팅 업체, 광고 쿠키)과 맞는지
- **사이트 주소가 자기 도메인인지.** 애드센스는 소유한 도메인 단위로 사이트를 등록한다. `*.pages.dev`는 Cloudflare 소유 주소라 등록이 막히거나 승인이 어려울 가능성이 크다(정책은 바뀔 수 있으니 "확인 필요"로 보고하고, 신청 전에 도메인을 사서 연결하도록 권한다). 도메인을 옮길 때 할 일은 [references/cloudflare.md](references/cloudflare.md)의 "직접 산 도메인"에 있다.
- **동의 기본값이 GA와 애드센스 어느 쪽만 켜도 적용되는지.** 동의 코드가 GA 스크립트 안에만 있으면, 애드센스만 켠 배포에서는 유럽 방문자에게 동의 없이 광고 쿠키가 저장된다. 두 프로젝트 모두 처음에 이 문제가 있었다. 동의 기본값은 광고 스크립트보다 **앞에** 나와야 한다. 프레임워크별로 넣는 위치와 코드는 [references/adsense-checklist.md](references/adsense-checklist.md)의 "동의 기본값 예시"를 따른다.
- **동의 기본값의 내용이 의도와 맞는지.** 유럽·영국·스위스 밖에서도 `ad_storage`·`ad_personalization`을 denied로 두면, 한국 방문자에게도 맞춤 광고가 꺼져 수익이 줄고, 맞춤 광고를 한다고 쓴 개인정보처리방침과도 어긋난다. 의도인지 사용자에게 묻는다.
- `ads.txt`: 애드센스 ID가 없을 때 무엇을 내보내는지. 정적 사이트는 404를 낼 수 없으므로 주석 한 줄만 두는 방식이 무난하다.
- **오픈소스 라이선스 고지:** 모델만이 아니라 브라우저로 내려보내는 것 전부가 대상이다. `package.json`의 `dependencies`(번들에 들어가는 라이브러리), 웹폰트(대개 OFL), 모델·데이터 파일을 모아 라이선스를 확인한다. BSD·MIT·Apache는 저작권 고지, MPL은 소스 위치 안내, LGPL은 고지와 교체 가능성 안내가 필요하다. 콘텐츠(샘플 이미지, 글)의 출처도 기록이 있는지 본다.

### 3. 캐시 헤더

[references/headers.md](references/headers.md)를 읽고 `_headers`를 만들거나 점검한다.

핵심 규칙: **주소에 버전이나 해시가 들어 있는 파일만 오래 캐시한다.** 파일 이름에 버전이 없는 큰 파일(모델, 런타임)을 그대로 1년 캐시하면, 갱신한 뒤에도 방문자 브라우저에 옛 파일이 남아 오류가 난다. 그런 파일은 경로나 쿼리에 버전을 넣은 뒤 캐시한다. 지금 쓸 버전을 알려 주는 manifest류는 `no-cache`로 둔다.

1~3단계를 마치면 결과를 아래 형식으로 보고한다.

```
## 배포 점검 결과
| 구분 | 항목 | 상태 | 내용 |
|---|---|---|---|
| 빌드 | 정적 빌드 | 통과 | out/ 412개 파일 |
| 한도 | 파일당 25MB | 통과 | 가장 큰 파일 21.7MB (ort wasm) |
| 애드센스 | 동의 기본값 | 고칠 것 | GA 블록 안에만 있음 → 애드센스만 켜면 적용 안 됨 |
...
### 고칠 것 (중요한 순서)
### 사용자가 직접 할 일
```

상태는 `통과`, `고칠 것`, `확인 필요`(직접 볼 수 없는 것), `해당 없음` 중 하나로 쓴다. 고칠 것이 있으면 바로 고치지 말고, 고칠지 먼저 묻는다(사용자가 "고쳐 줘"까지 요청했다면 고친다).

### 4. GitHub

1. 원격 저장소가 없으면 `gh repo create lilconan/<name> --private --source . --push`를 제안하고 승인 후 실행한다. 정책상 비공개가 기본이다. Cloudflare Pages는 비공개 저장소도 연결할 수 있다.
2. 있으면 올라가지 않은 커밋 수(`git status -sb`)를 알려 주고 push 승인을 받는다.
3. push 후 `git status -sb`로 원격과 맞는지 확인하고, 큰 파일이 실제로 올라갔는지 필요하면 `gh api repos/<owner>/<repo>/contents/<path>`로 확인한다.

### 5. Cloudflare 연결

[references/cloudflare.md](references/cloudflare.md)를 읽는다. 방식은 두 가지다.

- **A. 대시보드에서 Git 연결(기본):** 이후 push할 때마다 자동으로 다시 배포된다. 사용자가 대시보드에서 직접 연결해야 하므로, 프로젝트에 맞춘 빌드 설정 표와 환경 변수 표를 만들어 준다.
- **B. wrangler 직접 배포(선택):** 사용자가 `npx wrangler login`을 한 번 직접 하면, 프로젝트 생성과 배포를 명령으로 처리할 수 있다. push만으로는 자동 배포되지 않는다는 점을 알려 준다.

어느 쪽이 나은지 모르겠다는 사용자에게는 A를 권한다. 처음 한 번만 대시보드를 쓰면 이후에는 push만 하면 되기 때문이다.

### 6. 배포 후 확인

사용자가 주소를 알려 주면 아래를 확인하고 1~3단계와 같은 표로 보고한다.

1. 주요 페이지(홈, 정책 페이지, 가이드 하나)가 200이고, 없는 주소가 404인지: `curl -s -o /dev/null -w "%{http_code}" <url>`
2. 캐시 헤더가 의도대로인지: `curl -sI <url>/<versioned-file> | grep -i cache-control`
3. `/sitemap.xml`과 `/robots.txt`의 주소가 실제 주소인지
4. 핵심 기능을 브라우저에서 한 번 실행했는지. 직접 할 수 없으면 사용자에게 무엇을 눌러 보면 되는지 알려 준다.
5. 서치 콘솔(필요하면 네이버 서치어드바이저)에 사이트를 등록하고 사이트맵을 제출하도록 안내한다. 인증 메타 태그 값은 사이트 설정 파일에 넣는 방식을 권한다.

마지막으로, 이번 배포에서 프로젝트에만 해당하는 사실(프로젝트 이름, 주소, 예외)을 `DEPLOY.md`에 남길지 묻는다.
