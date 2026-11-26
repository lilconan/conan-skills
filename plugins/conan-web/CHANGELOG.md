# conan-web 변경 기록

## 0.6.3 (2026-11-26)

근거: 같은 날 kmb-portfolio에서 집 IP를 내부 트래픽으로 빼며 확인한 순서.

- `setup-analytics` 0.4.2
  - `references/ga4-console.md` 9절 "내부 트래픽 빼기": IP 확인(IPv4·IPv6), 태그 설정이 Tag Manager iframe 패널로 열림, 규칙 저장 뒤 **제출·게시**가 있어야 적용됨, 데이터 필터 `사용중`과 되돌릴 수 없다는 확인 창, `/g/collect`의 `tt=internal`로 확인, 빠지는 범위(그 속성 하나, 그 IP만).
  - 데이터 필터 화면 주소(`admin/datapolicies/datafilters`) 추가.
  - 6단계 안내: 내부 트래픽, 브라우저별 제외(`?notrack`), 출처별 `?ref` 링크를 목적에 따라 고르게 함.

## 0.6.2 (2026-11-26)

근거: 2026-11-26 포트폴리오(빌드 없는 일반 HTML)에 GA4를 붙인 뒤, `check_ga.py`가 JS 모듈에서 넣는 태그를 읽지 못해 "측정 ID 없음"으로 잘못 판정함.

- `setup-analytics` 0.4.1
  - `check_ga.py`: HTML에 측정 ID가 없으면 같은 사이트의 스크립트(`<script src>`, 인라인 모듈, 정적·동적 `import`와 `export … from`, 최대 30개 파일)를 따라가 측정 ID가 있는 파일에서 동의 기본값·로더·순서를 판정. 표에 "찾은 곳" 열 추가. kmb-portfolio(JS), PixelUp·SongToBars(HTML)로 확인.
  - 3단계: GA 홈의 "태그가 지정되어 있는지 확인하십시오" 안내는 첫 데이터 처리 전(최대 48시간)에 남는 것이라 실시간에 조회가 보이면 그대로 둔다는 설명 추가.

## 0.6.1 (2026-11-22)

근거: 2026-11-22 포트폴리오(빌드 없는 일반 HTML, 수익화 없음) 배포와 그 뒤의 스킬 검토 보고서에서 "꼭 고칠 것" 12개를 반영함.

- `deploy-cloudflare` 0.4.0
  - 0단계: 사이트 종류(수익화·포트폴리오·도구)를 먼저 정하고, 수익화 계획이 없으면 애드센스 항목과 ads.txt 확인을 `해당 없음`으로 접음.
  - 빌드 없는 일반 HTML 경로 추가: 저장소 루트를 출력으로 쓰지 않고 화이트리스트 스크립트로 `dist/`를 만듦. 새 `references/plain-html.md`(공개 범위, 404·`.html` 주소, 직접 적힌 사이트 주소, 해시 없는 `assets/` 캐시, noreply 커밋 이메일).
  - 404: 루트 404.html이 없으면 Cloudflare가 SPA로 보고 없는 주소에 홈을 200으로 준다는 사실로 고침(전에는 "기본 404가 나온다"고 잘못 적음).
  - `*.pages.dev` 애드센스 주장 고침: Public Suffix List에 있어 공식 기준으로는 등록 가능, 이전 비용 때문에 자기 도메인 권장.
  - 유럽 맞춤 광고에 Google 인증 CMP(IAB TCF)가 필수라는 규정 추가(EEA·영국 2024-01-16, 스위스 2024-07-31).
  - ads.txt 404 설명의 모순 정리, 첫 연결의 역할 분담(GitHub 앱 설치·저장소 허용은 사용자) 통일.
  - `references/cloudflare.md`: 2026-11 대시보드 경로, "저장소가 목록에 안 보일 때" GitHub 앱 Repository access 절차, 프로젝트 이름 규칙(소문자·숫자·하이픈), 빌드 없는 사이트 열.
  - `references/deploy-md-template.md`: 한 표 서두, Node 빌드·빌드 없음·수익화 조건부 절, "남은 일" 절.
  - `references/vite.md`: Vite 8의 `build.rolldownOptions`(7 이하 `rollupOptions`).
  - `check_output.py`: 루트 404.html 없으면 `고칠 것`, 공개되면 안 되는 파일(메모·스크립트·숨김 파일·작업 폴더) 검사, 모든 `href`·`src`를 따옴표와 상관없이 모으고 상대 경로를 풀어 확인(링크 0개면 `확인 필요`), `--no-ads`, 표 셀의 `|` 이스케이프.

## 0.6.0 (2026-11-20)

근거: 2026-11-06~20 PixelUp(Next.js)·SongToBars(Astro) 작업 기록 전체를 여섯 구간으로 나눠 교훈 후보 93개를 뽑고, 중복과 이미 반영된 것을 걸러 58개를 반영함(목록과 독립 검수 결과는 이번 작업 기록에 있음).

