# agents/

메인 대화가 검색/코드/리뷰 작업을 위임하는 서브에이전트 정의 (`docs/agent-harness-design.md` — "서브에이전트·백그라운드 위임").

| 파일 | 역할 |
|------|------|
| `config-review.md` | git diff / PR diff를 정확성(스키마·문법·값 범위) 위주로 리뷰. SRE 운영 설정 PR 대상 |
| `pr-author.md` | diff를 분석해 Conventional Commits 제목과 정해진 목차의 PR 본문 작성, 승인 후 PR 생성 |
| `exec-interviewer.md` | 경영진 관점 인터뷰 시뮬레이션 |
| `tech-interviewer.md` | 기술 인터뷰 시뮬레이션 |

`config-review`/`pr-author`는 `commands/review.md`, `commands/pr.md`를 통해 호출된다. 설계 배경은 `docs/specs/2026-06-21-git-review-pr-agent-design.md` 참조.
