# Changelog

이 저장소(`dotfiles-claude`)의 변경사항을 기능별·작업별로 날짜와 함께 기록한다.
카테고리: 추가 / 변경 / 수정 / 삭제 (`rules/documentation.md` 참조)

## 2026-07-19 (ship-discussion 재설계 — 대안 스코어카드 설계 병합)

사용자가 별도로 설계한 spec-kit 스타일 논의 파이프라인(슬래시커맨드 5개 + 정량 게이트 스코어카드)을
비교·병합. 아키텍처는 단일 스킬 유지(Spec/Clarify를 별도 커맨드+수동 `/clear`로 쪼개지 않음), 대신
단계 전환 시 대화 기억 대신 산출물 파일을 다시 읽는 "아티팩트 규율"을 명문화해 `/clear`의 효과를
대체 — Plan/Review/Result는 이미 `Workflow`의 `agent()` 호출이 격리된 컨텍스트라 이 규율이 필요 없음.

### 변경
- **Spec**: 측정 가능한 성공/판정 기준 표, 범위 포함/제외, 이해관계자 R/A/C/I 표, `[NEEDS
  CLARIFICATION: 질문]` 마킹 컨벤션 추가. 발산 루프·7축 Self-Review·배치 질문은 유지
- **Clarify**: 유형1 질문 배치를 순차(하나씩)로 되돌림 — 지난 라운드의 배치 결정을 부분 되돌림.
  이유: 소크라테스식 대화는 직전 답변에 다음 질문이 의존하는 적응적 구조라 배치와 근본적으로
  충돌(Spec의 발산 로테이션과는 성격이 다름). 모호어("개선","빠르게","충분히") 탐지를 Spec의
  red-flag 스캔에 이어 추가
- **Plan**: 쟁점별 대안 ≥2개 + 평가기준·가중치(합 100%) 설계 섹션 신설. 이 대안이 Result의 position
  A/B가 실제로 논쟁하는 대상이 되도록 `workflows/ship-discussion-panel.js`에 `alternativeA/B` 필드
  연결
- **Review**: rubber-duck 제외(1:1 대체 아님 — Review의 목적이 "계획 정합성 검증"에서 "의사결정
  지지 근거 채점"으로 바뀜). steel-man(정성) + 스코어링 매트릭스·5항목 루브릭(정량, 게이트 점수
  0~100)의 **하이브리드 판정**: CRITICAL 없음+≥80점 통과, CRITICAL 없음+60~79점 조건부 통과(이월표
  등록), 그 외 fail. 같은 게이트 2회 초과(3회째) 시 자동 에스컬레이션(수용/보류/폐기를 사용자에게
  요청) 추가. aporia/미해결 쟁점은 채점 분모에서 제외하되 "채점 제외 — 사유"로 명시해야 통과 가능
  (조용히 빠지면 게이트 우회로 간주)
- **Result**: 출력 구조를 "쟁점별 결론/잠정 결론/실행/주의사항"에서 사용자 지정 6단 구조(배경(goal/
  scope)/현재/문제점/고민한 내용/결정/참고·주의사항)로 전면 교체. "고민한 내용"은 대안 비교의 정리된
  결론만 담는다는 것을 명시 — "result엔 과정 안 남긴다" 원칙을 뒤집는 게 아니라 "과정"과 "대안 비교
  정리"를 구분한 것
- `SKILL.md`에 "게이트 우회 금지" 원칙 추가

### 참고
- 다중기법 병렬 에이전트(mece/first-principles/pre-mortem/inversion/steel-man/devils-advocate),
  소크라테스식 사용자 의도 탐구(Clarify 유형1), aporia 인정은 모두 유지 확인
- **이 라운드는 문서 수정만으로 검증되지 않는다** — 실제 `/ship-discussion` 1회 실행 후에 순차 질문·
  대안 채점·하이브리드 판정·6단 Result 구조가 실제로 동작하는지 확인 필요

## 2026-07-19 (ship-discussion 실사용 피드백 반영 — RFC 0002 실행 결과 기반)

`docs/rfc/0002-improve-work-quality/`로 `/ship-discussion`을 실제 끝까지 실행해본 결과 드러난
문제들을 수정. 조사(Explore 에이전트 3개 병렬)로 근본 원인을 확인하고, 유일한 설계 판단(Clarify
재설계)만 사용자 확인(AskUserQuestion)을 거쳤다.

