# dotfiles-claude

Claude Code 하네스 설정 파일. 새 노트북에서 클론하면 동일한 개발 환경을 바로 사용할 수 있다.

## 구조

```
~/.claude/
├── CLAUDE.md              # 글로벌 워크플로우 (spex + superpowers)
├── settings.json          # hooks, 플러그인, MCP 서버
├── rules/                 # Claude 행동 규칙 (자동 로드)
│   ├── conventions.md     # 언어, 문서 작성, 코딩 스타일
│   ├── git.md             # 커밋 컨벤션
│   ├── documentation.md   # docs/, CHANGELOG
│   └── work-style.md      # 진행 상황 표시 포맷
├── hooks/                 # 자동 실행 스크립트
│   ├── pre-commit-lint.sh # 커밋 전 lint
│   ├── protect-sensitive-files.sh  # .env 등 수정 차단
│   ├── protect-main-branch.sh     # main 직접 커밋 차단
│   └── block-build-artifacts.sh   # node_modules 등 쓰기 차단
├── agents/                # 에이전트
│   ├── exec-interviewer.md
│   └── tech-interviewer.md
└── skills → ~/Repository/claude/global/skills  # 글로벌 스킬
```

## 플러그인

| 플러그인 | 마켓플레이스 | 역할 |
|---------|------------|------|
| superpowers (v5.0.7) | claude-plugins-official | TDD, 규율, 14개 스킬 |
| spex (v4.0.0) | cc-rhuss-marketplace | SDD, speckit CLI 통합, 13개 스킬 |

## 새 노트북에서 복원

```bash
# 1. 클론
git clone git@github.com:<username>/dotfiles-claude.git ~/.claude

# 2. 플러그인 설치
claude
/plugin marketplace add rhuss/cc-rhuss-marketplace
/plugin install superpowers@claude-plugins-official
/plugin install spex@cc-rhuss-marketplace
/reload-plugins

# 3. 글로벌 스킬 (skills 심볼릭 링크가 가리키는 대상)
# ~/Repository/claude/global/skills/ 디렉토리가 필요
```

## 워크플로우 요약

| 시나리오 | 커맨드 |
|---------|--------|
| 프로젝트 시작 | `/init-project <name> [type]` → `/speckit-constitution` |
| 새 기능 (자동) | `spex:ship --ask smart` |
| 새 기능 (수동) | `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` |
| 버그 수정 | `superpowers:systematic-debugging` → `superpowers:test-driven-development` |
