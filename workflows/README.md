# workflows/

여러 서브에이전트를 하나의 명령으로 오케스트레이션하는 Workflow 스크립트(`*.js`) 저장소.
`docs/agent-harness-design.md` — "워크플로 자체도 설계 대상" 항목 참조.

| 파일 | 역할 |
|------|------|
| `ship-discussion-panel.js` | `skills/ship-discussion/`의 Plan/Review/Result 단계 — 서로 다른 사고도구를 가진 에이전트들을 병렬 실행 후 synthesizer로 수렴. `{stage: 'pipeline'}`로 호출하면 Plan→Review(fail시 재작업 루프)→Result(라운드 반복)까지 사람 개입 없이 한 번에 체이닝(3회 초과 fail만 조기 반환). 개별 단계 디버깅용으로 `{stage: 'plan'\|'review'\|'result'}`도 남아있음 |
| `doc-review-panel.js` | `skills/doc-review/`가 호출 — 영어 문서를 structure/grammar/readability/reproducibility/terminology/audience-tone 6개 디멘션으로 병렬 체크 후 synthesizer로 수렴. `{docPath, context?}`로 호출, 한 번 호출 = 문서 1개 리뷰 |
