# Ship / Ideation 프레임워크 설계

작성일: 2026-07-14
원본: `llm_wiki/LLM_Wiki/wiki/ideation/docs/2026-07-11-ship-ideation-framework-design.md` (2026-07-11 작성, 이 문서는 dotfiles-claude 구현 관점으로 포팅)

## 배경 / 목적

- 목적별로 반복되는 작업(수집·논의·개발)을 spec부터 review까지 **원클릭(OneClick)**으로 진행하는 파이프라인 프레임워크가 필요했다. 이를 "Ship"이라 부른다.
- 선행 사례: Claude Code spex 플러그인의 `/speckit-spex-ship` — spec→clarify→plan→tasks→implement→review→finish를 게이트로 묶은 9단계 원클릭 실행 (자세한 내용은 llm_wiki `spex-ship-pipeline` 참조). Ship 프레임워크는 이 패턴을 LLM Wiki 목적에 맞게 3종으로 특화한 것이며, 실제 구현 대상은 이 저장소(dotfiles-claude)다.
- 설치 위치: 전역 (`~/.claude/`, 원본은 dotfiles-claude 저장소) — 특정 프로젝트에 종속되지 않음. 기존 `pr`/`review` 커맨드·에이전트와 같은 배치 원칙을 따른다.

## 스코프

- **포함**: 3종 Ship(ship-insight/ship-discussion/ship-develop) 파이프라인의 단계 정의(agent/role/persona/skill), 각 단계 게이트 동작, 구현 아티팩트(skill/harness/template/hook) 방향.
- **제외**: 실제 구현(스킬 파일, Workflow 스크립트, 훅 로직 작성)은 이 문서의 범위 밖 — 별도 세션에서 `superpowers:writing-plans`를 통해 진행한다. 이 문서는 설계만 기록한다.

## Ship 공통 정의

**Ship** = 목적별 산출물을 정해진 단계로 원클릭 진행하는 파이프라인. 각 단계는 4개 필드로 정의한다.

| 필드 | 의미 |
|------|------|
| agent | 이 단계를 실행하는 주체 (기존 subagent_type 또는 신규 정의) |
| role | 이 단계가 파이프라인에서 하는 기능 |
| persona | 실행 시 취해야 할 태도·관점 |
| skill | 실제로 호출하는 Skill 또는 사고 도구 (thinking-tools 포함) |

3종의 Ship:

| Ship | 문서 유형 | 단계 수 | 단계 |
|------|----------|---------|------|
| ship-insight | 수집 문서 | 4 | spec → plan → result → review |
| ship-discussion | 논의 문서 | 4 | spec → plan → result → review |
| ship-develop | 개발 문서 | 7 | spec → review-spec → plan → review-plan → test-scenarios → implement → review |

## ship-insight (수집 문서)

목표는 auto-research에 가깝다. 이 환경엔 이미 `deep-research` skill(fan-out 검색→fetch→adversarial verify→synthesize를 내부 수행하는 멀티에이전트 harness)이 있으므로, ship-insight는 이를 통째로 재구현하지 않고 **실행 엔진으로 위임**한다. 대신 각 단계에 LLM Wiki 고유 사고 도구를 명시적으로 배치해, 범용 deep-research와 차별화되는 wiki 통합 지점을 만든다.

| 단계 | role | persona | skill |
|------|------|---------|-------|
| spec | 조사 질문 정의 + 중복 체크 | 회의적 리서처 | `wiki-query`(기존 위키 확인) + `first-principles`(가정 의심) |
| plan | 조사 범위·소스 전략 | 체계적 기획자 | `mece`(범위 누락 점검) |
| result | 실제 수집·검증·종합 | 객관적 분석가 | `deep-research`(엔진으로 위임) → 결과를 `wiki-ingest` 규칙대로 sources/wiki 페이지화 |
| review | wiki 통합 검증 | 비판적 리뷰어 | `rubber-duck` + `steel-man`(자가검증) + CLAUDE.md 연결질문·긴장감지 규칙 적용 + index.md/changelog 갱신 확인 |

`result`가 deep-research의 fan-out/fetch/verify/synthesize를 감싸는 위임 단계이므로, `review`는 그 내부 사실검증과 중복되지 않는 **wiki 통합 전용 게이트**로 정의한다 (중복 방지·모순 콜아웃·다른 도메인과의 연결).

## ship-discussion (논의 문서)

논쟁적·모호한 주제를 소크라테스식 문답으로 정리해 결론을 도출한다.

