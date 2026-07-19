---
name: agent-creator
description: Use when the user wants to create, review, validate, or improve a Claude Code subagent definition (agents/*.md) in this repo - triggers on "에이전트 만들어줘", "agent.md 검증해줘", "서브에이전트 평가해줘", "이 에이전트 description 트리거 잘 되는지 확인해줘", or when a new agents/*.md file needs to be drafted, syntax-checked, or its trigger accuracy measured before being added to agents/
---

# Agent Creator

이 저장소(`dotfiles-claude`)의 서브에이전트 정의 파일(`agents/*.md`)을 만들고, 검증하고,
개선하는 스킬. `skills/skill-creator`가 `SKILL.md`에 대해 하는 일을 `agents/*.md`에 대해
한다 — 다만 대상 컨벤션이 다르다. 이 저장소의 실제 에이전트는 일반 Claude Code 플러그인
컨벤션(model/color 필수, 영어, XML `<example>` 블록)을 쓰지 않는다. name/description/tools만
쓰는 최소 frontmatter, 한국어 본문, "무엇을 하는지 + 누가/언제 호출하는지"를 담는 description,
엄격한 `## 출력` 템플릿이 이 저장소의 실제 관례다. 이 스킬은 그 관례만 다룬다 — 자세한 내용은
`references/writing-guide.md`.

## 핵심 루프

1. 만들기 (인터뷰 → 초안 → 자기검토)
2. 문법 검증 (`validate_agent.py`)
3. 실행 품질 테스트/리뷰 (with_agent/without_agent → 사람 리뷰)
4. 트리거 정확도 최적화 (eval 쿼리 → `run_loop.py`)
5. `agents/README.md`에 등록

아래 순서대로 진행하되, 사용자가 이미 초안을 갖고 있으면 2단계부터 시작해도 된다.

---

## 1. 에이전트 만들기

### 인터뷰

에이전트를 새로 만드는 요청이면 먼저 확인한다 (이미 대화에 답이 있으면 다시 묻지 말고 추출):

1. 이 에이전트가 정확히 무엇을 하는가?
2. **누가, 언제 호출하는가?** — 사용자가 직접 명시적으로 요청하는가, 특정 워크플로우/명령이
   자동으로 부르는가, 메인 루프가 상황에 맞게 판단해서 위임하는가? 이게 description의 절반을
   차지하므로 빠뜨리면 안 된다.
3. 호출자가 프롬프트에 어떤 파라미터를 넘기는가? (쟁점, 대상 diff, 이전 라운드 기록 등)
4. 출력이 워크플로우/다른 에이전트가 파싱할 고정 템플릿이 필요한가, 아니면 자유 형식이어도
   되는가?
5. 본문 골격이 `## 규칙`(판단 기준)에 가까운가 `## 작업 순서`(다단계 절차)에 가까운가?
   (`references/writing-guide.md` §3)

### 초안 작성

`references/writing-guide.md`를 참고해 frontmatter와 본문을 채운다. 살아있는 예시
(`agents/ship-discussion-position.md`, `agents/config-review.md` 등)를 열어 구조를 그대로
본뜨는 게 처음부터 쓰는 것보다 빠르다. 파일명은 `agents/<name>.md`, `name` frontmatter와
반드시 일치해야 한다.

### description 자기검토

스크립트가 아니라 여기서, LLM 스스로 반문한다: **"이 description만 보고, 이런 요청이 왔을
때 내가 실제로 이 에이전트를 고를까? 반대로, 비슷하지만 다른 요청에서 잘못 고르지는 않을까?"**
"누가/언제 호출하는지"가 description에 실제로 들어있는지도 여기서 확인한다 — 이건 의미론적
판단이라 `validate_agent.py`가 아니라 이 단계에서 다룬다.

---

## 2. 문법 검증

초안을 쓴 직후, 그리고 이후 매 반복마다:

```bash
python3 scripts/validate_agent.py agents/<name>.md
```

에러(exit 1)는 반드시 고친다 — frontmatter 키, name/kebab-case/파일명 일치, description의
꺾쇠괄호, color 필드 등. 경고(exit 0)는 확인은 하되 맹목적으로 따르지 않아도 된다(예: 정말
출력 형식이 자유로워도 되는 에이전트라면 "## 출력 없음" 경고는 무시 가능).

이름/description 없이 `model`만 있는 **직접 호출형 에이전트**(예: `exec-interviewer.md`)를
검증하면, 트리거 검증 대상이 아니라는 안내와 함께 구조만 확인하고 끝난다 — 3~4단계는
건너뛴다.

---

## 3. 실행 품질 테스트/리뷰 루프

에이전트의 **시스템 프롬프트 자체가 좋은 행동을 만들어내는가**를 트리거 여부와 별개로
확인하는 단계. skill-creator의 Step 1-5 구조를 그대로 미러링하되, baseline 정의만 다르다:
스킬은 "스킬 없음"이 baseline이지만, 에이전트는 **"메인 루프가 이 에이전트에 위임하지 않고
직접 처리"**가 baseline(`without_agent`)이다.

1. 실제로 있을 법한 테스트 프롬프트 2~3개를 사용자와 함께 정한다.
2. 같은 턴에 `with_agent`(대상 에이전트로 실행)와 `without_agent`(일반 에이전트로 위임 없이
   직접 실행) 서브에이전트를 병렬로 스폰한다. 결과는
   `workspaces/<name>-workspace/iteration-N/eval-M/{with_agent,without_agent}/outputs/`에 저장.
3. `agents/grader.md`를 읽는 서브에이전트로 각 실행을 채점 → `grading.json`. 에이전트가
   `## 출력` 템플릿을 강제하면, 출력이 그 구조를 따르는지도 1급 체크 항목으로 포함된다
   (grader.md에 이미 반영돼 있음).
4. `python3 -m scripts.aggregate_benchmark <workspace>/iteration-N --agent-name <name>`으로 집계.
5. `python3 eval-viewer/generate_review.py <workspace>/iteration-N --agent-name <name> --benchmark ...`로
   뷰어를 띄우고 사용자 리뷰를 기다린다. 헤드리스 환경이면 `--static <path>`.
6. `feedback.json`을 읽고, 반복되는 문제(규칙 누락, 출력 형식 어김)가 있으면 `## 규칙`/
   `## 출력 형식`에 명시적으로 추가한다. skill-creator의 개선 4원칙(일반화, 군더더기 제거,
   이유 설명, 반복 패턴 발견)을 그대로 적용하되, "스크립트로 뽑아내기"는 에이전트에 해당 없음
   — 대신 "여러 테스트에서 같은 실수가 반복되면 규칙에 명시"로 대체한다.
7. 사용자가 만족하거나 피드백이 다 비어있을 때까지 반복.

(블라인드 A/B 비교 — 두 버전 중 뭐가 나은지 판정 — 는 v1 범위 밖이다. skill-creator도
"고급/선택" 취급하며, 에이전트는 반복 단위가 더 작아 우선순위가 낮다. 필요해지면
`skill-creator/agents/comparator.md`를 참고해 이식.)

---

## 4. 트리거 정확도 최적화

description만 보고 Claude가 실제로 이 에이전트를 고르는지 실측 기반으로 반복 개선한다.

**왜 실제 `claude -p` 트리거 테스트가 아니라 시뮬레이션인가**: 스킬은 `available_skills`
목록에 등록한 뒤 실제 Skill 도구 호출을 관찰해서 트리거 여부를 잰다. 에이전트는 Task 도구의
`subagent_type` 선택으로 트리거되는데, 이 저장소의 실제 형제 에이전트 중 일부(`pr-author`)는
브랜치 push·PR 생성 같은 부수효과가 있다. 그래서 실제 도구 호출이 전혀 없는 **순수 분류
프롬프트**로 대체했다 — `claude -p`에 "사용자 요청 + 후보 서브에이전트 목록"만 보여주고
텍스트로만 답하게 한다. skill-creator의 실측 방식보다 충실도가 낮은 프록시라는 점을
감안할 것.

### 4-1. eval 쿼리 생성

should-trigger 8~10개(다양한 표현, 격식/캐주얼 섞기, 명시적 요청과 암묵적 요청 둘 다) +
should-not-trigger 8~10개(형제 에이전트나 built-in이 이겨야 하는 near-miss가 가장
가치있다 — 명백히 무관한 쿼리는 테스트로서 의미가 약하다)를 만든다.

### 4-2. 사용자 검토

`assets/eval_review.html`을 템플릿으로 써서 (`__EVAL_DATA_PLACEHOLDER__`,
`__AGENT_NAME_PLACEHOLDER__`, `__AGENT_DESCRIPTION_PLACEHOLDER__`,
`__CANDIDATE_SET_PLACEHOLDER__` — 후보 집합은 `python3 -m scripts.list_sibling_agents --target
<name>`로 미리 구해서 채워 넣는다) 검토 페이지를 띄운다. should-not-trigger 쿼리를 검토할 때
사용자가 후보 집합(형제 + built-in + none)을 볼 수 있게 하는 게 중요하다 — 그 목록 밖에 있는
가상의 에이전트를 정답으로 가정하면 안 되기 때문.

### 4-3. 루프 실행

```bash
python3 -m scripts.run_loop \
  --eval-set <path> \
  --agent-path agents/<name>.md \
  --model <현재 세션 모델 ID> \
  --max-iterations 5 \
  --verbose
```

60/40 train/test 분리, 쿼리당 3회 실행, 최대 5회 반복, test 점수 기준 최선 선택 — skill-creator의
`run_loop.py`와 동일한 메커니즘이다. 후보 집합(형제+built-in+none)은 루프 시작 시 한 번만
계산되어 모든 반복에 고정된다 — 그래야 반복 간 점수 변화가 후보 집합 변화가 아니라 description
변경 때문이라고 해석할 수 있다.

### 4-4. 결과 적용

`best_description`을 `agents/<name>.md`의 frontmatter에 반영하고, before/after와 점수를
사용자에게 보여준다.

---

## 5. 완료 후

`agents/README.md`의 표에 새 에이전트 항목을 추가한다 (skill-creator에는 없는, 이 저장소
고유의 마무리 단계 — `agents/`는 README.md 표로 큐레이션되는 관례다). 기존 표에 다른 누락
항목이 있어도 이 작업 범위에서 함께 고치지 않는다 — 별도로 처리한다.

---

## Claude.ai / Cowork에서

subagent가 없는 환경에서는 3단계(실행 품질 테스트)의 병렬 스폰이 순차 실행으로 바뀌고,
브라우저가 없으면 `--static`으로 정적 HTML을 만든다 — skill-creator와 동일한 제약이다.
4단계(트리거 최적화)는 `claude -p`를 subprocess로 부르므로 브라우저 없이도 동작하지만,
에이전트가 충분히 안정된 뒤에 마지막으로 돌리는 걸 권장한다.

---

## 참고 파일

- `references/writing-guide.md` — 이 저장소 agent.md 작성 가이드 (frontmatter, description
  2단 구조, 규칙 vs 작업 순서, 출력 템플릿)
- `references/schemas.md` — eval_set/grading/benchmark JSON 스키마
- `references/builtin-subagents.json` — 트리거 테스트용 built-in 후보 (수동 유지, Claude Code
  built-in 목록이 바뀌면 갱신 필요)
- `agents/grader.md` — 실행 품질 채점 서브에이전트
- `scripts/validate_agent.py` — 문법 검증
- `scripts/list_sibling_agents.py` — 트리거 테스트용 고정 후보 집합 생성
- `scripts/run_eval.py`, `scripts/improve_description.py`, `scripts/run_loop.py` — 트리거
  정확도 최적화 루프
