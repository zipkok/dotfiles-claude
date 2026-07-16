# rules/

Claude Code가 모든 세션 시작 시 자동 로드하는 행동 규칙. 프로젝트별 설정이 아니라 전역(`~/.claude/`) 규칙.

| 파일 | 내용 |
|------|------|
| `conventions.md` | 언어(한국어), 문서 작성 통일 규칙, 코딩 스타일(과잉 추상화 금지) |
| `git.md` | 커밋 메시지 컨벤션 (한국어, `feat:`/`fix:`/`refactor:`/`docs:`/`test:`/`chore:`) |
| `documentation.md` | `docs/`, `docs/specs/`, `CHANGELOG.md` 작성 규칙 |
| `work-behavior.md` | 작업 단위(기능/Phase), 실패 시 질문, `cd` 승인 등 행동 규칙 |
| `ai-coaching.md` | AI 사용 코칭 메타 피드백 (현재 출력 비활성화, 평가 프레임워크는 보존) |

출력 형식(진행 상황 표시 포맷)은 규칙이 아니라 `output-styles/`에서 다룬다.