| 단계 | role | persona | skill |
|------|------|---------|-------|
| spec | 논점 수집·구조화 | 소크라테스식 문답자 | `superpowers:brainstorming` |
| plan | 질문 트리·진행 순서 설계 | 중립적 사회자 | `mece`(쟁점 분류) |
| result | 실제 문답 진행, 결론 도출 | 소크라테스식 대화자 (단정하지 않고 질문으로 파고듦) | `devils-advocate` |
| review | 결론 검증 | 비판적 리뷰어 | `steel-man` + `decision-review` |

## ship-develop (개발 문서)

spex의 9단계와 비교해 두 가지가 다르다: (1) test-scenarios를 명시적 단계로 분리해 TDD를 강제한다 — spex엔 없는 요소. (2) 팀·PR 기반 협업 게이트(clarify 별도 단계, finish/merge)는 1인 워크플로우에 과할 수 있어 제외한다. 대신 spec/plan 뒤에는 spex와 동일한 밀도로 게이트를 둔다.

| 단계 | role | persona | skill |
|------|------|---------|-------|
| spec | 요구사항 정의 | 꼼꼼한 스펙 작성자 | `superpowers:brainstorming` |
| review-spec | 스펙 자가검증 게이트 | 회의적 검토자 | brainstorming의 Spec Self-Review(placeholder·모순·범위·모호성 체크) |
| plan | 구현 계획 | 신중한 설계자 | `superpowers:writing-plans` |
| review-plan | 계획 타당성 게이트 | 실패 시나리오 예측자 | `pre-mortem` |
| test-scenarios | 테스트 설계 (TDD) | 엣지케이스 헌터 | `superpowers:test-driven-development` |
| implement | 실제 구현 | 실용적 엔지니어 | `superpowers:test-driven-development`(RED-GREEN-REFACTOR) |
| review | 코드 리뷰 | 깐깐한 시니어 | `code-review` skill |

게이트(review-spec, review-plan)는 실패 시 이전 단계로 피드백과 함께 되돌아가는 **최대 2회 재시도 루프**로 설계한다 (spex의 자동 수정 루프 패턴 차용, spex는 3라운드).

### spex 9단계와의 차이 요약

| 항목 | spex ship (9단계) | ship-develop (7단계) |
|------|-------------------|----------------------|
| clarify | 별도 단계 | spec 단계에 흡수 (질문으로 즉시 해소) |
| 중간 게이트 | review-spec, review-plan | 동일하게 유지 |
| tasks 분리 | plan과 tasks 별도 | plan에 통합 |
| TDD 시나리오 | 명시적 단계 없음 | test-scenarios로 명시 분리 (spex엔 없음) |
| finish/PR | 명시적 finish 단계 | 없음 — 1인 워크플로우 가정, review로 종료 |

## 구현 로드맵 (설계만 — 실제 구현은 별도 단계)

이 저장소(dotfiles-claude) 기준 구현 아티팩트 방향:

| 아티팩트 | 내용 | 배치 위치 (이 저장소 기준) |
|----------|------|--------------------------|
| skill | `/ship-insight` 등 slash-invocable Skill | `skills/ship-insight/`, `skills/ship-discussion/`, `skills/ship-develop/` |
| harness | Workflow 스크립트 — 단일 인스턴스가 순차 단계를 통과하는 체인(fan-out 아님), 게이트는 schema 기반 pass/fail + 재시도 루프 | 각 skill 내부 또는 `.claude/workflows/` |
| template | 각 단계 출력 파일의 고정 양식 | 각 skill의 `templates/` 하위 마크다운 스켈레톤 |
| hook | 게이트 통과 전 다음 단계 진입을 막는 PreToolUse 훅 | `hooks/` — 구체 로직은 구현 단계에서 `update-config` skill로 설계 |

실제 파일 작성은 이 문서의 범위 밖이며, 추후 `superpowers:writing-plans`를 통해 별도 세션에서 진행한다.

## 위키 반영 (llm_wiki, 완료)

- `wiki/ideation/index.md` + `ship-insight/`, `ship-discussion/`, `ship-develop/` 각각 `index.md` + 단계별 문서
- 각 `index.md`에는 파이프라인 흐름을 보여주는 ASCII 아키텍처 다이어그램 포함
- `CLAUDE.md` 도메인 표에 Ideation 도메인 추가
- `wiki/index.md`에 `## Ideation` 섹션 신설

## 미해결 / 셋업 필요

- 3종 Ship 모두 실제 skill/harness/template/hook 구현 필요 — 이 문서는 설계만 포팅한 상태.
- 게이트 재시도 루프(review-spec, review-plan)의 schema 기반 pass/fail 판정 로직 미정 — 구현 단계에서 확정.
- 구현 순서(ship-insight/discussion/develop 중 무엇을 먼저 만들지) 미정.