### 수정
- **Workflow 호출 크래시** (`Error: args.stage가 필요합니다`): `SKILL.md`의 pseudo-code
  `workflow('ship-discussion-panel', {...})`가 워크플로 스크립트 내부 헬퍼 문법과 똑같이 생겨서,
  Main이 실제 `Workflow` 도구(`name`/`args` 분리 파라미터, 비동기)를 그 문법 그대로 호출하려다
  args가 전달되지 않고 크래시했다. `SKILL.md` 3~5단계를 실제 도구 호출 형태로 재작성하고 비동기
  특성(즉시 반환, task-notification으로 결과 도착)을 명시. `doc-review/SKILL.md`에도 동일 표기가
  있어 같은 잠재 버그가 있음을 확인(이번 스코프에선 수정하지 않음)
- **템플릿 5개 선복사 + 번호 탈락**: 0단계가 아직 시작 안 한 plan/review/result까지 템플릿 5개를
  한꺼번에 번호 없이 복사해, 산출물 디렉터리가 알파벳 정렬 시 파이프라인 순서와 어긋났다(`clarify→
  plan→result→review→spec`). 각 단계 진입 시(파일 없을 때만) 그 단계 템플릿만 번호 유지한 채
  복사하도록 변경(`1-spec.md`~`5-result.md`) — `docs/rfc/README.md`도 반영

### 변경
- `AskUserQuestion` 질문을 라운드마다 하나씩 개별 호출하던 것을, 로테이션 기법 2~3개의 질문을
  한 호출의 `questions` 배열에 배치하도록 변경 (Spec 8라운드 → 대략 3회 안팎으로 왕복 감소)
- **Clarify 유형별 분기 신설**: 모든 쟁점을 예외 없이 사용자와 소크라테스식 대화로 처리하던 것을,
  유형1(사용자 고유 의도 — 대화 유지)과 유형2(내적 일관성 — Main이 직접 판단)로 분기. 유형2 처리
  중 spec 전제 자체의 문제로 판단되면 즉시 사용자와 라이브 대화로 에스컬레이션
- `workflows/ship-discussion-panel.js`에 `args.slug`(RFC 폴더명) 지원 추가 — agent 라벨·로그에
  붙여 `/workflows`에서 여러 실행 구분 가능하게. `meta.name`은 고정 literal이라 실행별 이름 변경은
  불가능함을 `SKILL.md`에 명시
- `templates/3-plan.md`의 "쟁점 분류"와 "진행 순서" 중복 섹션을 하나로 병합(분류를 진행 순서 항목
  안에 표기), Review-fail 재작업 라운드용 공식 헤더와 "기법 간 충돌·조정" 섹션 신설(산출물엔 있는데
  템플릿엔 없던 것)
- `templates/1-spec.md`에 쟁점 간 계층관계 표기 가이드 추가, `templates/2-clarify.md`에 "이미
  명확해 스킵" 케이스의 공식 포맷 추가
- `.claude/state/ship-discussion-active.json`에 `current_stage`, `pending_workflow_stage` 필드
  추가 — 비동기 Workflow 호출 중 세션이 재개돼도 무엇을 기다리던 중이었는지 복원 가능하게

### 참고
- 백그라운드 Explore 에이전트로 RFC 0002 산출물을 spec-kit/spex/superpowers와 비교: 구조적으로
  뒤지지 않고(라운드 로그, 실패 이력 보존, 다관점 기법 대조 등 세 도구에 없는 강점 있음), 다만
  프로젝트 원칙 대조 축·정량적 추적성 마커·형식화된 FR/SC 식별자는 없음 — 이번엔 반영하지 않고
  기록만 남김(범용 논의 도구에 항상 필요한 개념은 아니라 별도 설계 판단 필요)

## 2026-07-19 (ship-discussion Stop 훅 제거, Review 기법 축소, AskUserQuestion 도입)

### 삭제
- `hooks/ship-discussion-review-gate.sh` — Stop 훅으로 "사용자 승인 전 세션 종료 방지"를 구현했으나
  실사용 중 매 턴(정상적인 질문-대기 턴 포함)마다 오작동 확인. 근본 원인: Stop 이벤트는 세션 종료
  시도가 아니라 Claude가 응답을 마칠 때마다 발동하고, exit code 2 차단은 사용자 입력을 기다리는 게
  아니라 **Claude를 사용자 답변 없이 강제로 계속 응답하게 만듦** — 오탐 시 오히려 해로움. `settings.json`
  Stop 훅 등록도 함께 제거. 이후 이 규율은 `SKILL.md`의 자가 게이트 점검만으로 유지

### 변경
- `skills/ship-discussion/` Spec·Clarify·Result 단계의 사용자 확인 질문을 평문 대화 대신
  `AskUserQuestion` 도구로 던지도록 변경
- Review 단계 기법을 3개(steel-man/pre-mortem/decision-review) → 2개(steel-man/rubber-duck)로 축소
  — pre-mortem은 Plan 단계와 동일 질문을 재검증하는 중복이었고, decision-review는 "시간이 지나 결과를
  안 뒤 재평가"하는 기법이라 계획 직후 적용하는 시점과 전제가 안 맞아 제외
