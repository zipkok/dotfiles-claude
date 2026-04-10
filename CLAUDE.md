# Global Rules

모든 프로젝트에 공통 적용되는 규칙.

## 프로젝트의 CLAUDE.md

- 요청하는 내용은 다음에도 적용될 수 있도록 CLAUDE.md에 업데이트

## 워크플로우

**spex + superpowers** 기반 개발 파이프라인.

### 원칙

- 큰 기능은 바로 코딩하지 말고 `/plan`으로 계획부터
- 수정 전 관련 코드를 먼저 읽고 파악
- 요청에 적합한 subagent 적극 제안 (Explore, Plan, Agent 등)

### 사용자 커맨드

| 순서 | 커맨드 | 설명 |
|------|--------|------|
| 1 | `/init-project <name> [type]` | 프로젝트 생성 (최초 1회) |
| 2 | `/speckit-constitution` | 프로젝트 원칙 정의 (최초 1회) |
| 3 | `/speckit-specify` | 스펙 작성 |
| 4 | `/speckit-plan` | 기술 계획 |
| 5 | `/speckit-tasks` | 작업 분할 |
| 6 | `/speckit-implement` | 구현 |

- 1~2는 프로젝트 시작 시 1회만. 3~6은 기능마다 반복
- 필요한 단계만 선택 가능 (예: 간단한 기능은 3 → 6만)
- 구현 이후 리뷰/검증은 Claude가 자동 호출

### Claude 자동 호출

| 순서 | 커맨드 | 설명 |
|------|--------|------|
| 7 | `spex:review-code` | 구현 완료 시 자동 |
| 8 | `spex:verification` | 리뷰 통과 시 자동 |
| - | `superpowers:test-driven-development` | TDD가 적합할 때 제안 |
| - | `superpowers:systematic-debugging` | 버그/테스트 실패 시 제안 |

### 새 기능 (자동)

`spex:ship --ask smart` — 아래 9단계를 원클릭 실행.

| 순서 | 커맨드 | 설명 |
|------|--------|------|
| 0 | `/speckit-specify` | 스펙 작성 |
| 1 | `/speckit-clarify` | 명확화 |
| 2 | `/spex:review-spec` | 스펙 품질 게이트 |
| 3 | `/speckit-plan` | 기술 계획 |
| 4 | `/speckit-tasks` | 작업 분할 |
| 5 | `/spex:review-plan` | 계획 품질 게이트 |
| 6 | `/speckit-implement` | 구현 + superpowers TDD overlay |
| 7 | `/spex:review-code` | 5-agent 리뷰 + deep-review |
| 8 | `/spex:verification-before-completion` | 최종 검증 (stamp) |
