# Claude Code Hook 생명주기

settings.json의 `hooks`에 등록할 수 있는 이벤트(트리거 시점)를 세션 생명주기 흐름으로 정리한 문서.

- 🔴 = exit code 2로 **흐름 차단 가능** (검문소)
- ⚪ = **알림/사이드이펙트 전용** (이미 일어난 일 — 차단 불가)
- ★ = 현재 이 레포(`hooks/` + `settings.json`)가 실제 사용 중인 단계

## 생명주기 도식

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code 세션 생명주기                      │
└─────────────────────────────────────────────────────────────────┘

  ●  세션 시작
  │
  ├─⚪ SessionStart        (startup·resume·clear·compact)
  │                         └ 현재: ccstatusline, last30days
  │
  ▼
┌───────────────────────── 턴 루프 (반복) ─────────────────────────┐
│                                                                   │
│   사용자 입력                                                      │
│      │                                                            │
│      ├─🔴 UserPromptSubmit   ← 프롬프트 거부 가능                   │
│      │                         └ 현재: ccstatusline               │
│      ▼                                                            │
│   Claude 사고 → 도구 호출 결정                                     │
│      │                                                            │
│      │   ┌────────── 도구 호출 루프 (반복) ──────────┐            │
│      │   │                                            │            │
│      ├──▶│  ├─🔴 PreToolUse   ← 도구 차단 가능        │            │
│      │   │  │     └ 현재: lint, main보호, require-test│            │
│      │   │  │              sensitive, build-artifacts │            │
│      │   │  ▼                                         │            │
│      │   │  [ 도구 실행 ]                             │            │
│      │   │  │                                         │            │
│      │   │  ├─⚪ PostToolUse        (성공)            │            │
│      │   │  │     └ 현재: notify-claude-md            │            │
│      │   │  ├─⚪ PostToolUseFailure (실패)            │            │
│      │   │  └─⚪ PreCompact         (컨텍스트 압축 전) │            │
│      │   │                                            │            │
│      │   │  · 서브에이전트면:                          │            │
│      │   │    ⚪ SubagentStart → ⚪ SubagentStop      │            │
│      │   └────────────────────────────────────────────┘          │
│      ▼                                                            │
│   Claude 응답 완료                                                │
│      │                                                            │
│      └─🔴 Stop   ← "아직 끝내지 마" 강제 가능                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
  │
  ▼
  ⚪ SessionEnd           (clear·resume·logout)
  │
  ●  세션 종료


  [상시 발생 — 루프와 무관]
  ⚪ Notification        알림 발송 시 (권한 요청·인증 등)
  🔴 PermissionRequest   권한 대화 표시 시 (거부 가능)
```

## 차단 가능 vs 알림 전용

```
  차단 가능 (exit 2 = 흐름 멈춤)        알림 전용 (이미 일어난 일)
  ┌──────────────────────────┐        ┌──────────────────────────┐
  │ 🔴 UserPromptSubmit       │        │ ⚪ SessionStart / End     │
  │ 🔴 PreToolUse        ★    │        │ ⚪ PostToolUse       ★    │
  │ 🔴 Stop                   │        │ ⚪ SubagentStart/Stop     │
  │ 🔴 PermissionRequest      │        │ ⚪ PreCompact             │
  └──────────────────────────┘        │ ⚪ Notification           │
                                       └──────────────────────────┘
```

## 주요 이벤트 표

| 이벤트 | 실행 시점 | 차단(exit 2) | matcher |
|--------|----------|:---:|---------|
| **UserPromptSubmit** | 사용자 입력 처리 직전 | ✅ 프롬프트 거부 | ✗ |
| **PreToolUse** | 도구 호출 전 | ✅ 호출 차단 | ✅ 도구명 |
| **PostToolUse** | 도구 성공 후 | ✗ | ✅ 도구명 |
| **PostToolUseFailure** | 도구 실패 후 | ✗ | ✅ 도구명 |
| **Stop** | Claude 응답 완료 시 | ✅ 대화 계속 강제 | ✗ |
| **SubagentStart / SubagentStop** | 서브에이전트 생성 / 완료 | ✗ | ✅ 에이전트 타입 |
| **SessionStart** | 세션 시작/재개 | ✗ | ✅ `startup`/`resume`/`clear`/`compact` |
| **SessionEnd** | 세션 종료 | ✗ | – |
| **PreCompact** | 컨텍스트 압축 전 | ✗ | – |
| **Notification** | 알림 발송 시 | ✗ | ✅ 타입 |
| **PermissionRequest** | 권한 대화 표시 시 | ✅ 권한 거부 | ✗ |

## 현재 레포 훅 매핑

| 훅 파일 | 이벤트 | matcher | 동작 |
|---------|--------|---------|------|
| `pre-commit-lint.sh` | PreToolUse | Bash | lint 실패 시 커밋 차단 |
| `protect-main-branch.sh` | PreToolUse | Bash | main 직접 커밋 경고(권고) |
| `require-tests.sh` | PreToolUse | Bash | 테스트 없는 새 소스 커밋 차단 |
| `protect-sensitive-files.sh` | PreToolUse | Write\|Edit | 민감 파일 수정 차단 |
| `block-build-artifacts.sh` | PreToolUse | Write\|Edit | 빌드 산출물 쓰기 차단 |
| `notify-claude-md-update.sh` | PostToolUse | Write\|Edit | CLAUDE.md 수정 시 품질검사 안내 |

> 현재 6개 훅이 전부 `PreToolUse` / `PostToolUse` 두 단계에만 모여 있음.
> `SessionStart`(미러 자동 동기화), `Stop`(미커밋 변경 알림) 등으로 확장 여지 있음.

## 참고

- 공식 문서: https://code.claude.com/docs/en/hooks
