# 이 저장소의 agent.md 작성 가이드

이 문서는 `dotfiles-claude`의 실제 `agents/*.md`가 쓰는 관례를 정리한 것이다. **일반 Claude
Code 플러그인 컨벤션**(model/color 필수, XML `<example>` 블록, 영어 본문)과는 다르다 — 여기서
다루는 건 오직 이 저장소 로컬 관례다. 살아있는 예시를 직접 인용하니, 헷갈리면 실제 파일
(`agents/ship-discussion-position.md`, `agents/config-review.md` 등)을 열어 비교해보는 게 가장 빠르다.

## 1. 에이전트의 해부학

```yaml
---
name: agent-identifier         # 필수, kebab-case, 파일명과 동일해야 함
description: ...               # 필수, 한국어, "무엇을 하는지 + 누가/언제 호출하는지"
tools: Bash, Read, Grep, Glob  # 선택, 콤마 구분 스칼라 (YAML 배열 아님)
---

한국어 본문
```

스킬(`SKILL.md`)과 다른 점: 스킬은 progressive disclosure로 `scripts/`, `references/`, `assets/`
같은 번들을 점진적으로 로드하지만, 에이전트는 그런 번들이 없다. 에이전트의 "산출물"은 파일이
아니라 **행동/텍스트**이고, 그 행동은 이 frontmatter + 본문 전체가 매 호출마다 통째로 읽혀
system prompt가 되는 것으로 결정된다. 그래서 에이전트는 파일 하나가 전부다.

`color`, `model`(대부분의 경우), XML `<example>` 블록, `## When to invoke` 헤딩은 이 저장소에서
쓰지 않는다 — §6 참고.

## 2. `description` 작성법 — 트리거링의 유일한 수단

이 저장소 에이전트에는 `## When to invoke` 같은 별도 섹션이 없다. **트리거 정보 전부가 flat한
`description` 필드 하나에 들어간다.** 실제 예시 전수에서 확인되는 2단 구조:

> **(무엇을 하는지)** + **(누가/언제 호출하는지)**

정본 예시 (`agents/ship-discussion-position.md`):

```yaml
description: 쟁점 하나에 대해 지정된 입장을 최강 논리로 옹호한다. ship-discussion의 Result
  단계에서 workflows/ship-discussion-panel.js가 같은 쟁점에 대해 A/B 두 입장으로 2회 호출한다.
```

- 첫 문장 "쟁점 하나에 대해 지정된 입장을 최강 논리로 옹호한다" — **능력**
- 둘째 문장 "ship-discussion의 Result 단계에서 workflows/ship-discussion-panel.js가 ... 호출한다"
  — **호출자 + 시점 + 호출 방식**

두 부분 다 있어야 한다. 능력만 쓰면 Claude가 언제 이 에이전트를 골라야 할지 판단할 근거가
부족하고, 호출자 정보만 쓰면 능력이 불분명해진다.

**skill-creator의 "pushy하게 써라" 조언은 그대로 가져오지 않는다.** 스킬은 `available_skills`라는
넓은 목록 안에서 경쟁하므로 공격적인 트리거 문구가 도움이 되지만, 에이전트는 Task 도구가
`subagent_type`을 고를 때 **이 저장소의 소수 형제 에이전트 + built-in(general-purpose, Explore,
Plan) + "위임하지 않음"** 사이에서만 경쟁한다. 후보군이 훨씬 작고 고정적이기 때문에, description을
과도하게 넓게/공격적으로 쓰면 오히려 맞지 않는 상황에서도 이 에이전트가 뽑히는 오탐이 늘어난다.
정확하고 구체적인 게 낫다.

## 3. 골격 선택: `## 규칙` vs `## 작업 순서`

실제 예시를 보면 본문 골격이 목적에 따라 갈린다:

- **`## 작업 순서`(다단계 절차)** — `config-review.md`, `pr-author.md`처럼 여러 단계를 순서대로
  밟아야 하는 에이전트. "1. diff를 읽는다 → 2. 점검한다 → 3. 정리한다"처럼 번호 매긴 절차.
- **`## 규칙`(판단 기준)** — `ship-discussion-position.md`, `ship-discussion-technique-agent.md`처럼
  단일 판단/생성을 한 번에 수행하는 에이전트. "반대 입장의 장점을 인정하지 않는다", "근거 없는
  주장을 하지 않는다"처럼 제약 나열.

