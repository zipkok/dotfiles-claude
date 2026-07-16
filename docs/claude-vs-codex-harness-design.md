# Claude Code(CLAUDE.md) vs Codex CLI(AGENTS.md) 하네스 구조 비교·설계

`docs/agent-harness-design.md`에서 정리한 Harness 개념을 기준으로, Claude Code와 OpenAI Codex CLI 두 도구가 실제로 하네스를 어떻게 구조화하는지 비교하고, 이 저장소를 Codex 관점에서 설계한다면 어떤 모습이 될지 정리한 문서. Codex CLI를 실제로 설치·실행한 것은 아니며, 2026-07 시점 공식 문서를 조사해 분석했다.

## 배경/목적

`CLAUDE.md`가 `AGENTS.md`로 바뀌는 것 뿐이라는 인상과 달리, 두 도구는 하네스의 각 층(지침 파일, 스킬, 서브에이전트, 훅, 권한, MCP, 메모리)을 서로 다르게 구현한다. 목적은 (1) 두 도구의 공통점/차이점을 층별로 비교하고, (2) 이 저장소 구조를 Codex 방식으로 옮긴다면 어떤 설계가 되는지 정리하는 것. 실제 마이그레이션이나 Codex 설치는 스코프 밖.

## 스코프

- 포함: 지침 파일 탐색 방식, 스킬, 서브에이전트, 워크플로 오케스트레이션, 훅, 권한/샌드박스, MCP, 메모리 — 층별 비교와 Codex 관점 구조 설계안
- 제외: Codex CLI 실제 설치·인증·실행, 이 저장소의 실제 이식 작업

## 층별 비교

| 층 | Claude Code | Codex CLI |
|---|---|---|
| 지침 파일 | `CLAUDE.md` (프로젝트 루트) + `rules/*.md` (경로/호출 기반 지연 로드) | `AGENTS.md` — 글로벌(`~/.codex`) + Git 루트부터 cwd까지 디렉터리별 최대 1개, 하위가 상위를 오버라이드하며 병합. `project_doc_max_bytes`(기본 32KiB)로 총량 제한, 세션마다 재수집(캐시 없음) |
| 대체/보조 파일명 | 없음 (컨벤션으로만 구분) | `project_doc_fallback_filenames`로 `AGENTS.md` 없을 때 대체 파일명 지정 가능 |
| 재사용 절차(스킬) | `skills/<name>/SKILL.md` — 이름을 통해 명시 호출 | `.codex/skills/<name>/SKILL.md` (프로젝트) + `~/.codex/skills/`(개인) — cwd부터 루트까지 `.agents/skills` 탐색. name/description만 상시 로드, 본문은 호출 시 로드 (Claude와 동일한 "점진적 공개" 모델) |
| 서브에이전트 정의 | `agents/*.md` — 단일 마크다운 + frontmatter로 프롬프트/도구/모델 지정 | `agents/<name>/AGENTS.md` — 폴더 단위, 공통 규칙은 `agents/AGENTS.md`. 최대 8개 동시 실행, 각자 독립 컨텍스트 창 + 클라우드 샌드박스 |
| 워크플로 오케스트레이션 | `workflows/*.js` — 결정론적 스크립트로 여러 서브에이전트를 하나의 명령으로 조립 | 네이티브 기본 기능 없음. 병렬 서브에이전트 실행 자체는 되지만, Claude의 `workflows/*.js` 같은 스크립트 오케스트레이션 레이어는 별도로 **Agents SDK**를 붙여야 함 — 구조적 공백 |
| 훅(가드레일) | `hooks/*.sh` + `settings.json`의 `hooks` — 12개 이벤트(SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, PreCompact, SubagentStart/Stop, Stop, SessionEnd, Notification, PermissionRequest) | `.codex/hooks.json`(또는 `config.toml`의 `[hooks]`) — 10개 이벤트(SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PreCompact, **PostCompact**, SubagentStart/Stop, Stop). JSON 스키마(`matcher` + `hooks: [{type, command}]`)가 Claude와 사실상 동일 |
| 훅 차단 방식 | exit code 2 | exit code 2 또는 JSON `continue:false` — 사실상 동일 |
| 권한/샌드박스 | `settings.json`의 `permissions.deny` + `PreToolUse` 훅 조합으로 강제 | `config.toml`의 `sandbox_mode`(read-only/workspace-write/danger-full-access) + `approval_policy` + `[permissions.<profile>.filesystem/network]` — 경로/도메인 glob까지 선언적으로 세분화. Claude보다 권한 스키마 자체가 더 1급 시민 |
| MCP | `.mcp.json` (JSON) | `config.toml`의 `[mcp_servers.<id>]` (TOML) + `enabled_tools`/`disabled_tools`로 도구 단위 allow/deny |
| 메모리 | `agent-memory/<agent>/MEMORY.md` + `~/.claude/projects/`에 세션 간 메모리 자동 저장 — 코어 내장 기능 | 코어 내장 없음. SQLite 기반 영속 메모리 MCP 서버 등 **서드파티 MCP로 구현** — 가장 큰 구조적 차이 |
| 설정 파일 포맷 | JSON (`settings.json`, `.mcp.json`) | TOML (`config.toml`) — 관례 자체가 다름 |

