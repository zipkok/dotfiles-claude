# skills/

전역 스킬(`~/.claude/skills/`). 프로젝트에 종속되지 않고 모든 저장소에서 사용 가능하다.

| 디렉터리 | 역할 |
|----------|------|
| `agent-creator/` | 서브에이전트(`agents/*.md`) 생성·검증·평가(문법 검증, 실행 품질 리뷰, 트리거 정확도 최적화) |
| `directory/` | `/directory <path>` — Repository 디렉터리 기준으로 작업 디렉터리 변경 |
| `doc-review/` | 영어 문서를 6개 디멘션(구조/문법/가독성/재현성/용어/톤)으로 병렬 리뷰해 하나의 리포트로 수렴 |
| `eli5/` | 대상 청중(나이·학년·직무·관계)에 맞춰 개념·코드·에러를 눈높이 설명으로 변환 |
| `jd-analyze/` | `jds/` 폴더의 채용공고를 분석해 `analysis/`에 필요 기술·공부 방향 저장 |
| `ship-discussion/` | 논쟁적·모호한 주제를 소크라테스식 문답으로 정리해 결론 도출 (`docs/rfc/`에 결과 저장) |
| `skill-creator/` | 스킬 생성·개선·평가(eval, 벤치마크, 트리거 정확도 최적화) |
| `unity-mcp-skill/` | Unity Editor MCP 오케스트레이션 (GameObject·씬·테스트 자동화) |
| `wiki-ingest/` | 소스(링크·텍스트·파일)를 LLM Wiki에 인제스트 |
| `wiki-lint/` | LLM Wiki 건강 점검(중복·누락·구조 정리) |
| `wiki-query/` | LLM Wiki 기존 지식에 대한 질의 응답 |

각 스킬의 상세 트리거 조건과 사용법은 해당 디렉터리의 `SKILL.md` 참조.
