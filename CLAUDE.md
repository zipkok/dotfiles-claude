# Global Rules

모든 프로젝트에 공통 적용되는 규칙.

## 프로젝트의 CLAUDE.md

- 요청하는 내용은 다음에도 적용될 수 있도록 CLAUDE.md에 업데이트

## 워크플로우

**spex + superpowers** 기반 개발 파이프라인.

### 원칙

- 수정 전 관련 코드를 먼저 읽고 파악
- 요청에 적합한 subagent 적극 제안 (Explore, Plan, Agent 등)
- implement는 **반드시** `superpowers:test-driven-development` 스킬을 호출한다. 규모와 무관하게 항상 TDD (RED → GREEN → REFACTOR). 사용자가 명시적으로 "TDD 안 해"라고 할 때만 해제
- 리뷰 실패 시 이전 단계로 돌아가기 (`spex:evolve` 또는 해당 단계 재실행)
- superpowers 산출물은 specify 디렉토리 구조에 맞춘다:
  - brainstorming 결과 → `brainstorm/` (spex:ship 입력과 일치)
  - 그 외 산출물 → `specs/[NNN-feature]/` 하위
- 다음 단계 실행 시 이전 산출물을 자동 참조한다:
  - specify 실행 시 → `brainstorm/` 에서 최신 파일을 읽고 입력으로 사용
  - plan/tasks/implement → 브랜치 기반 `specs/*/` 자동 탐지 (specify CLI 내장)

### 사용자 커맨드

| 순서 | 커맨드 | 출처 | 설명 |
|------|--------|------|------|
| 0 | `/init-project <name>` | 커스텀 스킬 | 프로젝트 생성 + spex 초기화 (최초 1회, 재시작 필요) |
| 1 | `superpowers:brainstorming` | superpowers | 아이디어 정리, 요구사항 탐색 → brainstorm 파일 생성 |
| 2 | `/speckit-git-feature` | specify CLI | feature 브랜치 생성 (main 보호 hook 때문에 작업 전 필수) |
| 3 | `/speckit-specify` | specify CLI | 스펙 작성 |
| 4 | `/speckit-plan` | specify CLI | 기술 계획 |
| 5 | `/speckit-tasks` | specify CLI | 작업 분할 |
| 6 | `/speckit-implement` | specify CLI | TDD 기반 구현 |
| 7 | `superpowers:finishing-a-development-branch` | superpowers | CHANGELOG 업데이트 → merge/PR 결정 |

- 0은 프로젝트 시작 시 1회만. 1~7은 기능마다 반복
- 각 단계 사이에 품질 게이트가 자동 실행됨

### 규모별 가이드라인

brainstorming 후 규모에 맞는 다음 단계를 제안한다. "실행 방식 선택" 대신 아래 기준을 따른다.

| 규모 | 예시 | 흐름 | specify 필요 |
|------|------|------|:----------:|
| 🔴 버그 수정 | 1줄 수정, 오타 | brainstorming → git-feature → implement → finishing | ❌ |
| 🟡 작은 기능 | API 엔드포인트 1개 | brainstorming → git-feature → implement → finishing | ❌ |
| 🟢 일반 기능 | 새 페이지, 모듈 | brainstorming → git-feature → specify → plan → tasks → implement → finishing | ✅ |
| 🔵 대규모 기능 | 아키텍처 변경 | brainstorming → git-feature → specify → plan → tasks → implement → finishing + constitution | ✅ |

- 🔴🟡: brainstorming이 충분한 스펙 역할. review-code의 스펙 준수 체크는 brainstorm 파일 기준
- 🟢🔵: 정식 스펙(spec.md)이 필요. review-code가 스펙 준수율 검증

### Claude 자동 호출

#### trait overlay 자동 실행 (Skill 도구로 호출하지 않음 — speckit 명령어 실행 시 trait가 자동 부착)

| 시점 | 실행되는 것 | 출처 | 설명 |
|------|-----------|------|------|
| specify 후 | `spex:review-spec` | superpowers trait overlay | 스펙 품질 게이트 |
| plan+tasks 후 | `spex:review-plan` | superpowers trait overlay | 계획 품질 게이트 |
| implement 후 | `spex:review-code` | superpowers + deep-review trait overlay | 스펙 준수 + 5-agent 리뷰 + 자동 수정 (최대 3회) |
| review 통과 후 | `spex:verification` | superpowers trait overlay | 테스트 → 코드 위생 → 드리프트 체크 → 최종 판정 |

#### Claude 판단으로 호출 (CLAUDE.md 원칙에 의해 강제 또는 제안)

| 시점 | 커맨드 | 출처 | 설명 |
|------|--------|------|------|
| implement 시 | `superpowers:test-driven-development` | superpowers | TDD 기본 적용 (CLAUDE.md 원칙에 의해 강제) |
| implement 시 | `superpowers:dispatching-parallel-agents` | superpowers | 독립적인 태스크 2개 이상일 때 병렬 subagent 실행 |
| tasks 후 | `/speckit-analyze` | specify CLI | review-plan 실패가 잦을 때 정합성 사전 검증 제안 |
| PR 리뷰 수렴 시 | `superpowers:receiving-code-review` | superpowers | 외부 리뷰 피드백의 기술적 타당성 검증 후 반영 |
| - | `/speckit-clarify` | specify CLI | 스펙이 모호하거나 누락이 있을 때 제안 |
| - | `/speckit-constitution` | specify CLI | 기능 2개 이상 + constitution 미존재 시 제안 |
| - | `superpowers:systematic-debugging` | superpowers | 버그/테스트 실패 시 제안 |

### 리뷰 실패 시

| 실패 지점 | 대응 |
|----------|------|
| `review-spec` 실패 | → `/speckit-specify` 재실행 또는 `spex:evolve`로 스펙 보정 |
| `review-plan` 실패 | → `/speckit-plan` 재실행 |
| `review-code` 실패 (준수율 < 95%) | → `spex:evolve`로 스펙-코드 정합성 보정 |
| `review-code` 실패 (Critical 잔존) | → 수동 수정 후 `spex:review-code` 재실행 |
| `verification` 실패 | → 테스트 수정 → verification 재실행 |

### spex:ship (원클릭)

`spex:ship --ask smart` — brainstorm 파일을 입력으로 9단계 자동 실행. ship은 자체 SKILL.md를 따르므로 CLAUDE.md 설정과 무관하게 동작한다.
