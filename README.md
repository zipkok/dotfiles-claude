# dotfiles-claude

Claude Code 하네스 설정 파일. 새 노트북에서 클론하면 동일한 개발 환경을 바로 사용할 수 있다.

## 구조

### 폴더 구조

```
~/.claude/
├── agents/                # 에이전트
├── agent-memory/          # 파일 기반 장기 기억 (실험 로그, 오류 기록, TODO)
├── commands/              # 슬래시 커맨드
├── docs/                  # 프로젝트 지식 축적
│   ├── assets/            # 도식 이미지
│   └── specs/             # 설계 문서 (spec, plan, review)
├── hooks/                 # 자동 실행 스크립트
├── output-styles/         # 출력 스타일 (진행 상황 표시 포맷 등)
├── plugins/               # 플러그인 상태 파일 (CLI가 관리)
├── rules/                 # Claude 행동 규칙 (자동 로드)
├── skills/                # 글로벌 스킬
│   ├── directory/
│   ├── jd-analyze/
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

**rules/** — Claude 행동 규칙 (자동 로드)

| 파일 | 역할 |
|------|------|
| `conventions.md` | 언어, 문서 작성, 코딩 스타일 |
| `git.md` | 커밋 컨벤션 |
| `documentation.md` | `docs/`, `CHANGELOG.md` 작성 규칙 |
| `work-behavior.md` | 작업 단위, 확인 요청 기준 |
| `ai-coaching.md` | AI 사용 코칭 (현재 비활성화) |

**hooks/** — 자동 실행 스크립트

| 파일 | 역할 |
|------|------|
| `pre-commit-lint.sh` | 커밋 전 lint |
| `protect-sensitive-files.sh` | `.env` 등 수정 차단 |
| `protect-main-branch.sh` | main 직접 커밋 차단 |
| `block-build-artifacts.sh` | `node_modules` 등 쓰기 차단 |
| `require-tests.sh` | 테스트 없는 커밋 차단 |
| `notify-claude-md-update.sh` | CLAUDE.md 갱신 알림 |

**agents/** — 에이전트

| 파일 | 역할 |
|------|------|
| `config-review.md` | 설정 diff 리뷰 (SRE 대상) |
| `pr-author.md` | PR Title/Description 작성·생성 |
| `exec-interviewer.md` | 임원 면접관 — 문화 적합성·성장 가능성·리더십 평가 |
| `tech-interviewer.md` | 기술 면접관 — JD 기반 기술 면접 질문·답변 평가 |

**commands/** — 슬래시 커맨드

| 파일 | 역할 |
|------|------|
| `review.md` | `/review` — 로컬/PR diff 정확성 리뷰 |
| `pr.md` | `/pr` — PR 생성 |

**skills/** — 글로벌 스킬 (각 `<name>/SKILL.md`)

| 스킬 | 역할 |
|------|------|
| `directory` | 작업 디렉터리 변경 (`/directory <path>`) |
| `jd-analyze` | 채용공고 분석 → 필요 기술/공부 방향 저장 |
| `skill-creator` | 스킬 생성·개선·성능 측정 |
| `unity-mcp-skill` | Unity Editor MCP 오케스트레이션 |
| `wiki-ingest` | LLM Wiki 인제스트 |
| `wiki-lint` | LLM Wiki 건강 점검 |
| `wiki-query` | LLM Wiki 질의 응답 |

**workflows/** — Workflow 스크립트 (`*.js`)

아직 실제 워크플로우 스크립트는 없음 — 필요해지면 이 디렉터리에 추가한다.

**agent-memory/** — 파일 기반 장기 기억

아직 실제 기록은 없음 — 필요해지면 이 디렉터리에 추가한다.

**output-styles/**

| 파일 | 역할 |
|------|------|
| `work-style.md` | 프로그레스바·테이블·이모지로 진행 상황을 표시하는 출력 스타일 |

**plugins/** — 플러그인 상태 파일 (직접 편집 대신 `/plugin` 커맨드로 관리)

| 파일 | 역할 |
|------|------|
| `known_marketplaces.json` | 등록된 마켓플레이스 목록 |
| `installed_plugins.json` | 설치된 플러그인 버전·경로·설치 시각 |
| `blocklist.json` | 차단된 플러그인 목록 |

**docs/** — 프로젝트 지식 축적

| 파일 | 역할 |
|------|------|
| `hook-lifecycle.md` | Claude Code hook 생명주기 도식 |
| `agent-harness-design.md` | 하네스 개념 정리, 이 저장소와의 대응 |
| `claude-vs-codex-harness-design.md` | Claude vs Codex 하네스 설계 비교 |

**docs/assets/** — `docs/` 문서가 참조하는 도식 이미지

| 파일 | 사용 문서 |
|------|----------|
| `claude-code-project-structure.svg` | `agent-harness-design.md` |
| `prompt-context-harness-loop-engineering.svg` | `agent-harness-design.md` |

**docs/specs/** — 기능/변경 단위 설계 문서 (구현 전 설계 기록)

| 파일 | 내용 |
|------|------|
| `2026-06-21-git-review-pr-agent-design.md` | `/review`, `/pr` 명령·에이전트 설계 |
| `2026-07-14-ship-ideation-framework-design.md` | LLM Wiki ship-* 프레임워크 설계 포팅 |

각 디렉터리에는 위 내용을 요약한 `README.md`가 별도로 있다.

## 플러그인

| 플러그인 | 마켓플레이스 | 활성화 | 역할 |
|---------|------------|:---:|------|
| superpowers | claude-plugins-official | ❌ | TDD, 규율, 브레인스토밍 등 스킬 모음 (현재 비활성화) |
| spex | cc-rhuss-marketplace | ❌ | SDD, speckit CLI 통합 (현재 비활성화) |
| claude-md-management | claude-plugins-official | ✅ | CLAUDE.md 감사·개선 |
| swift-lsp | claude-plugins-official | ✅ | Swift LSP 연동 |
| last30days | last30days-skill | ✅ | 최근 30일 웹/커뮤니티 리서치 |
| claude-powerline | claude-powerline | ✅ | 상태줄(powerline) 렌더링 |

## 새 노트북에서 복원

```bash
# 1. 클론
git clone git@github.com:<username>/dotfiles-claude.git ~/.claude

# 2. 플러그인 설치 (settings.json의 enabledPlugins 기준)
claude
/plugin marketplace add rhuss/cc-rhuss-marketplace
/plugin install superpowers@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install swift-lsp@claude-plugins-official
/plugin install last30days@last30days-skill
/plugin install claude-powerline@claude-powerline
/reload-plugins

# 3. 글로벌 스킬/에이전트/커맨드/훅은 각 디렉터리에 포함되어 있음 (별도 작업 불필요)
```

## 워크플로우 요약

| 시나리오 | 커맨드 |
|---------|--------|
| 로컬/PR diff 리뷰 | `/review` |
| PR 생성 | `/pr` |
| 새 기능 구현 (브레인스토밍부터) | `superpowers:brainstorming` → `superpowers:writing-plans` → `superpowers:test-driven-development` |
| 버그 수정 | `superpowers:systematic-debugging` → `superpowers:test-driven-development` |
