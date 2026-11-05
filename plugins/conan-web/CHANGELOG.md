# conan-web 변경 기록

## 0.5.0 (2026-11-06)

- `deploy-cloudflare` 0.2.0: 다국어 정적 사이트 점검(`references/i18n.md`) 추가. 기본 언어는 `/`, 나머지는 `/<코드>/`, 언어마다 `<html lang>`(Next.js는 route group별 루트 레이아웃), canonical, hreflang과 x-default, 사이트맵 alternates, 자동 이동 금지와 안내 띠, 다국어 404, 정책 페이지 번역.
- `register-search` 0.2.0: `check_search.py`가 홈의 html lang, canonical, hreflang(x-default 누락·다른 주소 섞임 검사)과 사이트맵의 언어 대체 링크 수를 표에 보여 줌. 언어를 추가한 뒤 사이트맵 재제출과 네이버 수집 요청 안내.
  - 근거: PixelUp을 글로벌 대상으로 바꾸며 영어를 기본 주소로, 한국어를 `/ko`로 옮긴 과정.

## 0.4.2 (2026-11-05)

- `register-search` 0.1.1: `check_search.py`가 DNS 실패·연결 거부·타임아웃에서 멈추지 않고 표에 "연결 실패"로 적음.
- `setup-analytics` 0.3.1: 이벤트 설계 규칙 3가지 추가(깔때기 단계 이벤트는 실제로 추가됐을 때만, 페이지를 떠나며 하는 정리는 사용자 취소로 세지 않음, bfcache 복원 시 방문 요약 초기화).
  - 근거: PixelUp 전체 코드 리뷰에서 add_images가 전부 거부된 시도에도 전송되고, 페이지 이동 때 대기 작업마다 upscale_cancel이 찍히던 문제.

## 0.4.1 (2026-11-05)

- 검사 스크립트 3개(`check_output.py`, `check_ga.py`, `check_search.py`)를 ruff 기본 규칙과 서식에 맞춤. 넓은 `except Exception` 대신 네트워크·XML 오류만 잡도록 바꾸고 실행 권한을 줌. 동작은 같음.

## 0.4.0 (2026-11-05)

- `setup-analytics` 0.3.0: 이벤트 설계 단계(`references/event-design.md`) 추가.
  - 근거: PixelUp에 사용자 행동 이벤트 11가지(tool_ready, image_rejected, upscale_cancel, backend_fallback, batch_action, result_compare, sample_compare, leave_warning, session_summary 등)를 넣고 GA에 맞춤 측정기준 12개·측정항목 4개를 등록한 과정.
  - 질문에서 이벤트를 고르는 방법, 개인정보 규칙(구간·분류 코드), GA 화면의 함정(이름에 `·` 불가, Esc로 창이 닫힘, 주요 이벤트는 데이터가 들어온 뒤), gtag를 가로채는 시험 방법.

## 0.3.0 (2026-11-05)

- `register-search` 스킬 추가: 구글 서치 콘솔(URL 접두어, HTML 태그), 네이버 서치어드바이저(사용자가 직접, Claude in Chrome은 네이버를 못 엶), Bing(서치 콘솔에서 가져오기) 등록과 사이트맵 제출.
  - 근거: SongToBars에서 하고 PixelUp에서 빠져 있던 작업을 PixelUp에 적용한 과정.
  - 인증 값은 `meta name → content` 지도 하나로 관리(Next.js metadata, Astro 레이아웃, Vite 훅 예시).
  - 확인 스크립트 `scripts/check_search.py`(인증 태그, robots, 사이트맵, 크롤러 접근).
  - 평가(시험 2건): 스킬 사용 100%, 미사용 93%. 미사용 쪽이 짚은 크롤러 접근 확인, 색인 생성 요청, Bing 자체 인증 백업을 반영. Astro 사이트맵 경로(`sitemap-index.xml`) 안내도 고침.
- `setup-analytics` 0.2.0: Cloudflare Web Analytics 켜기(Metrics 탭, 개인정보처리방침 문구)와 홍보용 UTM 링크 표(템플릿 추가).

## 0.2.1 (2026-11-05)

- `setup-analytics`: GA 데이터 보관 화면 주소와 순서를 PixelUp에서 실제로 바꿔 보며 확인해 고침(이벤트 데이터만 기본 2개월, 저장 후 다시 불러와 확인).

## 0.2.0 (2026-11-05)

- `setup-analytics` 스킬 추가: 배포된 정적 사이트에 GA4를 연결하는 순서.
  - 근거: PixelUp(pixelup-ai.pages.dev)에 GA를 붙인 과정(Claude in Chrome으로 속성·웹 스트림 생성, Cloudflare 환경 변수, Retry deployment, 실시간 보고서 확인).
  - 코드 점검(측정 ID 입력 방식, 동의 기본값 위치, 이벤트와 개인정보처리방침, 다운로드 링크 클릭 중복, 방침의 보관 기간).
  - GA 화면 순서: 계정 확인(`authuser`), 기존 계정에 속성만 추가, 향상된 측정에서 파일 다운로드·양식 상호작용 끄기, 데이터 보관 14개월, 맞춤 측정기준, 측정 ID를 페이지 텍스트로 읽기(0과 O).
  - 실제 사이트 확인 스크립트 `scripts/check_ga.py`(측정 ID, 동의 기본값과 실행 순서, Next.js preload 링크는 제외).
- skill-creator 평가 1차(시험 2건): 스킬 사용 100%, 미사용 80%. 미사용 쪽이 짚은 데이터 보관 기간, 맞춤 측정기준, 새로고침 없는 페이지 이동 측정을 반영.
- 평가 2차(항목 19개): 스킬 사용 100%, 미사용 79%. 사용자 제공 데이터 수집 확인, 향상된 측정은 GA 화면에서만 확인(공개 태그 파일의 `vtp_enable*` 값은 실제 설정과 다름)을 추가.

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
