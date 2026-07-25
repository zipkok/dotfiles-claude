# docs/

프로젝트 지식 축적 공간(`rules/documentation.md`). 설계 문서, 기술 결정, 가이드를 보관한다.

| 파일/디렉터리 | 내용 |
|------|------|
| `agent-harness-design.md` | 하네스(harness) 개념 정리와 이 저장소 구조와의 대응 |
| `spex-ship-guide.md` | `/speckit-spex-ship` 사용 가이드 — 신규 기능 개발을 spec부터 review까지 원클릭 진행 |
| `assets/` | 문서에 쓰이는 도식 이미지 |
| `specs/` | 기능/변경 단위 설계 문서, 구현 전에 먼저 기록 |
| `adrs/` | Architecture Decision Record — 결정 1개당 파일 1개, Nygard 형식 |
| `rfc/` | 여러 입장을 수렴해 합의 도출하는 논의 문서 — `ship-discussion` 스킬이 자동 생성 |

변경 이력은 문서가 아니라 저장소 루트의 `CHANGELOG.md`에 날짜별로 기록한다.

> 2026-07-17: `hook-lifecycle.md`, `claude-vs-codex-harness-design.md`는 LLM Wiki(`~/Repository/llm_wiki`)로 이관 후 삭제. 각각 `wiki/ai/claude/claude-code-hook-lifecycle.md`, `wiki/ai/claude/claude-code-vs-codex-cli.md`로 병합됨.
