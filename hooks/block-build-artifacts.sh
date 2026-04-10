#!/bin/bash
# 빌드 산출물 디렉토리 쓰기 차단
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# file_path가 없으면 통과
if [ -z "$file_path" ]; then
  exit 0
fi

# 빌드 산출물 패턴 체크
if echo "$file_path" | grep -qE '(node_modules|dist|build|\.next|__pycache__|\.godot)/'; then
  echo '{"error": "🚫 빌드 산출물 디렉토리에 직접 쓸 수 없습니다: '"$file_path"'"}' >&2
  exit 2
fi
