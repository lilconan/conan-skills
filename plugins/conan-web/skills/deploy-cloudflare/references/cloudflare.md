# Cloudflare Pages 연결

무료 플랜 한도: 대역폭 무제한, 사이트당 파일 2만 개, 파일당 25MiB, 한 달 빌드 500회. 한도는 바뀔 수 있으므로 문제가 생기면 공식 문서(https://developers.cloudflare.com/pages/platform/limits/)를 확인한다.

## A. 대시보드에서 Git 연결 (기본)

사용자가 직접 하는 일이다. 프로젝트에 맞춰 아래 내용을 채워서 안내한다.

1. https://dash.cloudflare.com 에 가입하고 로그인한다.
2. **Workers & Pages → Create → Pages → Connect to Git**을 고르고 GitHub를 연결한다. 저장소 권한은 해당 저장소 하나만 허용해도 된다.
3. **프로젝트 이름**을 정한다. 주소가 `https://<프로젝트 이름>.pages.dev`가 되고 나중에 바꿀 수 없으므로 먼저 정한다. 이미 쓰인 이름이면 뒤에 문자가 붙을 수 있으니, 만든 뒤 실제 주소를 확인하고 사이트 주소 변수와 맞춘다.
4. 빌드 설정 표를 채운다.

   | 항목 | Next.js | Astro | Vite |
   |---|---|---|---|
   | Framework preset | None | Astro (또는 None) | None |
   | Build command | `npm run build` | `npm run build` | `npm run build` |
   | Build output directory | `out` | `dist` | `dist` (`build.outDir`) |

   preset은 빌드 명령과 결과 폴더를 채워 주는 편의 기능일 뿐이라, None으로 두고 직접 넣어도 결과는 같다.

5. **Environment variables**: 프로젝트의 변수 목록으로 표를 만든다. 최소한 `NODE_VERSION`과 사이트 주소 변수가 들어간다. 각 변수에 "필수 / 비워도 됨 / 승인 후"를 표시한다.
   - `NODE_VERSION`: 지원 기간 안의 LTS 메이저 버전을 쓴다. Node 20은 2026-04-30에 지원이 끝났으므로 22 이상을 쓴다. 로컬 버전(`node -v`)과 메이저가 다르면 빌드 결과가 달라질 수 있으니 맞추는 것이 좋다. 프로젝트 문서에 20이 적혀 있으면 고칠 것으로 보고한다.
   - 공개되는 값(문의 이메일, 운영자 이름)은 "사실상 필수"로 표시한다. 빠뜨리면 기본값이 공개된다.
6. **Save and Deploy**. 첫 빌드는 몇 분 걸린다. 실패하면 빌드 로그 전체를 붙여 달라고 한다.

이후에는 main 브랜치에 push할 때마다 자동으로 다시 배포된다. 다른 브랜치는 미리보기 주소로 배포된다.

## B. wrangler 직접 배포 (선택)

사용자가 처음 한 번 로그인하면 이후 명령으로 처리할 수 있다. Git 자동 배포는 되지 않는다.

```bash
npx wrangler@latest login                     # 사용자가 직접: 브라우저에서 승인
npx wrangler@latest pages project create <name> --production-branch main
npm run build                                  # 환경 변수는 이 빌드에 직접 줘야 한다
npx wrangler@latest pages deploy <out-or-dist> --project-name <name>
```

- 이 방식은 **로컬 빌드 결과를 그대로 올린다.** 그래서 `NEXT_PUBLIC_*`, `SITE_URL` 같은 빌드 변수를 빌드 명령 앞에 직접 붙여야 한다. 예: `NEXT_PUBLIC_SITE_URL=https://<name>.pages.dev npm run build`. Cloudflare 대시보드의 변수는 이 방식에 쓰이지 않는다.
- `CF_PAGES=1` 검사로 막아 둔 설정은 로컬 빌드에서는 동작하지 않으므로, 사이트 주소를 빠뜨리지 않았는지 빌드 결과의 사이트맵으로 확인한다.
- 배포마다 승인을 받는다(외부에 공개되는 동작).
- 나중에 A로 바꾸려면 대시보드에서 새 프로젝트를 Git으로 만들어야 한다. 직접 배포로 만든 프로젝트는 Git 연결로 바꿀 수 없다.

## 직접 산 도메인

애드센스를 신청하려면 대개 자기 도메인이 필요하다(`*.pages.dev`는 Cloudflare 소유). 옮길 때 할 일:

1. 도메인을 사서(Cloudflare Registrar를 쓰면 DNS 설정이 간단하다) 프로젝트의 **Custom domains**에 추가한다. 사용자가 직접 하는 일이다.
2. 사이트 주소 변수(또는 설정 파일 값)를 새 주소로 바꾸고 다시 배포한다. 사이트맵·canonical·robots가 새 주소로 바뀌었는지 확인한다.
3. `*.pages.dev`로 들어온 방문을 새 도메인으로 301 리디렉트한다. `_redirects`는 경로만 다루므로, Cloudflare 대시보드의 **Bulk Redirects**로 `<project>.pages.dev` → 새 도메인 규칙을 만든다.
4. 검색엔진 인증은 주소 단위라 서치 콘솔, 네이버 서치어드바이저, Bing에서 새 주소로 다시 인증받고 인증 값을 바꾼다. 사이트맵도 다시 제출한다.
5. 애드센스에는 새 도메인으로 신청한다.
