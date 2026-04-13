#!/bin/bash
# 새 소스 파일에 대응하는 테스트 파일이 없으면 커밋 차단
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# git commit 명령이 아니면 통과
if ! echo "$command" | grep -q "git commit"; then
  exit 0
fi

# 초기 커밋이면 통과
if ! git rev-parse HEAD >/dev/null 2>&1; then
  exit 0
fi

# docs, chore 커밋이면 통과 (테스트 불필요)
if echo "$command" | grep -qE '"(docs|chore):'; then
  exit 0
fi

# staged 파일 중 소스 파일 확인
missing_tests=""

for file in $(git diff --cached --name-only --diff-filter=A 2>/dev/null); do
  # 소스 파일만 체크 (테스트/설정/문서 제외)
  case "$file" in
    *.test.ts|*.test.js|*.spec.ts|*.spec.js|test_*|*_test.py|tests/*|__tests__/*) continue ;;
    *.md|*.json|*.yml|*.yaml|*.toml|*.cfg|*.ini|*.lock) continue ;;
    *.gitignore|*.env*|Makefile|Dockerfile*) continue ;;
    specs/*|brainstorm/*|.specify/*|.claude/*) continue ;;
  esac

  # 소스 파일 패턴 매칭
  case "$file" in
    src/*.ts|src/*.js)
      # TypeScript/JavaScript — test 파일 확인
      base=$(echo "$file" | sed 's/\.ts$/.test.ts/' | sed 's/\.js$/.test.js/')
      if [ ! -f "$base" ] && ! git diff --cached --name-only | grep -q "$(basename "$base")"; then
        missing_tests="$missing_tests\n  - $file → $base 없음"
      fi
      ;;
    src/*.py)
      # Python — test_ 파일 확인
      dir=$(dirname "$file")
      base=$(basename "$file")
      test_file="tests/test_$base"
      if [ ! -f "$test_file" ] && ! git diff --cached --name-only | grep -q "test_$base"; then
        missing_tests="$missing_tests\n  - $file → $test_file 없음"
      fi
      ;;
  esac
done

if [ -n "$missing_tests" ]; then
  echo "{\"error\": \"🧪 테스트 파일이 없는 소스 파일이 있습니다. 테스트 없는 구현은 금지입니다.$missing_tests\"}" >&2
  exit 2
fi
