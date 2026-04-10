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
/init-project <project-name> [type]
```

- `project-name`: 프로젝트 이름 (디렉토리명)
- `type` (선택): `web` | `api` | `game` | `python` (기본값: `web`)

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

### 6. spex 초기화 안내

프로젝트 생성이 완료되면 사용자에게 안내합니다:

```
프로젝트가 생성되었습니다.

다음 단계:
1. spex:init 으로 .specify/ 디렉토리를 초기화하세요
2. /speckit-constitution 으로 프로젝트 원칙을 정의하세요
3. 새 기능 개발 시 spex:ship --ask smart 를 사용하세요
```

## 주의사항

- 이미 존재하는 디렉토리에는 실행하지 않습니다 (덮어쓰기 방지)
- spex:init은 별도로 실행해야 합니다 (specify CLI 의존)
- 프로젝트 타입별 차이는 CLAUDE.md 템플릿에만 반영됩니다
