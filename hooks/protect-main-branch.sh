#!/bin/bash
# main 브랜치 직접 커밋 차단
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# git commit 명령이 아니면 통과
if ! echo "$command" | grep -q "git commit"; then
  exit 0
fi

# 초기 커밋이면 통과 (커밋 이력이 없는 경우)
if ! git rev-parse HEAD >/dev/null 2>&1; then
  exit 0
fi

# 현재 브랜치 확인
current_branch=$(git branch --show-current 2>/dev/null)

if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
  echo '{"error": "🚫 main 브랜치에서 직접 커밋할 수 없습니다. feature/ 또는 fix/ 브랜치를 사용하세요."}' >&2
  exit 2
fi
