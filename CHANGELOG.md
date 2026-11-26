# conan-skills 변경 기록

플러그인별 자세한 기록은 `plugins/<플러그인>/CHANGELOG.md`에 있습니다.

## 2026-11-26

- `conan-web` 0.6.4: 내부 트래픽 규칙을 만들기 전에 미게시 변경 확인.
- `conan-web` 0.6.3: setup-analytics에 내부 트래픽(운영자 IP) 빼기 절차와 확인 방법.
- `conan-web` 0.6.2: check_ga.py가 JS 모듈로 GA를 넣는 사이트도 검사, GA 홈 "태그 지정 확인" 안내 설명.

## 2026-11-20

- `conan-web` 0.6.0: 11월 6일~20일 PixelUp·SongToBars 작업에서 나온 교훈 반영(세 스킬 모두). IndexNow 제출 스크립트, check_output.py 제목·공유 메타·아이콘·내부 링크 검사, check_ga.py 지역 밖 동의 기본값 검사, check_search.py hreflang 대소문자 버그 수정.

## 2026-11-16

- `conan-writing` 0.4.1: unify-copy 조사 받침 규칙과 재검사.
- `conan-writing` 0.4.0: `unify-copy` 스킬(문서 말투 통일), distill-headline 6단계 이관.
- `conan-writing` 0.3.1: distill-headline 최고 위계 제목 말투 예외.
- `conan-writing` 0.3.0: distill-headline에 카드 제목·라벨 단어형 끝맺음 규칙.
- `conan-writing` 0.2.0: distill-headline에 문서 말투 통일 단계와 전체 검수 절차.
- `conan-writing` 0.1.0: `distill-headline` 스킬(목적이 담긴 한 줄 만들기).

## 2026-11-06

- `conan-web` 0.5.0: 다국어 사이트 점검(deploy-cloudflare `references/i18n.md`, check_search.py의 lang·hreflang 검사).

## 2026-11-05

- `conan-web` 0.4.2: check_search.py 연결 오류 처리, 이벤트 설계 규칙 보완.
- `conan-web` 0.4.1: 검사 스크립트 ruff 정리.
- `conan-web` 0.4.0: setup-analytics에 이벤트 설계 단계.
- `conan-web` 0.3.0: `register-search` 스킬, setup-analytics에 Web Analytics·UTM 추가.
- `conan-web` 0.2.1: setup-analytics 데이터 보관 순서 보완.
- `conan-web` 0.2.0: `setup-analytics` 스킬.
- 마켓플레이스 `conan-skills` 생성.
- `conan-web` 0.1.0: `deploy-cloudflare` 스킬.
