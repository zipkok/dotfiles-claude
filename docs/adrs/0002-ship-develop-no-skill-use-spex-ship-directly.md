# 0002. ship-develop은 스킬로 만들지 않고 `/speckit-spex-ship`을 직접 쓴다

## Status

Accepted (2026-07-25)

## Context

`docs/specs/2026-07-14-ship-ideation-framework-design.md`는 `ship-develop`을 `ship-discussion`처럼
스킬(spec→review-spec→plan→review-plan→test-scenarios→implement→review 7단계)로 만들려 했다.
spex 플러그인(`rhuss/cc-spex`)의 `/speckit-spex-ship`을 직접 읽어보니, 이미 8단계
(specify→clarify→review-spec→plan→tasks→review-plan→implement→review-code)를 오버사이트 레벨
(`--ask`)과 포크된 독립 게이트까지 포함해 완전 자동으로 제공한다. 래퍼 스킬을 얹어도 파이프라인
로직은 추가되지 않고(전부 spex 담당), 얻는 건 산출물 재배치·게이트 리포트 영속화 정도인데 spex
업데이트마다 같이 손봐야 하는 유지보수 부담이 더 크다.

## Decision

- `skills/ship-develop/`, `workflows/ship-develop-panel.js`, 신규 에이전트, 전용 `docs/` 폴더 —
  **만들지 않는다.**
- 대신 `docs/spex-ship-guide.md` 하나로 대체: `/speckit-spex-init` → `/speckit-spex-brainstorm`
  (유일한 필수 대화형 단계) → `/speckit-spex-ship --ask smart` 사용법, 종료 시 "Stop here" 권장
  (spex 기본 추천 "Submit PR"과 다름).
- `settings.json`에서 `spex@cc-rhuss-marketplace` 활성화.

## Consequences

**좋음**: 신규 코드 0, spex 업데이트에 안 깨짐, 실제 게이트·재시도 동작을 그대로 신뢰.

**트레이드오프**:
- 게이트 리포트(review-spec/plan/code)가 파일로 안 남음(spex 정책) — 감사 기록 필요하면 수동 복사.
- `/speckit-spex-init` 확장 선택 질문을 매번 반복 답해야 함(건너뛰기 옵션 없음).
- `/workflows` 진행 화면 못 씀 — spex ship은 일반 `Agent` 도구 스폰이라 `Workflow` 트리에 안 뜸.
- 작업 트리 dirty 상태를 확인 없이 자동 커밋하는 spex 자체 동작은 막을 수 없음.
- 원 설계 문서(`docs/specs/2026-07-14-...`)의 ship-develop 항목은 이 ADR로 대체됨(원문은 유지).

## 관련

- `docs/spex-ship-guide.md`
- `docs/specs/2026-07-14-ship-ideation-framework-design.md`
- `skills/ship-discussion/` — 대조군(같은 프레임워크의 다른 항목은 스킬로 구현됨)
