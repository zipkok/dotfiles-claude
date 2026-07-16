# plugins/

Claude Code CLI가 관리하는 플러그인 상태 파일. 직접 편집하지 않고 `/plugin` 커맨드로 관리한다.

| 파일 | 내용 |
|------|------|
| `known_marketplaces.json` | 등록된 마켓플레이스 목록 |
| `installed_plugins.json` | 설치된 플러그인 버전·경로·설치 시각 |
| `blocklist.json` | 차단된 플러그인 목록 |

실제 활성화 여부는 `settings.json`의 `enabledPlugins`에서 결정된다. 현재 설치·활성화 상태는 저장소 루트 `README.md`의 플러그인 표 참조.
