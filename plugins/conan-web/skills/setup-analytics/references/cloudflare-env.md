# Cloudflare Pages에 측정 ID 넣고 다시 배포하기

## 어디에 넣는가

| 프레임워크 | 넣는 곳 | 예 |
|---|---|---|
| Next.js(정적 내보내기) | Cloudflare 환경 변수 | `NEXT_PUBLIC_GA_ID=G-…` |
| Astro | 설정 파일 값(`src/site.config.js`의 `gaId`)이면 코드 수정 후 push. 환경 변수를 읽는 구조면 Cloudflare 환경 변수 | `gaId: 'G-…'` |
| Vite | Cloudflare 환경 변수(`VITE_` 접두사가 있어야 클라이언트 코드에 들어감), 또는 `index.html`에 직접 | `VITE_GA_ID=G-…` |

프로젝트 코드를 먼저 읽어 어떤 이름을 쓰는지 확인한다. 이름이 틀리면 저장해도 페이지에 아무것도 들어가지 않는다.

## 대시보드에서 변수 추가 (Claude in Chrome)

- Cloudflare 로그인은 데스크톱 앱 안의 브라우저에서 사람 확인을 통과하지 못한다. Claude in Chrome(사용자의 실제 브라우저. 웨일 같은 다른 Chromium 브라우저도 됨)을 쓰고, 로그인 버튼은 사용자가 누른다. 연결이 안 될 때 안내는 `deploy-cloudflare`의 `references/cloudflare.md` "대시보드를 다룰 브라우저"에 있다.
- 대시보드는 처음에 "Loading dashboard"만 보이는 시간이 있다. 몇 초 기다렸다 다시 읽고, 탭(Deployments·Metrics·Settings)이 첫 클릭에 안 바뀌면 한 번 더 누른다.

1. `https://dash.cloudflare.com/?to=/:account/pages/view/<project>/settings/environment-variables`(계정 ID를 몰라도 됨) 또는 `https://dash.cloudflare.com/<계정ID>/pages/view/<project>/settings/production` → 오른쪽 목차 **Variables and secrets**.
   - 이미 있는 변수의 값을 바꿀 때는 표의 값 칸을 바로 고치고(세 번 눌러 전체 선택 후 입력) 아래에 뜨는 **Save**를 누른다.
2. 표 오른쪽 위 **+ Add** → 창에서 Type은 **Text**(측정 ID는 공개 값이라 Secret일 필요 없음), Variable name, Value 입력 → **Save**.
   - 창 아래 "This change will take effect on the next deployment." 문구대로 저장만으로는 사이트가 바뀌지 않는다.
3. 표에 새 변수가 보이는지 확인한다.

## 다시 배포

- 방법 1(코드 변경 없음): **Deployments** 탭 → All deployments의 맨 위(최신) 행 오른쪽 **…** → **Retry deployment**. 같은 커밋을 새 환경 변수로 다시 빌드한다. 배포 상세 화면에서 initialize → clone → build → deploy가 차례로 끝나는지 본다.
- 방법 2: 문서(`DEPLOY.md`) 수정 커밋을 push하면 자동으로 다시 배포된다. push는 사용자 승인을 받는다.
- 진행 확인은 GitHub 체크로도 할 수 있다.
  ```bash
  gh api repos/<owner>/<repo>/commits/<sha>/check-runs --jq '.check_runs[] | .status+" "+(.conclusion//"")'
  ```
- 배포가 끝나기 전에는 옛 페이지가 나온다. 사이트 확인은 10초 간격으로 몇 번 반복한다(단독 `sleep`은 막히기도 하므로 조건이 맞으면 끝나는 반복문이나 Monitor를 쓴다).
  ```bash
  for i in $(seq 1 30); do curl -s https://<site>/ | grep -q "G-XXXXXXXXXX" && break; sleep 10; done
  ```
- 측정 ID가 아니라 여러 페이지에 나오는 값(운영자 이름 등)을 바꿨다면, 그 값을 보여 주는 페이지마다(언어별 포함) 새 값이 있고 옛 값이 0개인지 확인한다.

## wrangler 직접 배포를 쓰는 프로젝트

대시보드 환경 변수가 쓰이지 않는다. 로컬 빌드 명령 앞에 변수를 붙여 빌드하고(`NEXT_PUBLIC_GA_ID=G-… npm run build`), 사용자 승인 후 `npx wrangler pages deploy <out-or-dist> --project-name <name>`.
