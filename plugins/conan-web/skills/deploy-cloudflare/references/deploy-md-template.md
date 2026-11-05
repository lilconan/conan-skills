# DEPLOY.md 템플릿

프로젝트에 `DEPLOY.md`가 없을 때 이 틀로 만든다. 프로젝트마다 다른 값은 여기에 남겨 두어야 다음 배포 때 다시 조사하지 않는다. `<…>`를 채우고 해당 없는 절은 지운다.

```markdown
# 배포 안내 (Cloudflare Pages)

<서비스 이름>은 정적 사이트입니다. <처리 방식: 예) 이미지 처리는 방문자의 브라우저에서 이루어지므로> 서버, DB, 유료 API가 필요 없습니다.
Cloudflare Pages 무료 플랜으로 배포합니다(대역폭 무제한, 사이트당 파일 2만 개·파일당 25MB 한도).

- 저장소: `lilconan/<repo>` (비공개)
- 주소: `https://<project>.pages.dev` <직접 도메인이 있으면 함께>
- 연결 방식: 대시보드 Git 연결 (main에 push하면 자동 배포) / wrangler 직접 배포

## 1. 빌드 설정

| 항목 | 값 |
|---|---|
| Framework preset | <None> |
| Build command | `npm run build` |
| Build output directory | `<out 또는 dist>` |
| Environment variable `NODE_VERSION` | `<22 이상, 로컬 node -v와 같은 메이저>` |

## 2. 환경 변수

| 이름 | 값 | 설명 |
|---|---|---|
| `<SITE_URL 변수>` | `https://<project>.pages.dev` | **필수.** 사이트맵·canonical·robots에 쓰입니다 |
| `<연락처 변수>` | 문의 이메일 | 사실상 필수. 비면 기본값(가짜 주소)이 공개되지 않게 빌드가 막는지 확인 |
| `<GA 변수>` | `G-…` | 비워 두면 분석이 꺼집니다 |
| `<애드센스 변수>` | `ca-pub-…` | 승인 후에 넣습니다 |

값을 바꾸면 다시 배포해야 반영됩니다.

## 3. 캐시 헤더

`public/_headers` 참고. <오래 캐시하는 경로와 이유>

## 4. 배포 후 확인

- <핵심 기능 확인 방법>
- `/sitemap.xml`, `/robots.txt`의 주소가 실제 주소인지
- 캐시 헤더: `curl -sI https://<project>.pages.dev/<versioned-file> | grep -i cache-control`
- 서치 콘솔 등록과 사이트맵 제출

## 분석 이벤트

| 이벤트 | 언제 | 주요 값 |
|---|---|---|
| <event> | <when> | <params> |

수집 항목을 바꾸면 개인정보처리방침도 함께 고칩니다.

## 이 프로젝트만의 예외

- <예: 모델 파일을 20MiB로 나누어 25MB 한도를 맞춤>
```
