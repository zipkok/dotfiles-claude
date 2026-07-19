# 0001. 하네스·루프 엔지니어링 토대를 프로젝트 단위(dotfiles-claude)에 두고 specs/adrs로 구조화한다

## Status

Accepted (2026-07-17)

## Context

- `docs/agent-harness-design.md`에서 정리한 하네스(harness) 개념을 실제로 다듬고, Skill·Agent를
  다양하게 설계·구현해나갈 토대가 필요했다.
- LLM Wiki에서 미완결로 남아있던 ship-discussion 토론
  (`wiki/ideation/ship-discussion/runs/2026-07-17-harness-loop-engineering-scope/`)이 정확히 이 질문을
  다뤘다: "하네스/루프 엔지니어링 토대를 글로벌(`~/.claude`)에 둘지, 프로젝트 단위(`.claude/`)에 둘지."
  3-에이전트 패널 토론 결과 4개 쟁점 모두 조건부 결론으로 끝났고, 사용자의 최종 언어화만 남아있었다:
  - 적용 범위: 도메인 특칙 없이 재사용 가능함이 실증되면 글로벌, 아직 미실증이면 프로젝트
  - 실험 안정성: 구조적으로 프로젝트 쪽이 노출 범위가 작음 (근소 우세)
  - 우선순위·충돌(concatenate): 중립적 사실, 여러 프로젝트에 걸쳐 쓸 것이 참이면 글로벌에 조건부 우위
  - 이식성: promote가 demote보다 되돌리기 쉬움 (프로젝트 우세 논거이나 저비용 여부 미검증)
- 이 토론이 놓친 사실: `dotfiles-claude`는 이미 `~/.claude`에 설정 항목별로 개별 symlink 연결돼 있다
  (`CLAUDE.md`의 "~/.claude 심볼릭 링크 구조" 참조). 즉 이 저장소는 **git 이력·리뷰·롤백이 되는
  프로젝트 저장소이면서, 동시에 런타임 효과는 이미 전역**이다. 토론이 전제한 "글로벌=모든 세션 영향 vs
  프로젝트=이 레포만 영향"이라는 이분법 자체가, 이 저장소에 한해서는 성립하지 않는다 — symlink 덕분에
  promote/demote 비용이 사실상 0이고(파일을 고치면 곧바로 전역 적용), 동시에 dotfiles-claude에서
  git으로 이력·리뷰·롤백도 그대로 확보된다.
- 별도로, `docs/specs/`는 원래 "spex 워크플로우 산출물"이라는 이름 근거로 만들어졌으나 spex 플러그인은
  현재 비활성화 상태(`README.md` 플러그인 표)라 그 근거가 사라졌다.

## Decision

- 하네스·루프 엔지니어링 토대는 `dotfiles-claude` 저장소(프로젝트 단위)에 둔다. symlink 구조 덕분에
  실질적으로는 이미 전역 적용되므로, ship-discussion이 전제한 "프로젝트냐 글로벌이냐"의 양자택일은
  이 저장소에는 적용되지 않는다는 점을 결론으로 삼는다.
- `docs/`를 두 폴더로 구조화한다:
  - `docs/specs/` — 기능/변경 단위 설계 문서, 구현 전에 먼저 기록. 이름은 유지하되 "spex 산출물"이라는
    옛 설명은 폐기.
  - `docs/adrs/` — Michael Nygard 형식의 단일 결정 기록(Title/Status/Context/Decision/Consequences),
    순차 번호(`0001-...md`), 결정 1개 = 파일 1개, 작성 후 변경 금지(뒤집히면 새 ADR + Superseded 표시).
- `docs/` 루트에는 spec도 adr도 아닌 개념/배경 참고 문서(`agent-harness-design.md` 등)를 그대로 둔다 —
  구체적 결정이 아니라 앞으로의 spec·adr이 참조할 배경 지식이기 때문.
- 이 컨벤션을 `rules/documentation.md`(전역 규칙)에 반영해 dotfiles-claude 한정이 아니라 모든
  프로젝트의 `docs/` 컨벤션으로 승격한다.

## Consequences

**좋음**
- git 이력·리뷰·롤백이 되는 저장소에서 하네스를 다듬으면서도, symlink 덕분에 promote/demote 비용
  없이 즉시 전역 적용된다 — ship-discussion이 우려한 두 방식의 트레이드오프를 동시에 얻는다.
- ADR 규율(결정 1개 = 파일 1개, 변경 금지)로 "왜 이렇게 했는지"가 흩어지지 않고 순차적으로 누적된다.
- `specs/`(무엇을 만들 계획인지)와 `adrs/`(무엇을 왜 결정했는지)가 섞이지 않아, 스킬·에이전트를 여러
  개 설계할 때도 계획과 결정 근거를 분리해 추적할 수 있다.
- `rules/documentation.md` 전역 갱신으로 다른 프로젝트에서도 같은 패턴을 바로 재사용할 수 있다.

**트레이드오프**
- ADR 번호는 수동으로 관리해야 한다 (자동 번호 매김 도구 없음).
- 기존 `docs/specs/`의 두 문서(`2026-06-21-git-review-pr-agent-design.md`,
  `2026-07-14-ship-ideation-framework-design.md`)는 이미 spec+구현 로드맵+위키 반영 내용이 섞인
  디자인독 스타일이라 새 컨벤션과 완전히 일치하지는 않는다 — 소급 재작성하지 않고 그대로 둔다.
- ship-discussion 쟁점 1("적용 범위" — 도메인 특칙 없이 재사용 가능함의 실증)은 여전히 미검증 상태로
  남는다. 이번 결정은 그 실증 여부와 무관하게, symlink 구조가 이분법 자체를 완화한다는 관찰에
  근거한다 — 향후 하네스 로직이 실제로 다른 프로젝트에서도 재사용됨이 확인되면 별도 ADR로 갱신한다.

## 관련

- `wiki/ideation/ship-discussion/runs/2026-07-17-harness-loop-engineering-scope/{spec,plan,result}.md`
- `wiki/me/thinking-tools/adr.md` — ADR 컨벤션 출처
- `docs/agent-harness-design.md` — 하네스 개념 배경
- `CLAUDE.md` — `~/.claude` 심볼릭 링크 구조