## 공통점

- 지침 파일(CLAUDE.md/AGENTS.md)은 "요청 사항"이고, 훅+권한 설정은 "강제 사항"이라는 2단 구조가 동일
- 훅 이벤트 이름과 JSON 스키마가 사실상 1:1 대응 — 스크립트 자체는 거의 그대로 이식 가능
- 스킬의 "이름/설명만 상시 로드, 본문은 호출 시 로드"라는 점진적 공개 모델이 동일
- 서브에이전트가 독립 컨텍스트 창을 갖는다는 설계 원칙이 동일

## 차이점

- **지침 파일 탐색 방식이 다름**: Claude는 `rules/*.md`를 경로/스킬 호출 기준으로 지연 로드하는 반면, Codex는 "디렉터리마다 최대 1개 AGENTS.md"를 물리적 경로 계층 그대로 병합. 즉 Claude의 `rules/` 폴더 하나에 여러 규칙 파일을 topic별로 쪼개두는 방식은 Codex에서 그대로 재현되지 않고, 서브디렉터리별 `AGENTS.md`로 재배치하거나 `project_doc_fallback_filenames`로 흉내내야 함
- **워크플로 오케스트레이션 공백**: Claude의 `workflows/*.js`(결정론적 다단계 스크립트)에 대응하는 1급 기능이 Codex 코어에는 없음 — Agents SDK로 별도 구축 필요
- **메모리가 코어 vs 애드온**: Claude Code는 세션 간 메모리를 하네스 코어 기능으로 내장하지만, Codex는 서드파티 MCP 서버에 의존
- **권한 스키마의 성숙도**: Codex의 `sandbox_mode`/`approval_policy`/`[permissions.*]`가 Claude의 `permissions.deny` + 훅 조합보다 더 세분화·선언적

## Codex 관점 구조 설계안 (이 저장소를 Codex로 옮긴다면)

```
프로젝트 루트/
├─ AGENTS.md                     ← 최상위 CLAUDE.md 대응
├─ .codex/
│  ├─ config.toml                ← settings.json + .mcp.json 통합 대응
│  ├─ hooks.json                 ← hooks/*.sh 스크립트는 거의 그대로 재사용
│  ├─ skills/                    ← skills/*/SKILL.md 그대로 이식
│  └─ agents/
│     ├─ AGENTS.md               ← 서브에이전트 공통 규칙
│     ├─ code-reviewer/AGENTS.md ← agents/code-reviewer.md 대응(파일→폴더)
│     └─ debugger/AGENTS.md
├─ rules/ 는 유지하되 project_doc_fallback_filenames로만 인식되거나,
│  실질적으로는 src/api/AGENTS.md, src/payments/AGENTS.md 처럼
│  하위 디렉터리별 AGENTS.md로 재배치하는 편이 Codex 철학에 더 맞음
└─ workflows/*.js 는 Codex 네이티브 대응이 없어 Agents SDK 스크립트로 별도 작성 필요
```

`docs/agent-harness-design.md`의 10장(Self-Harness)·10장 실무 교훈("평가자·권한은 루프 밖에 둔다")이 두 도구 모두에서 훅+권한 스키마로 이미 실현되고 있다는 점이 이번 조사로 확인됨.

## 미해결/셋업 필요

- 이 분석은 문서 조사 기반이며, 실제 Codex CLI를 설치·인증해 위 구조가 그대로 동작하는지 검증되지 않음
- Codex의 워크플로 오케스트레이션(Agents SDK 필요 여부)은 버전에 따라 달라질 수 있어 재확인 필요
- Codex의 메모리 코어 내장 여부도 빠르게 변하는 영역이라 추후 릴리스 노트 확인 필요

## 출처

- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Build skills](https://developers.openai.com/codex/skills)
- [Codex CLI Custom Agent Definitions](https://codex.danielvaughan.com/2026/04/27/codex-cli-custom-agent-definitions-toml-specialised-subagents/)
- [The Codex CLI Customisation Stack](https://codex.danielvaughan.com/2026/04/12/codex-cli-customisation-stack-unified-system/)
- 이 저장소의 `docs/hook-lifecycle.md` (Claude Code 훅 이벤트 12종 정리)
