# IndexNow로 수집 요청 보내기

기준: 2026-11-20 PixelUp(Next.js)과 SongToBars(Astro)의 한국어 페이지 27개를 네이버에 보낸 과정.

## 왜 쓰는가

네이버 서치어드바이저(searchadvisor.naver.com)는 앱 안의 브라우저와 Claude in Chrome 모두에서 안전 제한으로 열리지 않는다. 그래서 웹 콘솔의 "웹 페이지 수집" 요청은 사용자가 주소를 하나씩 넣어야 한다. IndexNow는 네이버가 공식으로 지원하는 수집 요청 방식이라, 사이트에 키 파일을 하나 두면 에이전트가 명령으로 여러 주소를 한 번에 알릴 수 있다. 같은 요청이 Bing 등 IndexNow에 참여한 다른 검색엔진에도 전달된다.

IndexNow로 대신할 수 없는 것: 네이버 사이트 등록과 소유 확인, 사이트맵 제출. 이것들은 여전히 사용자가 웹 콘솔에서 한다.

## 순서

1. **사용자에게 묻는다.** 저장소마다 키 파일을 하나 추가해 push하고 배포하는 일이므로 승인을 받는다. 보낼 범위(새로 바뀐 주소만, 한 언어 전체, 사이트 전체)도 함께 고르게 한다.
2. **키 만들기:** `openssl rand -hex 16`으로 영문 소문자와 숫자 32자를 만든다.
3. **키 파일 넣기:** 정적 파일 폴더(Next.js·Astro 모두 `public/`)에 `<key>.txt`를 만들고 내용은 키 한 줄만 둔다. 줄바꿈 없이 쓰려면 `printf '%s' "$KEY" > public/$KEY.txt`. `public/_redirects`가 있으면 그 경로를 가로채는 규칙이 없는지 먼저 본다.
4. **커밋과 push:** 키 파일만 이름으로 넣는다(`git add public/<key>.txt`). 같은 폴더에서 다른 세션이 작업 중일 수 있으니 `git add -A`는 쓰지 않는다. push는 1단계에서 받은 승인으로 한다.
5. **배포 기다리기:** `https://<site>/<key>.txt`가 키와 같은 내용을 돌려줄 때까지 조건 반복문이나 Monitor로 기다린다(보통 1~2분).
6. **제출:** [scripts/indexnow_submit.py](../scripts/indexnow_submit.py)로 보낸다. 먼저 `--dry-run`으로 주소 목록을 확인한다.
   ```bash
   python3 -I <skill-dir>/scripts/indexnow_submit.py https://<site> <key> --filter '/ko($|/)' --dry-run
   python3 -I <skill-dir>/scripts/indexnow_submit.py https://<site> <key> --filter '/ko($|/)'
   ```
   스크립트는 키 파일이 키와 같은 내용인지 확인하고, robots.txt의 `Sitemap:` 줄(사이트맵 묶음 포함)에서 주소를 모아 `--filter`에 맞는 것만 한 번에 보낸다. 기본 엔드포인트는 `https://searchadvisor.naver.com/indexnow`이고, `--endpoint https://api.indexnow.org/indexnow`로 바꾸면 IndexNow 공용 주소로 보낸다.
7. **결과 읽기:** 200(또는 202)은 **요청을 받았다**는 뜻이지 색인됐다는 뜻이 아니다. 실제 수집과 반영은 며칠에 걸쳐 이루어진다고 사용자에게 알린다. 403이나 422면 키 파일 내용과 주소의 호스트를 확인한다.
8. **기록:** 키와 키 파일 경로, 커밋, 보낸 날짜와 주소 수를 `DEPLOY.md`(또는 메모리)에 적는다. 키 파일은 지우지 않는다. 다음에 새 글을 올리면 같은 키로 그 주소만 보내면 된다.

## 언제 보내는가

- 새 페이지(번역 글 포함)를 추가했을 때: 그 주소들.
- 주소 구조를 바꿨을 때(예: 한국어를 `/`에서 `/ko`로): 옮긴 언어의 주소 전체.
- 같은 주소의 내용만 조금 고쳤을 때는 보내지 않아도 된다. 너무 자주, 많이 보내지 않는다.

## 도메인을 바꾸면

키 파일은 새 도메인에서도 같은 경로로 열려야 한다. 새 도메인으로 옮긴 뒤 `https://<new-domain>/<key>.txt`를 확인하고, 새 주소로 다시 보낸다.
