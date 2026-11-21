# DEPLOY.md 템플릿

프로젝트에 `DEPLOY.md`가 없을 때 이 틀로 만든다. 프로젝트마다 다른 값은 여기에 남겨 두어야 다음 배포 때 다시 조사하지 않는다. `<…>`를 채우고 해당 없는 절은 지운다. "(Node 빌드)", "(빌드 없음)", "(수익화)" 표시가 붙은 절은 그 경우에만 남긴다.

```markdown
# 배포 메모

| 항목 | 값 |
|---|---|
| 사이트 주소 | https://<project>.pages.dev <직접 도메인이 있으면 함께> |
| GitHub | `<owner>/<repo>` (비공개), 브랜치 `main` |
| Cloudflare Pages 프로젝트 | `<project>` (Git 연결, push하면 자동 배포 / wrangler 직접 배포) |
| Framework preset | <None> |
| Build command | <`npm run build` / `sh tools/build_site.sh`> |
| Build output directory | <`out` / `dist`> |
| 환경 변수 | <아래 표 / 없음> |

## 환경 변수 (Node 빌드)

| 이름 | 값 | 설명 |
|---|---|---|
| `NODE_VERSION` | `<22 이상, 로컬 node -v와 같은 메이저>` | 빌드 Node 버전 |
| `<SITE_URL 변수>` | `https://<project>.pages.dev` | **필수.** 사이트맵·canonical·robots에 쓰입니다 |
| `<연락처 변수>` | 문의 이메일 | 사실상 필수. 비면 기본값(가짜 주소)이 공개되지 않게 빌드가 막는지 확인 |
| `<GA 변수>` | `G-…` | 비워 두면 분석이 꺼집니다 |
| `<애드센스 변수>` | `ca-pub-…` | (수익화) 애드센스 심사를 요청하기 **전에** 넣고 다시 배포합니다 |

값을 바꾸면 다시 배포해야 반영됩니다.

## 이 프로젝트에만 해당하는 것

- **공개 파일 목록 (빌드 없음):** `tools/build_site.sh`가 사이트 파일만 `dist/`로 복사합니다. 새로 공개할 파일이나 폴더를 만들면 이 스크립트의 목록에 추가해야 배포에 들어갑니다. <일부러 뺀 폴더>는 공개하지 않습니다.
- **사이트 주소가 직접 적힌 곳 (빌드 없음):** <파일 목록>. 주소를 바꾸면 모두 고치고 사이트맵을 다시 만듭니다.
- **주소의 .html:** Cloudflare는 `x.html`을 `x`로 이동시킵니다. 사이트맵·canonical은 `.html` 없는 주소로 적습니다.
- **캐시:** `_headers` 참고. <오래 캐시하는 경로와 이유, 같은 이름으로 파일을 바꿀 때 주의할 점>
- <예: 모델 파일을 20MiB로 나누어 25MB 한도를 맞춤>

## 배포 후 확인

- <핵심 기능 확인 방법>
- 없는 주소가 404인지(200이면 루트 404.html이 빠진 것)
- `/sitemap.xml`, `/robots.txt`의 주소가 실제 주소인지
- 캐시 헤더: `curl -sI https://<project>.pages.dev/<file> | grep -i cache-control`

## 분석 이벤트 (GA를 쓸 때)

| 이벤트 | 언제 | 주요 값 |
|---|---|---|
| <event> | <when> | <params> |

수집 항목을 바꾸면 개인정보처리방침도 함께 고칩니다.

## 남은 일

push로 끝나지 않고 사용자가 해야 하는 일을 날짜와 함께 적습니다.

- <YYYY-MM-DD> <예: 서치 콘솔에 사이트를 등록하고 사이트맵을 제출합니다(`register-search` 스킬)>
- <예: (수익화) 애드센스 "개인정보 보호 및 메시지"에서 European regulations 메시지를 켭니다>
```
