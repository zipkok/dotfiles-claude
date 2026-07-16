# commands/

슬래시 커맨드 정의. 각 커맨드는 `agents/`의 서브에이전트를 오케스트레이션한다.

| 파일 | 커맨드 | 동작 |
|------|--------|------|
| `review.md` | `/review` | 로컬 변경 또는 PR diff를 자동 판별해 `config-review` 에이전트로 리뷰 (읽기 전용, 반복 실행 안전) |
| `pr.md` | `/pr` | `pr-author` 에이전트로 Title/Description 작성 → 사용자 승인 → 브랜치 push · PR 생성 (쓰기 작업, 승인 게이트 필수) |
