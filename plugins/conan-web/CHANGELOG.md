# conan-web 변경 기록

## 0.1.0 (2026-11-05)

- `deploy-cloudflare` 스킬 추가: 정적 사이트를 GitHub(비공개)와 Cloudflare Pages로 배포하는 순서와 배포 전후 점검.
  - 근거: PixelUp(Next.js) 7단계와 마지막 점검, SongToBars(Astro) 배포에서 겪은 것.
  - 한 번씩 놓쳤던 항목을 점검표에 넣음: 애드센스만 켰을 때의 동의 기본값, 버전 없는 큰 파일의 캐시 헤더, 파일당 25MiB 한도, 사이트맵의 localhost 주소.
  - 빌드 결과 검사 스크립트 `scripts/check_output.py`(한도, robots·sitemap·ads.txt·_headers·404, localhost, 자리표시자 값).
  - Cloudflare 연결은 대시보드 Git 연결(기본)과 wrangler 직접 배포(선택)를 모두 안내.
  - 프레임워크별 설명서: Next.js, Astro, Vite.
- skill-creator 평가 1차(시험 3건, 스킬 사용 100% / 미사용 76%)에서 나온 점을 반영:
  - 애드센스는 자기 도메인이 필요할 수 있음(`*.pages.dev`), 도메인 이전 순서(Bulk Redirects, 검색엔진 재인증).
  - `NODE_VERSION`은 22 이상(Node 20은 2026-04-30 지원 종료).
  - 결과 폴더에만 있는 파일은 Cloudflare Git 빌드에서 사라짐.
  - 문의 이메일·운영자 이름의 자리표시자 기본값이 공개되는 문제, 검사 스크립트로 탐지.
  - 오픈소스 고지 대상을 라이브러리·웹폰트까지 넓힘(MPL, LGPL, OFL 요건).
  - 동의 기본값의 위치(광고 스크립트보다 앞)와 내용(유럽 밖 맞춤 광고 꺼짐 여부), 승인 후 유럽 동의 메시지.
  - 따라 쓸 수 있는 예시 추가: 프레임워크별 동의 기본값 코드, Vite에서 사이트맵·robots를 빌드 때 만드는 플러그인.
- 평가 2차(시험 3건, 항목 28개): 스킬 사용 100%, 미사용 71%.
