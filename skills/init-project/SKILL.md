---
name: init-project
description: 새 프로젝트 폴더를 생성하고 하네스(CLAUDE.md, .claude/, .specify/)를 자동 구축합니다
user-invocable: true
disable-model-invocation: true
---

# /init-project

새 프로젝트의 하네스를 자동으로 구축합니다.

## 사용법

```
/init-project <project-name>
```

- `project-name`: 프로젝트 이름 (디렉토리명)

## 동작

다음 순서로 실행합니다:

### 1. 프로젝트 디렉토리 생성

```bash
mkdir -p ~/Repository/<project-name>
cd ~/Repository/<project-name>
```

### 2. CLAUDE.md 생성

`~/.claude/templates/base/CLAUDE.md.tmpl` 템플릿을 기반으로 생성합니다.

사용자에게 다음을 질문합니다:
- 프로젝트 설명 (한 줄)
- 기술 스택
- 실행 명령어
- 테스트 명령어

템플릿의 `{{placeholder}}`를 실제 값으로 치환하여 `CLAUDE.md`를 작성합니다.

### 3. .claude/ 디렉토리 구조 생성

```bash
mkdir -p .claude/agents
```

`~/.claude/templates/base/settings.local.json.tmpl`을 기반으로 `.claude/settings.local.json`을 생성합니다. `{{PROJECT_PATH}}`를 실제 경로로 치환합니다.

### 4. CHANGELOG.md 생성

```markdown
# Changelog

## [0.1.0] - YYYY-MM-DD

### 추가
- 프로젝트 초기화
```

날짜는 오늘 날짜를 사용합니다.

### 5. git init

```bash
git init
git add -A
git commit -m "chore: 프로젝트 초기화

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

### 6. spex 초기화

specify CLI가 설치되어 있는지 확인 후, `spex-init.sh`를 직접 실행합니다:

```bash
bash ~/.claude/plugins/cache/cc-rhuss-marketplace/spex/*/spex/scripts/spex-init.sh
```

- `NEED_INSTALL` 출력 시: specify CLI 설치 안내를 표시하고 중단
- `RESTART_REQUIRED` 출력 시: `.specify/`와 `.claude/skills/speckit-*/`가 새로 생성된 것. 사용자에게 **Claude Code 재시작**을 안내
- `READY` 출력 시: 이미 초기화 완료

> **중요**: 스킬이 새로 설치되면 Claude Code를 재시작해야 `/speckit-*` 명령어가 보입니다.

초기화 후 traits와 권한을 기본값으로 자동 설정합니다 (질문하지 않음):

```bash
bash ~/.claude/plugins/cache/cc-rhuss-marketplace/spex/*/spex/scripts/spex-traits.sh init --enable "superpowers,deep-review,worktrees"
bash ~/.claude/plugins/cache/cc-rhuss-marketplace/spex/*/spex/scripts/spex-traits.sh permissions standard
```

기본 설정:
- **traits**: `superpowers`, `deep-review`, `worktrees`
- **permissions**: `standard` (spex 스크립트만 자동 승인)

### 7. 완료 안내

```
프로젝트가 생성되었습니다.
Claude Code를 재시작하면 /speckit-* 명령어를 사용할 수 있습니다.

다음 단계:
1. Claude Code 재시작
2. 새 기능 개발 시 spex:ship --ask smart 를 사용하세요
```

## 주의사항

- 이미 존재하는 디렉토리에는 실행하지 않습니다 (덮어쓰기 방지)
- 기술 스택은 템플릿 질문으로 결정됩니다 (타입 파라미터 없음)
