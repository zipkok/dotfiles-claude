# docs/rfc/

Request For Comments — 여러 입장을 수렴해 합의된 결론에 도달하는 논의 문서. LLM Wiki
`wiki/me/thinking-tools/rfc.md`의 취지를 따른다: "comments를 받는 것"이 핵심 — 결정 전 다수
stakeholder(또는 여러 관점)의 의견을 수렴한다.

`skills/ship-discussion/` 스킬이 `/ship-discussion` 실행 시 자동으로 이 디렉터리에 결과를 쌓는다.

## 구조

폴더 단위로 순차 번호를 매긴다 — 하나의 논의(spec→clarify→plan→review→result 5단계)가 한 세트이기
때문에 `docs/adrs/`(결정 1개 = 파일 1개)와 달리 **폴더 단위**다. spec/clarify는 사용자와 직접 대화로,
plan/review/result는 `workflows/ship-discussion-panel.js`가 여러 에이전트를 협의시켜 진행한다.

```
docs/rfc/
└── 0001-{주제-slug}/
    ├── 1-spec.md     — 논점을 3~5개 쟁점으로 구조화 (사용자 대화)
    ├── 2-clarify.md  — 쟁점의 애매한 정의·범위 확정 (유형1: 사용자 대화 / 유형2: Main 자체 판단)
    ├── 3-plan.md     — mece/first-principles/pre-mortem/inversion 4기법 협의 → 진행 순서 + 대안·평가기준
    ├── 4-review.md   — steel-man 정성 + 정량 루브릭 채점 → 통과/조건부통과/fail 하이브리드 게이트
    └── 5-result.md   — 쟁점별 입장 A/B 논쟁 + devils-advocate 판정, 라운드 반복 → 배경/현재/문제점/
                         고민한 내용/결정/참고·주의사항 (사용자 승인)
```

파일명에 번호를 유지하는 이유: 각 단계는 시작할 때 그 단계의 파일만 새로 만들기 때문에, 번호가
없으면 디렉터리 정렬 순서(알파벳순)가 실제 진행 순서(spec→clarify→plan→review→result)와 어긋난다.

## `docs/adrs/`와의 차이

| | `docs/rfc/` | `docs/adrs/` |
|---|---|---|
| 목적 | 여러 입장을 수렴해 합의 도출 | 이미 내려진 결정 1개를 기록 |
| 산출물 | 폴더(4단계 파일 세트) | 파일 1개 |
| 생성 방식 | `/ship-discussion` 스킬이 자동 생성 | 결정 시점에 수동 작성 |
| 원본 | `wiki/me/thinking-tools/rfc.md` | `wiki/me/thinking-tools/adr.md` |

논의 끝에 도달한 최종 결론이 이후 "결정"으로 확정되면, 별도로 `docs/adrs/`에 ADR을 만들어 그 결정만
따로 기록할 수 있다 (예: 이번 세션의 `docs/adrs/0001-harness-loop-engineering-project-scope.md`도
LLM Wiki의 ship-discussion 논의 결과를 결정으로 확정한 사례).
