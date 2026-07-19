---
name: doc-review
description: Use when the user wants to review an English-written document for structure, grammar, readability, and reproducibility - triggers on "/doc-review", "문서 리뷰해줘", "영어 문서 검토해줘", or when checking whether a doc is well-structured and can be followed successfully by a first-time reader
---

# Doc-Review

영어로 작성된 문서를 6개 디멘션(`structure`/`grammar`/`readability`/`reproducibility`/
`terminology`/`audience-tone`)으로 병렬 리뷰해 하나의 리포트로 수렴하는 스킬. 각 디멘션은 반드시
별개 에이전트가 담당한다 — Main이 문서를 직접 읽고 여러 관점을 혼자 판정하지 않는다.

## 실행 아키텍처

`workflows/doc-review-panel.js`를 호출한다. 이 워크플로가 `agents/doc-review-checker.md`를
디멘션마다 다른 프롬프트로 6회 병렬 호출하고, `agents/doc-review-synthesizer.md`로 결과를
하나의 리포트로 수렴한다.

```
workflow('doc-review-panel', { docPath: <리뷰 대상 문서 절대/상대 경로>, context: <선택, 문서 배경> })
```

## 절차

1. **대상 문서 확인**: 사용자가 문서 경로를 명시하지 않았으면 먼저 물어본다. 여러 문서를 한 번에
   요청하면 문서마다 workflow를 개별 호출한다 (한 번의 workflow 호출 = 문서 1개 리뷰).
2. **워크플로 호출**: 위 형태로 `doc-review-panel`을 호출한다.
3. **결과 제시**: 반환된 `report`를 그대로 사용자에게 보여준다. Main이 리포트 내용을 임의로
   재작성하거나 발견을 추가/삭제하지 않는다 — 다르게 판단되면 이유를 밝히고 별도로 언급한다.

## Common Mistakes

| 실수 | 올바른 방법 |
|------|-----------|
| Main이 6개 디멘션을 혼자 순차적으로 검토 | 반드시 `doc-review-panel` workflow로 병렬 위임 |
| synthesizer의 리포트를 Main이 임의로 재작성 | 반환된 리포트를 그대로 반영, 다르면 이유 명시 |
| 문서 경로 없이 workflow부터 호출 | 사용자에게 대상 문서를 먼저 확인 |
| 여러 문서를 한 workflow 호출에 섞음 | 문서마다 별도로 `workflow('doc-review-panel', ...)` 호출 |
