# 빌드 없는 일반 HTML 사이트 점검

기준: `package.json`도 빌드 도구도 없이 HTML·CSS·JS(ES 모듈 포함)와 이미지만으로 된 사이트. 저장소에 사이트 파일과 작업 파일(스크립트, 메모, 보고서)이 함께 있는 경우가 많다. 2026-11 포트폴리오(`2026_portfolio`, `kmb-portfolio.pages.dev`)에서 정리했다.

## 공개 범위: 화이트리스트로 dist/를 만든다

Cloudflare 문서는 프레임워크가 없으면 빌드 명령을 비우거나 `exit 0`을 쓰라고 안내한다. 이때 출력 폴더를 저장소 루트로 두면 **비공개 저장소라도 루트의 모든 파일이 사이트 주소로 열린다**(`/tools/…`, `/DEPLOY.md`, `/.claude/…`). 그래서 공개할 파일만 복사하는 스크립트를 빌드 명령으로 쓴다.

```sh
#!/bin/sh
# tools/build_site.sh: 공개할 파일만 dist/로 복사한다
set -e
cd "$(dirname "$0")/.."
rm -rf dist
mkdir dist
cp -R index.html 404.html favicon.svg main.js styles.css \
      robots.txt sitemap.xml _headers assets dist/
```

- Cloudflare 설정: Framework preset None, Build command `sh tools/build_site.sh`, Build output directory `dist`, 환경 변수 없음.
- `dist/`는 `.gitignore`에 넣는다.
- **목록에 없는 파일은 배포되지 않는다.** 새 HTML·JS 모듈·폴더를 만들면 목록에 추가해야 한다. 이 사실을 `DEPLOY.md`의 "이 프로젝트에만 해당하는 것"에 적는다. ES 모듈 하나를 빠뜨리면 그 모듈을 import하는 페이지 전체가 동작하지 않는다.
- 블랙리스트(전체 복사 후 지우기)보다 화이트리스트가 안전하다. 나중에 생기는 작업 폴더가 자동으로 공개되지 않기 때문이다.
- 로컬에서 `sh tools/build_site.sh` 뒤에 `check_output.py dist --no-ads`(수익화하지 않을 때)로 검사한다. 스크립트가 공개되면 안 되는 파일 섞임과 깨진 `href`·`src`를 잡는다.

## 404와 주소 규칙

- 루트에 `404.html`을 둔다. 없으면 Cloudflare Pages가 SPA로 판단해 없는 주소에도 `index.html`을 200으로 준다. 404.html은 어느 깊이의 주소에서든 나오므로 그 안의 CSS·아이콘·링크는 `/styles.css`처럼 `/`로 시작하는 절대 경로로 쓴다.
- Pages는 `/x.html`을 `/x`로, `/index.html`을 `/`로 이동시킨다(실측 308, 쿼리는 유지). 사이트맵·canonical·`og:url`은 처음부터 확장자 없는 주소(`/project?id=x`)로 쓴다.
- `?id=`처럼 쿼리로 내용을 바꾸는 페이지는 HTML이 하나뿐이라, 모든 주소의 `<title>`과 공유 카드가 같다. 검색 결과나 공유 미리보기를 페이지별로 다르게 하려면 페이지별 HTML을 만들어야 한다는 점을 사용자에게 알린다.

## 사이트 주소

환경 변수가 없으므로 사이트 주소는 파일에 직접 적힌다(`og:image`·`twitter:image`, `robots.txt`의 `Sitemap:`, 사이트맵 생성 스크립트). 주소가 정해지면 `grep -rn 'pages.dev' --exclude-dir=dist .`로 위치를 모아 `DEPLOY.md`에 목록으로 남긴다. 도메인을 바꿀 때 이 목록을 모두 고친다.

사이트맵은 손으로 쓰기보다 페이지 데이터에서 만드는 작은 스크립트(예: `tools/make_sitemap.py`)를 두고, 페이지를 추가할 때 다시 실행한다.

## 캐시

빌드 없는 사이트의 `assets/`는 파일 이름에 해시가 없다. Vite 예시처럼 `/assets/*`를 1년 immutable로 두면 같은 이름으로 이미지를 바꿔도 1년 동안 옛 파일이 보인다.

```
/*
  Cache-Control: no-cache

/assets/*
  ! Cache-Control
  Cache-Control: public, max-age=86400
```

HTML·JS·CSS는 매번 재검증해 ES 모듈끼리 버전이 어긋나지 않게 한다. 같은 이름으로 이미지를 바꾸면 최대 하루 동안 옛 이미지가 보일 수 있다는 점을 `DEPLOY.md`에 적는다.

## 커밋 작성자

포트폴리오처럼 나중에 공개할 수 있는 저장소는 첫 커밋 전에 `git config user.email`을 확인한다. 개인 이메일이면 저장소 로컬에 GitHub noreply 주소(`<id>+<login>@users.noreply.github.com`, 값은 `gh api user --jq '.id,.login'`)를 쓸지 사용자에게 묻는다.
