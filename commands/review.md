---
description: 로컬 변경 또는 PR diff를 정확성 위주로 리뷰한다
argument-hint: "[PR번호 또는 URL · 생략 시 로컬 변경]"
allowed-tools: Bash, Read, Grep, Glob, Task
---

변경분을 정확성 위주로 리뷰한다. 인자: `$ARGUMENTS`

1. **대상 판별**
   - `$ARGUMENTS` 가 있으면(PR 번호/URL) → `gh pr diff $ARGUMENTS` 로 diff 수집.
   - 없으면 → 로컬 변경: `git status` 확인 후 `git diff` + `git diff --staged`.
   - 변경이 전혀 없으면 그 사실을 알리고 종료.
2. **리뷰 실행**: `config-review` 서브에이전트(Task)에게 수집한 diff를 넘겨
   정확성 리뷰를 수행시킨다.
3. **결과 보고**: 서브에이전트의 발견을 심각도 표(🔴/🟡/🔵)와 함께 대화에 요약한다.
   파일로 저장하지 않는다(대화 요약만).