기준: **여러 단계를 순서대로 밟아야 하면 작업 순서, 판단 기준만 있으면 규칙.** 둘 다 필요하면
둘 다 써도 된다(`config-review.md`는 사실 둘 다 갖고 있다 — "무엇을 보는가" 섹션이 판단 기준,
"작업 순서" 섹션이 절차).

## 4. `## 출력` / `## 출력 형식`의 엄격함

이 저장소 에이전트는 거의 예외 없이 **리터럴 markdown 템플릿**으로 끝난다:

```md
## 입장: {네게 배정된 입장}

### 핵심 주장
{1~2문장}

### 근거
- {근거 1}
- {근거 2}
```

이유: 호출자가 사람이 아니라 **워크플로우(`workflows/*.js`)나 다른 에이전트**이기 때문이다.
자연스러운 산문보다 구조적 예측가능성이 훨씬 중요하다 — 호출자가 결과를 그대로 다음 단계에
넘기거나 파싱해야 하는 경우가 많다. 새 에이전트를 만들 때는 항상 호출자가 결과를 어떻게 쓸지
먼저 생각하고, 그에 맞는 고정 템플릿을 `## 출력`/`## 출력 형식` 아래 코드펜스로 명시하라.

## 5. "호출자를 아는 것" — 본문 첫 문장

이 저장소 에이전트는 제로샷으로 호출되지 않는다 — 호출자가 프롬프트에 구체적인 파라미터를
함께 넘긴다. 그래서 본문 첫 문장은 보통 페르소나 선언 + 호출자가 넘기는 파라미터 설명이다:

> "너는 **지정된 입장 하나만** 옹호하는 토론자다. 호출자가 프롬프트에 `쟁점`, `네가 맡을 입장`,
> `맥락`(주제·배경·이전 라운드 기록이 있으면 그것도)을 함께 넘긴다."

이걸 빠뜨리면 에이전트가 무엇을 기대해야 하는지 스스로 추측해야 하고, 호출자도 어떤 값을
넘겨야 하는지 다른 곳(워크플로우 코드)을 봐야 알 수 있다. **본문 첫 문장에서 호출자가 넘기는
파라미터를 명시하라.**

## 6. 4개 패턴 (일반 plugin-dev 컨벤션의 Analysis/Generation/Validation/Orchestration을
이 저장소 사례로 재매핑)

| 패턴 | 이 저장소 예시 | 골격 |
|---|---|---|
| Validation | `config-review.md` | 정확성 리뷰, 심각도별(🔴🟡🔵) 출력 |
| Generation | `pr-author.md` | 고정 목차 문서 생성 + 승인 게이트(`## 안전 규칙`) |
| Analysis/Debate | `ship-discussion-position.md`, `ship-discussion-technique-agent.md` | 단일 관점/기법 적용 |
| Orchestration/Synthesis | `ship-discussion-synthesizer.md` | 여러 결과를 하나로 수렴 |

새 에이전트를 만들 때 어느 패턴에 가장 가까운지 먼저 판단하고, 해당 예시 파일을 그대로 열어
구조를 참고하는 게 처음부터 쓰는 것보다 빠르다.

## 7. 명시적 비-패턴 (하지 않는 것)

- **`color` 필드 없음** — 일반 plugin 컨벤션에만 있음, 이 저장소는 안 씀
- **XML `<example>` 블록 없음** — description은 항상 flat prose
- **영어 본문 없음** — `rules/conventions.md`에 따라 대화·문서는 한국어
- **`## When to invoke` 헤딩 없음** — 트리거 정보는 전부 `description` 필드 하나에
- **`model` 필드는 거의 안 씀** — 직접 호출형 에이전트(예: `exec-interviewer.md`)에서만 예외적으로
  `model`만 있고 name/description/tools가 아예 없는 형태로 쓰인다. 이런 에이전트는 워크플로우/명령이
  파일 경로로 직접 부르므로 트리거 문구가 필요 없다.

## 다음 단계

새 에이전트 초안을 다 썼으면:
1. `python3 scripts/validate_agent.py <path>`로 문법 검증 (§SKILL.md 3단계)
2. 스스로에게 반문: "이 description만 보고, 이 요청이 왔을 때 내가 이 에이전트를 고를까?"
3. 트리거 정확도가 걱정되면 트리거 최적화 루프(`run_loop.py`)로 실측 (§SKILL.md 6단계)
