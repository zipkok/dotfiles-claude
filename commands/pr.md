---
description: 로컬 변경으로 PR Title/Description을 작성하고 PR을 생성한다
argument-hint: "[대상 브랜치 · 생략 시 기본 브랜치]"
allowed-tools: Bash, Read, Task
---

로컬 변경을 PR로 올린다. 대상(base) 브랜치: `$ARGUMENTS` (생략 시 저장소 기본 브랜치)

1. `git status`, `git diff`로 로컬 변경을 확인한다. 변경이 없으면 알리고 종료.
2. `pr-author` 서브에이전트(Task)에게 변경 내용을 넘겨 Conventional Commits 제목과
   6섹션 본문 초안을 작성시킨다.
3. 초안을 사용자에게 보여주고 **명시적 승인**을 받는다.
   승인 전에는 절대 push/PR 생성을 하지 않는다.
4. 승인되면 `pr-author`가 브랜치 생성 → commit → push → `gh pr create`까지 수행한다.
5. 생성된 PR URL을 보고한다.
