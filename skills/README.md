# skills/

전역 스킬(`~/.claude/skills/`). 프로젝트에 종속되지 않고 모든 저장소에서 사용 가능하다.

| 디렉터리 | 역할 |
|----------|------|
| `directory/` | `/directory <path>` — Repository 디렉터리 기준으로 작업 디렉터리 변경 |
| `jd-analyze/` | `jds/` 폴더의 채용공고를 분석해 `analysis/`에 필요 기술·공부 방향 저장 |
| `skill-creator/` | 스킬 생성·개선·평가(eval, 벤치마크, 트리거 정확도 최적화) |
| `unity-mcp-skill/` | Unity Editor MCP 오케스트레이션 (GameObject·씬·테스트 자동화) |
| `wiki-ingest/` | 소스(링크·텍스트·파일)를 LLM Wiki에 인제스트 |
| `wiki-lint/` | LLM Wiki 건강 점검(중복·누락·구조 정리) |
| `wiki-query/` | LLM Wiki 기존 지식에 대한 질의 응답 |

각 스킬의 상세 트리거 조건과 사용법은 해당 디렉터리의 `SKILL.md` 참조.
