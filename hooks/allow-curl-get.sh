#!/bin/bash
# curl GET 호출은 자동 허용, POST/PUT/DELETE/PATCH나 데이터 전송이 섞인 curl은 그대로 확인받게 둔다.
# permission 규칙(prefix 매칭)만으로는 "curl이되 GET만" 표현이 안 돼서 훅으로 명령 내용을 직접 검사한다.
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# curl 호출이 아니면 관여하지 않는다 (기본 permission 흐름에 맡김)
echo "$command" | grep -qE '(^|[;&|]\s*)curl\b' || exit 0

# 메서드를 POST 등으로 바꾸거나 데이터를 보내는 플래그가 있으면 관여하지 않는다 (평소대로 확인받음)
if echo "$command" | grep -qE -- '-X[[:space:]]*(POST|PUT|DELETE|PATCH)|--request[[:space:]=]*(POST|PUT|DELETE|PATCH)|--data|(^|[[:space:]])-d([[:space:]]|=)|--data-raw|--data-binary|--data-urlencode|(^|[[:space:]])-F([[:space:]]|=)|--form|--upload-file|(^|[[:space:]])-T([[:space:]]|=)'; then
  exit 0
fi

# GET으로 보이는 curl만 자동 허용
echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "curl GET (메서드 변경/데이터 전송 플래그 없음)"}}'
exit 0
