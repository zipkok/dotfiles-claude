# JSON 스키마

agent-creator가 쓰는 JSON 구조를 정리한다. `grading.json`/`benchmark.json`은 skill-creator의
스키마를 라벨만 바꿔 그대로 쓴다 — `eval-viewer/generate_review.py`와 `agents/grader.md`가
정확히 이 필드 이름에 의존하므로, 수동으로 만들 때는 이 문서를 반드시 참고할 것.

---

## eval_set.json (트리거 정확도용)

트리거 최적화 루프(`run_loop.py`)의 입력. `should-trigger`/`should-not-trigger` 쿼리 목록.

```json
[
  { "query": "이 Loki 설정 YAML PR에서 문법 오류나 스키마 문제 있는지 봐줘", "should_trigger": true, "note": "선택 사항, 리뷰어용 메모" },
  { "query": "새로 만든 함수에 대한 유닛 테스트 작성해줘", "should_trigger": false }
]
```

**필드:**
- `query`: 실제로 있을 법한 사용자 요청 텍스트
- `should_trigger`: 이 쿼리에서 대상 에이전트가 선택되어야 하면 `true`. `false`는 "형제
  에이전트가 이겨야 함"과 "none이 이겨야 함" 둘 다 포함한다 — 별도 `expected_agent` 필드는
  없다 (run_loop.py 로직이 이 둘을 구분할 필요가 없기 때문에 스키마를 단순하게 유지).
- `note`: 선택 사항, 검토자를 위한 메모 (eval_review.html에는 노출되지 않음, 원본 JSON에만 보존)

---

## builtin-subagents.json

`references/builtin-subagents.json` — 수동 유지되는 built-in 서브에이전트 목록. §트리거 정확도
최적화 루프 참고. `_note` 키는 유지보수 안내이며 후보 집합 계산에는 쓰이지 않는다.

```json
{
  "_note": "...",
  "agents": [
    { "name": "general-purpose", "description": "..." }
  ]
}
```

---

## run_eval.py 출력

```json
{
  "agent_name": "config-review",
  "description": "git diff 또는 PR diff를 정확성 위주로...",
  "results": [
    {
      "query": "이 Loki 설정 YAML PR에서 문법 오류나 스키마 문제 있는지 봐줘",
      "should_trigger": true,
      "trigger_rate": 1.0,
      "triggers": 3,
      "runs": 3,
      "pass": true,
      "picks": ["config-review", "config-review", "config-review"]
    }
  ],
  "summary": { "total": 12, "passed": 10, "failed": 2 }
}
```

skill-creator의 run_eval.py 출력과 필드 이름이 동일하다(`query`, `should_trigger`, `trigger_rate`,
`triggers`, `runs`, `pass`, `summary`) — `run_loop.py`/`improve_description.py`/`generate_report.py`가
이 스키마에 의존하므로 그대로 유지했다. 추가된 필드는 `picks`(각 실행에서 실제로 선택된
이름의 리스트)뿐 — `improve_description.py`가 "대신 무엇이 선택됐는지"를 프롬프트에 포함시키는
데 쓴다.

---

## run_loop.py 출력

skill-creator와 동일한 구조에 `candidate_set`(이번 실행에 쓰인 고정 후보 이름 목록, 재현성
확인용)만 추가됐다.

```json
{
  "exit_reason": "all_passed (iteration 3)",
  "original_description": "...",
  "best_description": "...",
  "best_score": "10/10",
  "best_train_score": "6/6",
  "best_test_score": "4/4",
  "final_description": "...",
  "iterations_run": 3,
  "holdout": 0.4,
  "train_size": 6,
  "test_size": 4,
  "candidate_set": ["pr-author", "ship-discussion-position", "...", "general-purpose", "Explore", "Plan", "none"],
  "history": [ "... 반복별 상세, skill-creator와 동일 ..." ]
}
```

---

## grading.json (skill-creator와 동일, 재사용)

`agents/grader.md`의 출력. 필드: `expectations[]`(`text`/`passed`/`evidence`), `summary`,
`execution_metrics`, `timing`, `claims`, `user_notes_summary`, `eval_feedback`. 전체 스키마와
필드 설명은 `agents/grader.md`의 "Output Format" 섹션을 참고 — 여기서 중복 서술하지 않는다.

---

## benchmark.json (skill-creator와 동일한 구조, 라벨만 교체)

`configuration` 값이 `"with_skill"`/`"without_skill"` 대신 `"with_agent"`/`"without_agent"`인 것만
다르다. 나머지 필드(`metadata`, `runs[]`, `run_summary`, `delta`, `notes`)는 skill-creator의
`benchmark.json` 스키마와 동일 — `scripts/aggregate_benchmark.py`가 그대로 이 구조를 생성한다.

**중요**: 뷰어는 이 필드 이름을 정확히 읽는다. `configuration` 대신 `config`를 쓰거나
`pass_rate`를 `result` 밖에 두면 뷰어가 빈 값을 보여준다.
