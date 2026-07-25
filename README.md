# dotfiles-claude

Claude Code 하네스 설정 파일. 새 노트북에서 클론하면 동일한 개발 환경을 바로 사용할 수 있다.

## 이 저장소와 ~/.claude의 관계

`~/.claude`는 실체 디렉터리이고, 이 저장소의 설정 항목(아래 폴더/파일 구조에 나열된 것들)만 개별
심볼릭 링크로 연결되어 있다. 즉 **이 저장소의 파일을 고치면 = `~/.claude`도 그대로 바뀐다** (같은
파일을 가리키는 symlink라 둘이 다른 사본이 아니다).

- 세션·캐시·데몬 로그 같은 런타임 데이터(`sessions/`, `cache/`, `daemon/` 등)는 저장소 밖 실제
  `~/.claude`에만 존재하고 이 저장소에는 절대 들어오지 않는다.
- 저장소에 새 최상위 폴더/파일을 추가해도 `~/.claude`에 자동으로 나타나지 않는다 — [새 노트북에서
  복원](#새-노트북에서-복원)의 `ln -s` 명령으로 개별 연결해야 한다.
- `~/.claude`는 git 저장소가 아니다(`.git`은 이 저장소 경로에만 있음). 커밋·브랜치 확인·PR 등 git
  작업은 항상 `~/Repository/dotfiles-claude`에서 한다.

## 구조

### 폴더 구조

```
~/.claude/
├── agents/                # 에이전트
├── agent-memory/          # 파일 기반 장기 기억 (실험 로그, 오류 기록, TODO)
├── commands/              # 슬래시 커맨드
├── docs/                  # 프로젝트 지식 축적
│   ├── assets/            # 도식 이미지
│   ├── adrs/              # Architecture Decision Record
│   ├── rfc/               # 여러 입장을 수렴해 합의 도출하는 논의 문서
│   └── specs/             # 설계 문서 (spec, plan, review)
├── hooks/                 # 자동 실행 스크립트
├── output-styles/         # 출력 스타일 (진행 상황 표시 포맷 등)
├── plugins/               # 플러그인 상태 파일 (CLI가 관리)
├── rules/                 # Claude 행동 규칙 (자동 로드)
├── skills/                # 글로벌 스킬
│   ├── agent-creator/
│   ├── directory/
│   ├── jd-analyze/
│   ├── ship-discussion/
│   ├── skill-creator/
│   ├── unity-mcp-skill/
│   ├── wiki-ingest/
│   ├── wiki-lint/
│   └── wiki-query/
└── workflows/             # Workflow 스크립트 (*.js) — 서브에이전트 오케스트레이션
```

### 파일 구조

**최상위**

| 파일 | 역할 |
|------|------|
| `CLAUDE.md` | 글로벌 워크플로우 (spex + superpowers) |
| `settings.json` | hooks, 플러그인, MCP 서버 |
| `claude-powerline.json` | 상태줄(powerline) 설정 |
| `CHANGELOG.md` | 변경 이력 (날짜별, 추가/변경/수정/삭제) |
| `README.md` | 이 문서 |
| `.gitignore` | 백업 파일(`*.bak`, `*.orig`) 제외 |

**하위 디렉터리** — 안의 파일 목록·역할은 폴더별 `README.md` 참고

| 디렉터리 | 역할 |
|------|------|
| [`rules/`](rules/README.md) | Claude 행동 규칙 (자동 로드) |
| [`hooks/`](hooks/README.md) | 자동 실행 스크립트 |
| [`agents/`](agents/README.md) | 에이전트 |
| [`commands/`](commands/README.md) | 슬래시 커맨드 |
| [`skills/`](skills/README.md) | 글로벌 스킬 |
| [`workflows/`](workflows/README.md) | Workflow 스크립트 |
| [`agent-memory/`](agent-memory/README.md) | 파일 기반 장기 기억 |
| [`output-styles/`](output-styles/README.md) | 출력 스타일 |
| [`plugins/`](plugins/README.md) | 플러그인 상태 파일 (직접 편집 대신 `/plugin` 커맨드로 관리) |
| [`docs/`](docs/README.md) | 프로젝트 지식 축적 |
| [`docs/specs/`](docs/specs/README.md) | 설계 문서 |
| [`docs/adrs/`](docs/adrs/README.md) | Architecture Decision Record |
| [`docs/rfc/`](docs/rfc/README.md) | 논의 문서 (`ship-discussion` 스킬이 자동 생성) |

## 플러그인

| 플러그인 | 마켓플레이스 | 활성화 | 역할 |
|---------|------------|:---:|------|
| superpowers | claude-plugins-official | ✅ | TDD, 규율, 브레인스토밍 등 스킬 모음 |
| spex | cc-rhuss-marketplace | ✅ | SDD, speckit CLI 통합 — `/speckit-spex-ship` 사용법은 [`docs/spex-ship-guide.md`](docs/spex-ship-guide.md) 참고 |
| claude-md-management | claude-plugins-official | ✅ | CLAUDE.md 감사·개선 |
| swift-lsp | claude-plugins-official | ✅ | Swift LSP 연동 |
| last30days | last30days-skill | ✅ | 최근 30일 웹/커뮤니티 리서치 |
| claude-powerline | claude-powerline | ✅ | 상태줄(powerline) 렌더링 |

## 새 노트북에서 복원

`~/.claude`를 저장소로 통째로 클론하지 않는다 — 저장소는 `~/Repository/dotfiles-claude`에 두고,
`~/.claude`는 실체 디렉터리로 만들어 설정 항목만 개별 symlink로 연결한다.

```bash
# 1. 클론 (~/.claude가 아니라 별도 경로에)
git clone git@github.com:<username>/dotfiles-claude.git ~/Repository/dotfiles-claude
REPO=~/Repository/dotfiles-claude

# 2. ~/.claude 뼈대 + 설정 항목 개별 symlink
mkdir -p ~/.claude/plugins
for item in agent-memory agents CHANGELOG.md claude-powerline.json CLAUDE.md \
            commands docs hooks output-styles rules settings.json skills workflows README.md; do
  ln -s "$REPO/$item" ~/.claude/"$item"
done
for item in blocklist.json installed_plugins.json known_marketplaces.json README.md; do
  ln -s "$REPO/plugins/$item" ~/.claude/plugins/"$item"
done
# sessions/, cache/, daemon/ 등 런타임 디렉터리는 Claude Code가 첫 실행 시 알아서 만든다 — 미리 만들 필요 없음

# 3. 플러그인 설치 (settings.json의 enabledPlugins 기준)
claude
/plugin marketplace add rhuss/cc-rhuss-marketplace
/plugin install superpowers@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install swift-lsp@claude-plugins-official
/plugin install last30days@last30days-skill
/plugin install claude-powerline@claude-powerline
/reload-plugins

# 4. 글로벌 스킬/에이전트/커맨드/훅은 각 디렉터리에 포함되어 있음 (별도 작업 불필요)
```

새 설정 폴더/파일을 저장소에 추가했다면, 2단계의 `for` 목록에도 이름을 추가해야 `~/.claude`에서
보인다.

## 워크플로우 요약

| 시나리오 | 커맨드 |
|---------|--------|
| 로컬/PR diff 리뷰 | `/review` |
| PR 생성 | `/pr` |
| 새 기능 구현 (브레인스토밍부터) | `superpowers:brainstorming` → `superpowers:writing-plans` → `superpowers:test-driven-development` |
| 신규 기능 개발 (spec부터 구현·리뷰까지 원클릭) | `/speckit-spex-brainstorm` → `/speckit-spex-ship` — [`docs/spex-ship-guide.md`](docs/spex-ship-guide.md) |
| 버그 수정 | `superpowers:systematic-debugging` → `superpowers:test-driven-development` |
