# UTM 링크 표 템플릿

프로젝트의 `docs/marketing/utm-links.md`로 복사해 `<site>`, 채널, 핵심 이벤트를 채운다. PixelUp(`~/image_upscale/docs/marketing/utm-links.md`, 한국어 채널)과 SongToBars(`~/Documents/visual/docs/marketing/utm-links.md`, 영어 채널)가 실제 예다.

```markdown
# 채널별 UTM 링크

글, 댓글, 프로필, 영상 설명란에 사이트 링크를 넣을 때 아래 표의 링크를 그대로 복사해서 씁니다. 링크 끝의 `utm_…` 값으로 GA4가 어느 채널에서 들어온 방문인지 구분합니다.

GA4에서 보는 곳: **보고서 → 획득 → 트래픽 획득**에서 측정기준을 "세션 소스/매체"나 "세션 캠페인"으로 바꾸면 채널별로 나뉩니다. `utm_content`는 "세션 수동 광고 콘텐츠"로 볼 수 있습니다. 채널별 성과는 방문 수보다 `<핵심 이벤트>` 수로 비교하는 편이 정확합니다.

## 규칙

- 모든 값은 소문자, 공백 없이 씁니다. 대소문자가 다르면 GA4에서 다른 값으로 집계됩니다.
- `utm_source`: 플랫폼 이름 (naver, reddit, youtube …)
- `utm_medium`: 유입 종류. `blog`, `social`(커뮤니티·SNS), `video`(영상 설명란), `directory`(도구 소개 사이트), `chat`(오픈채팅·디스코드)
- `utm_campaign`: 첫 공개 홍보는 `launch`, 이후 업데이트 소식은 `update-YYYYMM`.
- `utm_content`: 같은 플랫폼 안에서의 구분 (게시판·서브레딧 이름, 영상 이름 등)
- 새 채널이 생기면 이 표에 한 줄 추가하고, 같은 채널에는 늘 같은 값을 씁니다.
- 사이트 안 링크(메뉴, 버튼)에는 UTM을 붙이지 않습니다.
- 사이트 주소를 자기 도메인으로 옮기면 표의 주소 부분만 바꿉니다.

## <채널 묶음>

| 위치 | 링크 |
|---|---|
| <위치> | `https://<site>/?utm_source=<source>&utm_medium=<medium>&utm_campaign=launch` |
```
