# agents/

메인 대화가 검색/코드/리뷰 작업을 위임하는 서브에이전트 정의 (`docs/agent-harness-design.md` — "서브에이전트·백그라운드 위임").

| 파일 | 역할 |
|------|------|
| `config-review.md` | git diff / PR diff를 정확성(스키마·문법·값 범위) 위주로 리뷰. SRE 운영 설정 PR 대상 |
| `pr-author.md` | diff를 분석해 Conventional Commits 제목과 정해진 목차의 PR 본문 작성, 승인 후 PR 생성 |
| `exec-interviewer.md` | 경영진 관점 인터뷰 시뮬레이션 |
| `tech-interviewer.md` | 기술 인터뷰 시뮬레이션 |
| `ship-discussion-technique-agent.md` | 지정된 사고도구 1개를 대상(쟁점 목록·계획)에 적용해 의견을 낸다 |
| `ship-discussion-position.md` | 쟁점 하나에 대해 지정된 입장을 최강 논리로 옹호한다 |
| `ship-discussion-synthesizer.md` | 여러 에이전트 결과를 devils-advocate로 검토해 하나로 수렴시킨다 |
| `doc-review-checker.md` | 영어 문서를 지정된 디멘션 1개(구조/문법/가독성/재현성/용어/톤) 관점에서만 리뷰 |
| `doc-review-synthesizer.md` | doc-review-checker 6개 결과를 중복 병합·심각도순 정렬해 하나의 리포트로 수렴 |

`config-review`/`pr-author`는 `commands/review.md`, `commands/pr.md`를 통해 호출된다. 설계 배경은 `docs/specs/2026-06-21-git-review-pr-agent-design.md` 참조. `ship-discussion-*`는 `workflows/ship-discussion-panel.js`가, `doc-review-*`는 `workflows/doc-review-panel.js`가 호출한다.
