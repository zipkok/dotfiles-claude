---
name: directory
description: 작업 디렉터리를 변경합니다. `/directory <path>` 형식으로 사용하며, Repository 디렉터리 기준 경로로 이동합니다.
argument-hint: <path>
allowed-tools: [Bash]
---

# Directory

작업 디렉터리를 빠르게 변경하는 스킬입니다.

## 사용법

- `/directory fate-weave` — `/Users/woobs/Repository/fate-weave`로 이동
- `/directory claude/global` — `/Users/woobs/Repository/claude/global`로 이동
- `/directory repository` — `/Users/woobs/Repository`로 이동 (별칭)
- `/directory llm_wiki` — `/Users/woobs/Repository/llm_wiki/LLM_Wiki`로 이동 (옵시디언 볼트 별칭)
- `/directory .` — 현재 디렉터리 확인

## 별칭 (Aliases)

다음 키워드는 특별 경로로 해석됩니다:

| 별칭 | 대상 경로 |
|------|----------|
| `repository` | `/Users/woobs/Repository` |
| `llm_wiki` | `/Users/woobs/Repository/llm_wiki/LLM_Wiki` |

## 인자

$ARGUMENTS

## 동작 방식

1. 인자가 위 **별칭 표**에 있으면 해당 경로로 매핑합니다.
2. 아니면 다음 규칙으로 해석합니다:
   - 절대 경로(`/`로 시작)가 주어지면 그대로 사용합니다.
   - `~`로 시작하면 홈 디렉터리로 확장합니다.
   - 그 외에는 `/Users/woobs/Repository/` 접두사를 붙입니다.
3. 해당 디렉터리가 존재하는지 확인합니다.
4. `cd`로 이동한 뒤 `pwd`로 현재 위치를 출력합니다.
5. 이동 후 간단히 `ls`로 디렉터리 내용을 보여줍니다.

## 실행 지시

다음 순서로 실행하세요:

1. `$ARGUMENTS` 에서 경로를 파싱합니다. 비어 있으면 사용법을 안내합니다.
2. 별칭 표 매칭을 먼저 확인하고, 매칭되지 않으면 경로 해석 규칙을 적용합니다. (기본 베이스: `/Users/woobs/Repository/`)
3. `cd <대상 디렉터리> && pwd && ls` 를 Bash로 실행합니다.
4. 디렉터리가 없으면 에러 메시지를 출력합니다.
