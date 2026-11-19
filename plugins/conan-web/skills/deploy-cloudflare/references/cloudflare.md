# Cloudflare Pages 연결

무료 플랜 한도: 대역폭 무제한, 사이트당 파일 2만 개, 파일당 25MiB, 한 달 빌드 500회. 한도는 바뀔 수 있으므로 문제가 생기면 공식 문서(https://developers.cloudflare.com/pages/platform/limits/)를 확인한다.

## 대시보드를 다룰 브라우저

- **Cloudflare 로그인은 데스크톱 앱 안의 브라우저(Claude_Browser 패널)에서 사람 확인을 통과하지 못한다.** 2026-11 PixelUp에서 "There was a problem with verification. Please reload and try again."이 반복됐다. 대시보드 작업은 Claude in Chrome(사용자의 실제 브라우저에 설치한 확장 프로그램)으로 한다.
- Claude in Chrome은 Chrome이 아닌 Chromium 브라우저(예: 네이버 웨일)에도 설치해 쓸 수 있다. 연결이 안 되면(`tabs_context_mcp`가 "not connected", `list_connected_browsers`가 `[]`) 두 번 시도한 뒤 멈추고 사용자에게 안내한다: 그 브라우저의 Claude 아이콘을 눌러 **이 앱과 같은 계정으로 로그인**했는지, 다른 대화에 연결되어 있지 않은지 확인하고 다시 연결하게 한다. 연결되면 `list_connected_browsers`에 브라우저가 나온다.
- 로그인 화면에서 비밀번호가 자동 입력되어 있어도 Sign in은 사용자가 누른다.
- 대시보드는 처음 열 때 "Loading dashboard"만 보이는 시간이 있다. 몇 초 기다린 뒤 화면을 다시 읽고, 탭이 첫 클릭에 안 바뀌면 한 번 더 누른다.

## 환경 변수를 바꾸고 다시 배포하기

1. `https://dash.cloudflare.com/?to=/:account/pages/view/<project>/settings/environment-variables`로 바로 간다(`:account` 자리는 로그인한 계정으로 자동으로 바뀐다).
2. **Variables and secrets** 표에서 값 칸을 눌러 바꾼다(아래로 스크롤해야 보인다). 값 칸을 세 번 누르고 전체 선택한 뒤 입력하면 옛 값이 섞이지 않는다. 아래에 뜨는 **Save**를 누른다.
3. 빌드 때 들어가는 값이므로 **Deployments → 최신 Production 배포의 "…" → Retry deployment**로 다시 배포한다.
4. 배포가 끝나면 그 값을 보여 주는 모든 페이지(언어별 포함)에서 새 값이 있고 옛 값이 0개인지 확인한다. 기다리는 방법은 SKILL.md 6단계 "배포 기다리기"를 따른다.

## A. 대시보드에서 Git 연결 (기본)

Cloudflare 가입과 GitHub 연결 권한 허용(OAuth)은 사용자가 직접 해야 하므로, 프로젝트를 처음 연결하는 이 과정은 사용자에게 맡기고 아래 내용을 채워서 안내한다. 연결된 뒤의 설정 변경(환경 변수, 다시 배포)은 사용자가 로그인한 Claude in Chrome으로 대신할 수 있다.

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

5. **Environment variables**: 프로젝트의 변수 목록으로 표를 만든다. 최소한 `NODE_VERSION`과 사이트 주소 변수가 들어간다. 각 변수에 "필수 / 비워도 됨 / 애드센스 심사 요청 전"을 표시한다.
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
5. GA 웹 스트림 주소와 홍보용 UTM 링크 표(`docs/marketing/utm-links.md`)의 주소를 새 도메인으로 바꾼다. IndexNow 키 파일을 쓰고 있었다면 새 도메인에서도 열리는지 확인한다.
6. 애드센스에는 새 도메인으로 신청한다. 순서를 지키는 것이 중요하다: 승인 뒤에 도메인을 바꾸면 새 도메인을 다시 등록하고 심사받아야 한다.

## 애드센스 신청 순서

사용자가 "애드센스 어떻게 신청해?"라고 물으면 아래 순서를 안내한다.

1. 자기 도메인 연결(위 "직접 산 도메인" 1~5). Cloudflare Registrar로 사면 같은 계정에서 Pages에 바로 연결할 수 있다.
2. 애드센스 가입과 약관 동의: 사용자가 직접 한다.
3. 발급받은 게시자 ID(`ca-pub-…`)를 환경 변수에 넣고 다시 배포한다. `ads.txt`와 광고 스크립트가 실제 주소에 나오는지 확인한다. **심사를 요청하기 전에** 해야 한다.
4. 애드센스에서 사이트 확인 → 심사 요청. 심사는 며칠에서 2~4주 걸린다.
5. 애드센스에 사이트를 추가한 뒤 "개인정보 보호 및 메시지"에서 유럽(GDPR) 동의 메시지를 만든다. 늦어도 승인 직후, 광고가 나가기 전에는 켜져 있어야 한다.
6. 승인 뒤: 자동 광고 켜기. 수익이 약 10달러가 되면 오는 PIN 우편, 세금 정보(W-8BEN), 은행 계좌 입력은 모두 사용자만 할 수 있다. 지급은 100달러부터다.
