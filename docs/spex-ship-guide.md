# spex ship 사용 가이드

## 오버뷰

- 신규 기능 개발을 spec부터 코드 리뷰까지 자동 진행하는 가이드.
- `ship-develop` 스킬은 만들지 않는다 — `/speckit-spex-ship`를 직접 쓴다.
- 이유: spex가 게이트·재시도 루프까지 포함한 완전 자동 파이프라인을 이미 제공한다. 래퍼 스킬을
  얹어도 이득은 작고, spex 업데이트마다 같이 손봐야 하는 부담만 커진다.
- 대신 이 문서로 사용법과 매번 답해야 할 선택지를 명시해둔다.

## 사전조건

- `settings.json`에서 `spex@cc-rhuss-marketplace`가 `true`인지 확인.

## 스텝별 가이드

### 1. `/speckit-spex-init`

- **방법**: 프로젝트마다 최초 1회 실행. 3개 질문에 매번 답한다(건너뛰는 옵션 없음):
  - **Quality**: `spex-gates`, `spex-deep-review` 선택. `spex-teams`는 선택 해제(실험적 기능, 안 씀).
  - **Workflow**: `spex-worktrees`/`spex-collab`/`spex-detach` — 선택 사항. worktree 격리를
    원하면 `spex-worktrees`만 추가 선택.
  - **Permissions**: `Standard` 선택(권장).
- **주의**: 재실행해도 이 3개 질문을 매번 다시 받는다. 위 선택지를 그대로 반복하면 된다.

### 2. `/speckit-spex-brainstorm`

- **방법**: 대화로 아이디어를 정리한다. `brainstorm/{NN}-{slug}.md`를 생성한다.
- **주의**: ship의 8단계에 포함되지 않는 별도 커맨드다. 이 파일이 없으면 ship이 실행을 거부한다.

### 3. `/speckit-spex-ship [brainstorm-file] --ask smart`

- **방법**: 아래 8단계를 순서대로 자동 진행한다(스킵·재정렬 불가).

  | # | 단계 | 실행 방식 | 대화형? |
  |---|------|----------|---------|
  | 0 | specify | 인라인 | 아니오 |
  | 1 | clarify | 인라인 | `ask=always`만 |
  | 2 | review-spec | 포크된 독립 게이트 | 아니오(findings 따라 일시정지) |
  | 3 | plan | 인라인 | 아니오 |
  | 4 | tasks | 인라인 | 아니오 |
  | 5 | review-plan | 포크된 독립 게이트 | 아니오(findings 따라 일시정지) |
  | 6 | implement | 포크된 서브에이전트 | 아니오(체크포인트 fail 반복 시 정지) |
  | 7 | review-code | 포크된 독립 게이트 | 아니오(compliance <100%면 evolve로) |

- **`--ask` 레벨**(기본 `smart`)이 findings 자동수정 범위를 정한다:

  | 레벨 | Unambiguous | Ambiguous | Blocker |
  |------|---|---|---|
  | `always` | 일시정지 | 일시정지 | 일시정지 |
  | `smart`(기본) | 자동수정 | 일시정지 | 일시정지 |
  | `never` | 자동수정 | 자동수정 | 일시정지 |

  재시도는 단계당 최대 2회. 그래도 안 풀리면 레벨 무관하게 정지.

- **주의**: 시작 시 dirty 작업 트리를 "WIP: save before ship"로 확인 없이 자동 커밋한다.
- **주의**: `Workflow` 도구를 쓰지 않는다 — `/workflows` 진행 화면에 안 뜬다. 일반 서브에이전트
  실행으로만 보인다.

### 4. 종료 선택

- **방법**: 8단계 완료 후 "Submit PR" / "Merge directly" / "Stop here" 중 하나를 고른다.
- **주의**: spex 기본 추천은 "Submit PR"이지만, 이 저장소는 리뷰까지만 자동 진행하고 병합·PR은
  직접 한다 — **"Stop here"를 선택한다.**

### 5. 산출물 확인

- **위치**: `brainstorm/{NN}-{slug}.md`, `specs/<feature>/{spec,plan,tasks,research,data-model}.md`
  — spec-kit 고정 경로, 커스터마이즈 불가.
- **주의**: review-spec/review-plan/review-code 게이트 리포트는 파일로 안 남는다(콘솔·서브에이전트
  반환 텍스트뿐). 기록이 필요하면 그 세션에서 직접 복사해둔다.

## 원 설계 문서와의 관계

`docs/specs/2026-07-14-ship-ideation-framework-design.md`의 `ship-develop` 항목(스킬 구현 계획)은
이 가이드로 대체됐다. 원문은 이력 보존을 위해 수정하지 않는다.
