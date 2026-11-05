# 애드센스·분석 준비 점검표

애드센스 심사는 "실제 콘텐츠가 있는, 운영자가 분명한 사이트"인지를 본다. 아래 항목은 심사에서 자주 문제가 되는 것과, 두 프로젝트에서 실제로 놓쳤던 것이다.

| 항목 | 확인 방법 | 왜 필요한가 |
|---|---|---|
| 자기 도메인 | 사이트 주소가 `*.pages.dev` 같은 남의 도메인이 아닌지 | 애드센스는 소유한 도메인 단위로 사이트를 등록한다. 공용 하위 도메인은 등록이 막히거나 승인이 어렵다(정책은 신청 전에 다시 확인) |
| 개인정보처리방침 | 페이지 존재, 푸터 링크 | 애드센스 정책상 필수. 광고 쿠키와 제3자 광고 업체 고지 문구가 있어야 한다 |
| 방침 내용과 실제 수집 일치 | GA 이벤트 목록(`track()` 호출, 위임 리스너)과 방침의 수집 항목 표 비교. 호스팅 업체(Cloudflare) 기재 | 실제와 다르면 신뢰와 법적 문제 |
| 약관, 소개, 문의 | 페이지 존재, 운영자 이름·연락처 표시 | 운영자가 분명해야 심사를 통과하기 쉽다 |
| 연락처가 비어 있을 때 | 이메일 값이 없으면 줄을 숨기는지, 빈 `mailto:`가 남지 않는지 | 빈 연락처는 심사와 신뢰에 불리 |
| 자리표시자 기본값 | 설정 파일에 `contact@….example`, `○○ 운영자` 같은 기본값이 있는지, 빌드 결과에 남았는지(`check_output.py`) | 변수를 빠뜨린 배포에 가짜 연락처가 공개됨. Cloudflare 빌드(`CF_PAGES=1`)에서 비면 실패시키거나 숨긴다 |
| HTML 사이트맵과 XML 사이트맵 | `/site-map` 같은 페이지, `sitemap.xml`(또는 `sitemap-index.xml`) | 탐색과 색인 |
| robots.txt | 전체 허용, `Sitemap:` 줄이 실제 주소 | 크롤러 차단 방지 |
| ads.txt | ID가 있으면 `google.com, pub-…, DIRECT, f08c47fec0942fa0`, 없으면 주석 한 줄 | 승인 후 수익 손실 방지. 정적 사이트는 404를 낼 수 없음 |
| 동의 기본값 위치 | `gtag('consent','default', …)`가 GA와 애드센스 **어느 쪽만 켜도** 들어가는지, 광고·분석 스크립트보다 **앞에** 있는지. EEA·영국·스위스는 denied | 유럽 방문자 규정. 방침에 "동의 전에는 저장하지 않는다"고 썼다면 그대로 동작해야 함 |
| 동의 기본값 내용 | 지역 외(한국 등) 기본값이 의도와 맞는지. 지역 외에서도 `ad_storage`·`ad_personalization`이 denied면 맞춤 광고가 꺼짐 | 수익 감소, "맞춤 광고를 한다"는 방침 문구와 불일치. 의도인지 사용자에게 확인 |
| 유럽 동의 메시지 | 애드센스 승인 후 "개인정보 보호 및 메시지"에서 GDPR 메시지를 켜는지 | 기본값만으로는 유럽 방문자에게 광고 쿠키를 쓸 수 없음. 방침에 동의 메시지를 언급했다면 실제로 켜야 함 |
| 광고 스크립트 조건 | 애드센스 ID가 있을 때만 `adsbygoogle.js`를 넣는지 | ID 없이 넣으면 콘솔 오류 |
| 콘텐츠 | 가이드·설명 글이 충분한지, 직접 쓴 글인지, 샘플 이미지·폰트·모델의 라이선스 | 얇은 콘텐츠와 저작권 문제는 대표적인 거절 사유 |
| 오픈소스 고지 | 브라우저로 내려보내는 것 전부: `package.json`의 `dependencies`(번들에 들어가는 라이브러리), 웹폰트, 모델·런타임·데이터. 각 라이선스와 저작권자를 소개 페이지 등에 고지 | BSD·MIT·Apache는 저작권 고지 의무, MPL-2.0은 소스 위치 안내, LGPL은 고지와 교체 가능성 안내, OFL(폰트)은 저작권·라이선스 고지. 모르는 라이선스는 원문을 확인 |
| 서치 콘솔 인증 | 인증 메타 태그 값 설정, 사이트맵 제출 | 색인 확인 |
| 이미지·파일 이름 등 민감 정보 | 분석 이벤트에 이미지 내용·파일 이름이 들어가지 않는지 | 개인정보 |

## 동의 기본값 예시

GA와 애드센스 중 **하나라도** 켜져 있으면 넣고, 두 스크립트보다 **앞에** 둔다. 유럽 밖 기본값은 사이트 정책에 맞춰 정한다(아래는 유럽 밖에서 광고 쿠키를 허용하는 예. 맞춤 광고를 쓰지 않을 거라면 `denied`로 두고 방침에도 그렇게 쓴다).

```html
<!-- (GA_ID || ADSENSE_ID)일 때만, <head>에서 GA·애드센스 스크립트보다 먼저 -->
<script>
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { dataLayer.push(arguments); };
  gtag('consent', 'default', {
    analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    region: ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT',
             'NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH'],
  });
  gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted' });
</script>
<!-- 그다음에 GA(gtag.js + config), 애드센스(adsbygoogle.js) -->
```

- Next.js(App Router): 별도 컴포넌트로 만들어 레이아웃에서 `(gaId || adsenseId) &&` 조건으로 GA·애드센스보다 먼저 렌더링한다(PixelUp `components/Analytics.tsx`의 `ConsentDefaults`).
- Astro: `BaseLayout.astro`의 `<head>`에서 `{(SITE.gaId || SITE.adsenseClient) && <script is:inline>…</script>}`를 광고·분석 스크립트보다 위에 둔다.
- 일반 HTML(Vite): 모든 HTML 파일의 `<head>` 맨 앞에 넣는다.

## 점검 요령

- 오픈소스 목록은 `package.json`의 `dependencies`를 기준으로 `node_modules/<pkg>/package.json`의 `license`와 `LICENSE` 파일을 확인한다. `@fontsource*` 같은 폰트 패키지, 직접 넣은 모델·wasm 파일도 빠뜨리지 않는다. `devDependencies`는 브라우저로 나가지 않으면 고지 대상이 아니다.
- GA 이벤트 목록은 코드에서 `track(`, `gtag('event'`를 검색해 모은다. 오류 메시지 일부나 클릭 위치처럼 이벤트 값으로 보내는 내용도 방침에 적혀 있는지 본다. 방침의 표와 `DEPLOY.md`의 이벤트 표가 함께 맞는지도 본다.
- 동의 기본값은 빌드 결과에서 확인하는 것이 가장 확실하다. 애드센스 ID만 임시로 넣고 빌드해 `out/index.html`에 `ad_storage`가 들어가는지 본다(커밋하지 않는다).
- 정책 시행일은 공개 전이라면 공개일로 맞춰도 된다. 이미 공개된 뒤 바꾸는 경우에는 방침에 적은 사전 고지 기간을 지킨다.
