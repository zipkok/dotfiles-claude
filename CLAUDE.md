# Global Rules

모든 프로젝트에 공통 적용되는 규칙.

## 프로젝트의 CLAUDE.md

- 요청하는 내용은 다음에도 적용될 수 있도록 CLAUDE.md에 업데이트

## ~/.claude 심볼릭 링크 구조

- `~/.claude`는 실체 디렉터리다. 이 저장소(dotfiles-claude)의 설정/콘텐츠 항목만 개별 symlink로 연결되어 있다: `agents/`, `commands/`, `hooks/`, `rules/`, `skills/`, `output-styles/`, `workflows/`, `docs/`, `agent-memory/`, `CLAUDE.md`, `settings.json`, `README.md`, `CHANGELOG.md`, `claude-powerline.json`, `plugins/`의 매니페스트 3종(`blocklist.json`, `installed_plugins.json`, `known_marketplaces.json`) + `plugins/README.md`.
- 세션·캐시·데몬 로그 등 런타임 데이터(`sessions/`, `projects/`, `cache/`, `daemon/`, `history.jsonl` 등과 `plugins/cache`·`plugins/data`·`plugins/marketplaces`)는 저장소 밖 실제 `~/.claude`에 그대로 존재하며 저장소에는 절대 들어오지 않는다.
- 저장소에 새 설정 폴더/파일을 추가하면 `~/.claude`에도 `ln -s`로 수동 연결해야 한다 (자동 반영 안 됨).