- `deploy-cloudflare` 0.3.0
  - 0단계: 정적 배포가 가능한지(서버 기능, Next.js 빌드 표의 `ƒ`), 대상 독자와 언어, "다른 프로젝트처럼"이면 그 프로젝트와 비교.
  - 1단계: 빌드 전 개발 서버 멈추기, 빈 결과 폴더 검사 금지, `.env.local`을 치우고 Cloudflare와 같은 조건으로 시험 빌드, Cloudflare처럼 띄워 보기, 첫 배포 전 독립 검토.
  - `check_output.py`: 페이지 수(0개면 실패), `<title>` 하나와 og·twitter 제목 일치, `og:image`·`twitter:image`와 그 파일, favicon·터치 아이콘·매니페스트, 내부 링크가 실제 파일을 가리키는지. ads.txt 안내를 "심사 요청 전에 게시자 ID"로 고침.
  - 4단계: 첫 커밋 전 올라갈 파일·토큰 검사·git 사용자 확인, 다른 세션과 같은 폴더면 내 파일만 넣기.
  - 6단계: 주소 추측 금지, 배포 기다리기(check-run 확인 뒤 새 빌드에만 있는 내용으로, 공용 JS 조각까지), ads.txt·사이트맵 주소 200, 콘솔 오류·깨진 이미지, 회귀 비교, 언어별 공개 환경 변수 확인.
  - 원칙: 목표·훅은 승인이 아님, 외부 지시서는 먼저 검증하고 프로젝트 원칙과 부딪치면 묻기, 사용자만 할 수 있는 남은 일은 글로 남기기, 대시보드는 사용자 로그인 뒤 Claude in Chrome으로.
  - `references/cloudflare.md`: 대시보드를 다룰 브라우저(앱 안의 브라우저는 로그인 실패, 웨일 등 Chromium의 Claude in Chrome 연결 안내), 환경 변수 바꾸고 다시 배포하기(`?to=/:account/…` 주소), 애드센스 신청 순서, 도메인 이전 때 GA 스트림·UTM·IndexNow 키.
  - `references/adsense-checklist.md`: ads.txt 실제 주소, 게시자 ID 시점, 제목·공유 카드, 아이콘·매니페스트, 구조화 데이터 점검(Article 선택 항목, TechArticle, FAQ 문구 일치, FAQ 리치 결과 제한), 모바일 375px, 이미지 크기, 홈 본문 측정, 없어진 기능의 설명, 동의 기본값 세 가지 조합 빌드.
  - `references/nextjs.md`: `trailingSlash`, `start` 스크립트, `ƒ` 경로, `title.template`이 홈에 안 붙는 문제, `.next` 삭제 순서, 빈 `out/`의 거짓 통과, `.env.local`, prebuild 훅과 ESLint 제외.
  - `references/i18n.md`: hreflang 대소문자(Next `hrefLang`), 404 제외, 운영자 이름 같은 공개 값은 언어 중립으로 두고 배포 뒤 언어별 확인.
- `register-search` 0.3.0
  - 네이버 서치어드바이저는 앱 안의 브라우저와 Claude in Chrome(웨일 포함) 모두에서 막힘. 우회하지 말고 대안(IndexNow)을 먼저 내고, 못 한 단계를 완료로 표시하지 않음.
  - 새 `references/indexnow.md`와 `scripts/indexnow_submit.py`(키 파일 확인, 사이트맵 묶음에서 주소 모으기, `--filter`, `--dry-run`).
  - 네이버 사이트맵은 주소가 그대로면 다시 제출할 필요 없음, 입력란에 전체 주소. 구글 "가져올 수 없음"은 2주 넘게 남을 수 있어 Googlebot 요청으로 먼저 진단, Astro는 `sitemap-0.xml`도 제출, 제출 버튼 클릭과 확인 방법.
  - 인증 태그 전체를 붙여 넣어도 되게 안내, 두 메타 태그가 실제 페이지에 나올 때까지 기다린 뒤 "확인", 번역 페이지 추가 뒤 점검, 리치 결과 테스트 사용법.
  - `check_search.py`: hreflang을 대소문자 무시로 찾음. 전에는 Astro의 `hreflang`(소문자)을 못 찾아 SongToBars가 "없음"으로 나왔다.
- `setup-analytics` 0.4.0
  - 유입경로 탐색은 데이터 없이도 만들 수 있음(`이벤트 생성` 줄). 주요 이벤트만 데이터가 필요하고 "최근 활동" 탭에서 지정, 그때까지 남은 일로 기록.
  - `references/ga4-console.md`: 앱 안의 브라우저로 할 때(로그인은 사용자, 창 넓히기, `find`·`ref`), 맞춤 측정기준의 비슷한 이름 제안 함정과 개수 다시 세기, 화면 주소 표, 유입경로 탐색 만드는 순서.
  - `references/event-design.md`: 두 프로젝트 이벤트 비교와 맞춤 측정기준 등록 확인, 주요 이벤트·깔때기를 쉬운 예로 설명, 시험 요령(DataTransfer, 슬라이더 setter, 이동·시간 초과로 끊기는 스크립트, 배포 뒤 JS 조각 확인, 확인하지 못한 것 보고).
  - `check_ga.py`: 유럽·영국·스위스 밖의 `ad_storage` 기본값을 표에 보여 주고, 지역 구분 없이 거부면 "확인 필요".
  - 개발 서버에서 GA가 켜지는지, Cloudflare 대시보드 로딩·Metrics 탭 함정, 못 한 일 보고 원칙.

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
