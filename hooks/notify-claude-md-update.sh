#!/bin/bash
# CLAUDE.md 수정 시 claude-md-improver 실행 안내
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [ -z "$file_path" ]; then
  exit 0
fi

if echo "$file_path" | grep -q "CLAUDE.md"; then
  echo "📋 CLAUDE.md가 수정되었습니다. /claude-md-management:claude-md-improver 로 품질 검사를 실행하세요."
fi
