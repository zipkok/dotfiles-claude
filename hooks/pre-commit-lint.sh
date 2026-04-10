#!/bin/bash
# 커밋 전 lint 자동 실행
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# git commit 명령이 아니면 통과
if ! echo "$command" | grep -q "git commit"; then
  exit 0
fi

# package.json이 있으면 lint 실행
if [ -f "package.json" ]; then
  if jq -e '.scripts.lint' package.json > /dev/null 2>&1; then
    result=$(npm run lint --silent 2>&1)
    if [ $? -ne 0 ]; then
      echo '{"error": "lint 실패. 커밋 전에 lint 에러를 수정해주세요.\n'"$result"'"}' >&2
      exit 2
    fi
  fi
fi
