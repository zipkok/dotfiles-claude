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
- `/directory .` — 현재 디렉터리 확인

## 인자

$ARGUMENTS

## 동작 방식

1. 인자로 받은 경로를 `/Users/woobs/Repository/<path>` 로 해석합니다.
   - 절대 경로(`/`로 시작)가 주어지면 그대로 사용합니다.
   - `~`로 시작하면 홈 디렉터리로 확장합니다.
   - 그 외에는 `/Users/woobs/Repository/` 접두사를 붙입니다.
2. 해당 디렉터리가 존재하는지 확인합니다.
3. `cd`로 이동한 뒤 `pwd`로 현재 위치를 출력합니다.
4. 이동 후 간단히 `ls`로 디렉터리 내용을 보여줍니다.

## 실행 지시

다음 순서로 실행하세요:

1. `$ARGUMENTS` 에서 경로를 파싱합니다. 비어 있으면 사용법을 안내합니다.
2. 경로 해석 규칙에 따라 대상 디렉터리를 결정합니다. (기본 베이스: `/Users/woobs/Repository/`)
3. `cd <대상 디렉터리> && pwd && ls` 를 Bash로 실행합니다.
4. 디렉터리가 없으면 에러 메시지를 출력합니다.
