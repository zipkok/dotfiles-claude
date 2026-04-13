#!/bin/bash
# 커밋 전 lint 자동 실행 (언어별 분기)
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# git commit 명령이 아니면 통과
if ! echo "$command" | grep -q "git commit"; then
  exit 0
fi

run_lint() {
  local result=$1
  if [ $? -ne 0 ]; then
    echo "{\"error\": \"lint 실패. 커밋 전에 lint 에러를 수정해주세요.\\n$result\"}" >&2
    exit 2
  fi
}

# Node.js / TypeScript — package.json의 lint 스크립트
if [ -f "package.json" ] && jq -e '.scripts.lint' package.json > /dev/null 2>&1; then
  result=$(npm run lint --silent 2>&1)
  run_lint "$result"

# Python — ruff, flake8, pylint 순서로 탐지
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  if command -v ruff &>/dev/null; then
    result=$(ruff check . 2>&1)
    run_lint "$result"
  elif command -v flake8 &>/dev/null; then
    result=$(flake8 . 2>&1)
    run_lint "$result"
  fi

# Go
elif [ -f "go.mod" ]; then
  if command -v golangci-lint &>/dev/null; then
    result=$(golangci-lint run 2>&1)
    run_lint "$result"
  fi
fi
