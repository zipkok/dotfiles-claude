# Global Rules

모든 프로젝트에 공통 적용되는 규칙.

## 프로젝트의 CLAUDE.md

- 요청하는 내용은 다음에도 적용될 수 있도록 CLAUDE.md에 업데이트

## 워크플로우

**spex + superpowers** 기반 개발 파이프라인.

### 원칙

- 수정 전 관련 코드를 먼저 읽고 파악
- 요청에 적합한 subagent 적극 제안 (Explore, Plan, Agent 등)
- implement 시 상황에 따라 테스트 전략을 선택한다:

  | 상황 | 접근 | 스킬 |
  |------|------|------|
  | 스펙 충분 + 구현 확실 | SDD → 구현 → Test-After (스펙 기준 테스트 작성) | 테스트 직접 작성 |
  | 스펙 충분 + 구현 불확실 | SDD → TDD (테스트가 구현을 검증) | `superpowers:test-driven-development` |
  | 스펙 부족 + 탐색적 | TDD가 설계를 이끔 (테스트가 인터페이스 결정) | `superpowers:test-driven-development` |

  - 어떤 경우든 **테스트 없는 구현은 금지**
  - 판단이 애매하면 TDD 스킬을 호출한다
  - implement 시작 전 "🧪 테스트 전략: [Test-After/TDD] — 이유: [상황 판단 근거]" 선언 필수
- 리뷰 실패 시 이전 단계로 돌아가기 (`spex:evolve` 또는 해당 단계 재실행)
- **게이트 선언 규칙**: 각 단계 완료 후 다음 게이트를 반드시 선언하고 실행한다. 생략하지 마라.
  - specify 완료 → "🔒 review-spec 게이트 실행합니다" → 실행
  - plan+tasks 완료 → "🔒 review-plan 게이트 실행합니다" → 실행
  - implement 완료 → "🔒 review-code 게이트 실행합니다" → 실행
  - review 통과 → "🔒 verification 게이트 실행합니다" → 실행
  - 선언 없이 다음 단계로 넘어가는 것은 규칙 위반이다
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
| 6 | `/speckit-implement` | specify CLI | 구현 (테스트 전략은 원칙 참조) |
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

#### 품질 게이트 (게이트 선언 규칙으로 실행)

speckit 스킬의 trait overlay가 자동 실행할 수도 있지만, **자동 실행에 의존하지 말고 게이트 선언 규칙을 따른다.**

| 시점 | 게이트 | 설명 |
|------|--------|------|
| specify 후 | `spex:review-spec` | 스펙 품질 게이트 |
| plan+tasks 후 | `spex:review-plan` | 계획 품질 게이트 |
| implement 후 | `spex:review-code` | 스펙 준수 + 5-agent 리뷰 + 자동 수정 (최대 3회) |
| review 통과 후 | `spex:verification` | 테스트 → 코드 위생 → 드리프트 체크 → 최종 판정 |

#### Claude 판단으로 제안

| 시점 | 커맨드 | 설명 |
|------|--------|------|
| implement 시 | `superpowers:test-driven-development` | 구현 불확실 또는 탐색적일 때 (원칙 테이블 참조) |
| implement 시 | `superpowers:dispatching-parallel-agents` | 독립 태스크 2개 이상일 때 |
| tasks 후 | `/speckit-analyze` | review-plan 반복 실패 시 |
| PR 리뷰 수렴 시 | `superpowers:receiving-code-review` | 외부 리뷰 피드백 검증 |
| - | `/speckit-clarify` | 스펙이 모호할 때 |
| - | `/speckit-constitution` | 기능 2개 이상 + constitution 미존재 시 |
| - | `superpowers:systematic-debugging` | 버그/테스트 실패 시 |

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
