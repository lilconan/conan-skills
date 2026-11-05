# conan-skills

lilconan이 여러 프로젝트에서 함께 쓰는 Claude Code 스킬 묶음(플러그인 마켓플레이스)입니다. 한 저장소에서 이름, 버전, 변경 기록을 관리하고, 설치하면 모든 프로젝트에서 같은 스킬을 쓸 수 있습니다.

## 들어 있는 것

| 플러그인 | 버전 | 스킬 | 하는 일 |
|---|---|---|---|
| `conan-web` | 0.2.1 | `deploy-cloudflare` | 브라우저에서 처리하는 정적 사이트를 GitHub와 Cloudflare Pages로 배포하고 배포 전후를 점검 |
| | | `setup-analytics` | 배포된 정적 사이트에 구글 애널리틱스 4를 연결(속성 만들기, 개인정보 맞춤 설정, 측정 ID 배포, 수집 확인) |

스킬은 `플러그인:스킬` 형태로 불립니다. 예: `conan-web:deploy-cloudflare`. "배포 점검해 줘"처럼 말하면 Claude가 설명을 보고 알아서 고르고, `/conan-web:deploy-cloudflare`로 직접 부를 수도 있습니다.

## 설치

```bash
claude plugin marketplace add ~/conan-skills          # 이 컴퓨터의 폴더
# 다른 컴퓨터에서는: claude plugin marketplace add lilconan/conan-skills
claude plugin install conan-web@conan-skills
```

설치한 뒤 새 세션부터 쓸 수 있습니다.

## 이름 규칙

- **플러그인(주제별 묶음):** `conan-<주제>`. 예: `conan-web`(웹 서비스 출시), 앞으로 `conan-music`, `conan-design`.
- **스킬:** `동사-대상` 형식의 영어 소문자, 하이픈 연결. 예: `deploy-cloudflare`, `check-adsense`, `setup-analytics`.
- **폴더:** `plugins/<플러그인>/skills/<스킬>/SKILL.md`. 스킬 폴더 이름과 `SKILL.md`의 `name`을 같게 둡니다.

## 버전과 날짜

| 어디 | 무엇 | 규칙 |
|---|---|---|
| `plugins/<플러그인>/.claude-plugin/plugin.json`의 `version` | 플러그인 버전 | 이 값이 바뀌어야 설치된 곳에 업데이트가 갑니다 |
| `.claude-plugin/marketplace.json`의 해당 플러그인 `version` | 같은 값 | `plugin.json`과 맞춥니다 |
| `SKILL.md` 앞부분 `metadata.version`, `metadata.updated` | 스킬 버전과 고친 날짜 | skill-creator 검사기가 허용하는 위치 |
| `plugins/<플러그인>/CHANGELOG.md` | 날짜, 버전, 바뀐 점, 바뀐 이유 | 어떤 프로젝트에서 무엇을 겪어 고쳤는지 남깁니다 |

semver: 문구나 작은 수정은 patch(0.1.0 → 0.1.1), 단계나 기능 추가는 minor(0.2.0), 쓰는 방법이 바뀌면 major(1.0.0).

## 스킬을 고치거나 새로 만들 때

1. 스킬 본문은 Anthropic 공식 플러그인 **skill-creator**로 만들고 고칩니다(초안 → 검사 → 평가 → 개선). 평가 작업 폴더(`*-workspace/`)는 커밋하지 않습니다.
2. 검사:
   ```bash
   claude plugin validate ~/conan-skills                       # 마켓플레이스
   claude plugin validate ~/conan-skills/plugins/<플러그인>      # 플러그인과 스킬
   ```
3. 버전 올리기: `plugin.json`, `marketplace.json`, `SKILL.md`의 `metadata`, `CHANGELOG.md`를 함께 고칩니다.
4. 커밋하고 릴리스 태그를 답니다. `claude plugin tag`가 `plugin.json`과 마켓플레이스 항목의 버전이 맞는지 확인하고 `<플러그인>--v<버전>` 태그를 만듭니다.
   ```bash
   claude plugin tag plugins/<플러그인>
   ```
5. 설치된 곳에 반영:
   ```bash
   claude plugin marketplace update conan-skills
   claude plugin update <플러그인>@conan-skills    # 반영하려면 Claude Code를 다시 시작
   ```
   고치는 중에는 설치 없이 `claude --plugin-dir ~/conan-skills/plugins/<플러그인>`으로 바로 시험할 수 있습니다.

## 주의할 점

- **설명(description)이 스킬을 고르는 기준입니다.** "언제 쓰는지"를 구체적으로 쓰고, 다른 스킬과 겹치지 않게 합니다.
- **프로젝트마다 다른 값은 그 프로젝트에 둡니다.** 예: 배포 주소, 환경 변수 표는 각 프로젝트의 `DEPLOY.md`. 스킬에는 여러 프로젝트에 공통인 순서와 규칙만 둡니다.
- **비밀값(토큰, 키)은 넣지 않습니다.** 저장소는 비공개입니다.
- **아직 옮기지 않은 개인 스킬:** `~/.claude/skills`의 `portfolio-deck`, `suno-jazzfunk-generator`, `jazz-sage`, `nebula-analyst`, `nebula-strategist`. 나중에 `conan-design`, `conan-music`으로 옮길 수 있습니다.
