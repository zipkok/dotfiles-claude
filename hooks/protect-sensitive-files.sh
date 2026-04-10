#!/bin/bash
# 민감 파일 수정 경고
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# file_path가 없으면 통과
if [ -z "$file_path" ]; then
  exit 0
fi

# 민감 파일 패턴 체크
if echo "$file_path" | grep -qiE '\.(env|env\..*)$|credentials|secrets|\.pem$|\.key$|id_rsa'; then
  echo '{"error": "⚠️ 민감 파일 수정 감지: '"$file_path"'. 시크릿이 하드코딩되지 않았는지 확인하세요."}' >&2
  exit 2
fi