- `agents/ship-discussion-technique-agent.md`, `agents/ship-discussion-synthesizer.md`,
  `workflows/ship-discussion-panel.js`, `stages/4-review.md`, `templates/4-review.md` 반영
- `SKILL.md`의 Mermaid 다이어그램이 기존 Graphviz `dot` 표기라 대부분의 마크다운 뷰어에서 안 그려지던
  문제 수정 (`dot` → `mermaid`)

## 2026-07-17 (ship-discussion 스킬 포팅 + docs/rfc 신설, output-style 개선)

### 추가
- `skills/ship-discussion/` — LLM Wiki `wiki/ideation/ship-discussion/`의 소크라테스식 논의 파이프라인(spec→plan→result→review)을 dotfiles-claude 전역 스킬로 포팅. 어느 프로젝트에서 호출하든 그 프로젝트의 `docs/rfc/{NNNN}-{주제}/`에 결과가 쌓인다
  - `templates/{spec,plan,result,review}.md` — wiki 원본 그대로
  - `stages/{spec,plan,result,review}.md` — wiki `.claude/agents/*.md` 기반 참조 문서. Agent 도구 서브에이전트 레지스트리(`agents/`)에는 넣지 않음 — 다회 왕복 대화가 필요해 호출 금지로 설계됐기 때문
- `docs/rfc/` — RFC(`wiki/me/thinking-tools/rfc.md`) 컨벤션 신설. `docs/adrs/`(결정 1개=파일 1개)와 달리 폴더 단위(스킬이 자동 생성)

### 변경
- `rules/documentation.md`(전역 규칙), `docs/README.md`, 루트 `README.md`, `skills/README.md`에 `docs/rfc/`·`ship-discussion` 반영
- `output-styles/work-style.md` — 중복 `---` 버그 수정, "액션 아이템(체크리스트)" 포맷 추가, 진행 중 단계별 프로그레스바 갱신 규칙 추가, 프로그레스바 위치를 응답 최하단으로 명시, 플레이스홀더 없는 실제 예시 추가

## 2026-07-17 (docs/adrs 신설)

### 추가
- `docs/adrs/` — Architecture Decision Record 폴더 신설 (Nygard 형식, `wiki/me/thinking-tools/adr.md` 컨벤션 재사용)
  - `docs/adrs/0001-harness-loop-engineering-project-scope.md` — 하네스/루프 엔지니어링 토대를 프로젝트 단위(dotfiles-claude)에 두고 `docs/specs/` + `docs/adrs/` 구조로 다루기로 한 결정. LLM Wiki에 미완결로 남아있던 ship-discussion 토론(`wiki/ideation/ship-discussion/runs/2026-07-17-harness-loop-engineering-scope/`)의 답을 겸함

### 변경
- `rules/documentation.md`(전역 규칙) — `specs/`의 낡은 "spex 워크플로우 산출물" 설명(spex 플러그인 비활성화로 근거 소실)을 정정하고 `adrs/` 컨벤션 추가. 모든 프로젝트의 `docs/` 컨벤션으로 승격
- `docs/README.md`, 루트 `README.md`, `rules/README.md`에 `docs/adrs/` 반영. `docs/specs/`는 경로 변경 없음

## 2026-07-17

### 삭제
- `docs/hook-lifecycle.md`, `docs/claude-vs-codex-harness-design.md` — LLM Wiki(`~/Repository/llm_wiki`)로 병합 이관 후 원본 삭제
  - `hook-lifecycle.md` → `wiki/ai/claude/claude-code-hook-lifecycle.md`에 이미 존재하던 내용과 중복 확인 후 삭제 (레포별 훅 매핑 표는 `hooks/README.md`에 보존)
  - `claude-vs-codex-harness-design.md` → 신규 `wiki/ai/claude/claude-code-vs-codex-cli.md` + source `wiki/sources/ai/2026-07-17-claude-vs-codex-harness-design.md`

### 변경
- `docs/README.md`, `docs/specs/README.md`, 루트 `README.md` 파일 구조 표에서 삭제된 항목 제거 및 이관 안내 추가

> `docs/assets/`, `docs/specs/2026-07-14-ship-ideation-framework-design.md`도 같은 작업에서 한 차례 LLM Wiki로 이관·삭제했으나, 곧이어 원복 요청을 받아 dotfiles-claude에 그대로 복원했다 (위키 쪽 병합 내용도 되돌림). 최종 상태: 두 항목 모두 dotfiles-claude에 유지.

<!-- 아래에 최신 항목이 위로 오도록 추가한다.

## 2026-07-17

### 추가
- ...

-->
