# hooks/

`settings.json`의 `hooks` 설정에 연결되어 도구 호출 전후에 자동 실행되는 스크립트. 모델의 판단과 무관하게 강제 적용된다 (`docs/agent-harness-design.md` — "평가자·권한은 루프 밖에").

| 파일 | 이벤트 | 동작 |
|------|--------|------|
| `pre-commit-lint.sh` | PreToolUse(Bash) | `git commit` 전 언어별 lint 자동 실행 |
| `protect-main-branch.sh` | PreToolUse(Bash) | main 브랜치 직접 커밋 경고 (차단은 아님) |
| `require-tests.sh` | PreToolUse(Bash) | 대응 테스트 파일 없는 커밋 차단 |
| `allow-curl-get.sh` | PreToolUse(Bash) | curl GET(메서드 변경·데이터 전송 플래그 없음) 자동 허용, POST/PUT/DELETE/데이터 전송은 평소대로 확인 |
| `protect-sensitive-files.sh` | PreToolUse(Write\|Edit) | `.env` 등 민감 파일 수정 경고 |
| `block-build-artifacts.sh` | PreToolUse(Write\|Edit) | `node_modules` 등 빌드 산출물 쓰기 차단 |
| `notify-claude-md-update.sh` | PostToolUse(Write\|Edit) | `CLAUDE.md` 수정 시 `claude-md-improver` 실행 안내 |

훅 생명주기 전체 흐름은 LLM Wiki `wiki/ai/claude/claude-code-hook-lifecycle.md` 참조 (2026-07-17 `docs/hook-lifecycle.md`에서 이관).
