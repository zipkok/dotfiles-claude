# docs/adrs/

Architecture Decision Record — 결정 **1개**를 짧게 기록하는 문서 (Michael Nygard 형식). LLM Wiki
`wiki/me/thinking-tools/adr.md`의 컨벤션을 그대로 따른다.

## 구조

| 섹션 | 내용 |
|------|------|
| Title | `0001-use-postgres-for-orders.md` 같은 한 줄 |
| Status | Accepted / Proposed / Deprecated / Superseded by [#0002] |
| Context | 왜 결정이 필요한가 (배경·제약·요구사항) |
| Decision | 무엇을 결정했나 (능동태) |
| Consequences | 결과 — 좋은 점·나쁜 점·트레이드오프 |

## 규칙

- **결정 1개 = 파일 1개** (`0001-...md`, `0002-...md`)
- 번호는 순차. 한 번 매기면 재사용하지 않는다
- **작성 후 변경 금지** — 결정이 뒤집히면 새 ADR을 만들고 이전 것은 Status에 `Superseded by [#NNNN]` 표시
- 짧게 — 1~2페이지. 길어지면 `docs/specs/`의 설계 문서 영역

## `docs/specs/`와의 관계

| | `docs/specs/` | `docs/adrs/` |
|---|---|---|
| 규모 | 기능/변경 단위 전체 설계 | 결정 1개 |
| 시점 | 구현 전 | 결정 직후 (구현 중·후 포함) |
| 누적 | 기능 단위 | 순차 번호 시리즈 |

| 파일 | 내용 |
|------|------|
| `0001-harness-loop-engineering-project-scope.md` | 하네스/루프 엔지니어링 토대를 프로젝트 단위(dotfiles-claude)에 두고 `docs/specs/` + `docs/adrs/` 구조를 채택한 결정 |
