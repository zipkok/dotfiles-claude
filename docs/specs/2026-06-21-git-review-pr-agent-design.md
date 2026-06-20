# Git 리뷰 & PR 생성 에이전트 설계

작성일: 2026-06-21

## 배경 / 목적

SRE 업무에서 운영 도구(Grafana, Loki, Tempo 등)의 설정 변경을 PR로 올린다.
git 사용 경험이 없는 사용자가 "한 줄 명령"으로 변경분을 리뷰하고, 별도 명령으로
PR을 생성할 수 있도록 돕는 도구를 만든다.

- 사용자: SRE (개발자 아님). 주 대상은 설정-as-code PR.
- 설치 위치: 전역 (`~/.claude/`, 원본은 dotfiles-claude 저장소) — 특정 프로젝트에 종속되지 않음.

## 스코프

- **포함**: 로컬/PR diff 리뷰(코드 정확성 중심), PR Title/Description 자동 작성, PR 생성.
- **제외**: 운영 리스크 판단(ops-risk), 관측성 모범사례(observability-practices),
  도메인 지식 스킬(loki/tempo/grafana) — 모두 의도적으로 제외. 코드 리뷰에만 집중.

## 전체 구조

명령 2개 + 에이전트 2개. **스킬 없음**(규칙은 각 에이전트/명령 정의에 인라인).

```
/review  ->  [diff 에이전트 · 리뷰]
              1. 로컬 변경 or PR diff 수집 (대상 자동 판별)
              2. diff 확인 -> 정확성 위주 리뷰
              3. 결과 전달 (대화에 요약 + 심각도)

/pr      ->  [PR 생성 에이전트 · 작업]
              1. diff 분석
              2. Title 생성 (Conventional Commits)
              3. Description 생성 (정해진 목차)
              4. 내용 보여주고 승인 -> 브랜치 push -> gh로 PR 생성
```

- `/review`는 읽기 전용(안전). 마음껏 반복 실행.
- `/pr`은 외부 쓰기 작업 -> **실행 전 사용자 승인 게이트 필수**.

## 에이전트 1: diff 리뷰 (`config-review`)

- **미션**: 변경분이 작성자 의도대로 문법·스키마·값 범위상 올바른가를 본다.
- **입력 대상 판별**:
  - PR 번호/URL이 주어지면 -> 해당 PR diff (`gh pr diff`)
  - 아니면 -> 로컬 변경 (`git diff`, 커밋 전/후)
- **리뷰 수준**: B = 정확성 위주로 꼼꼼히 (스키마·문법·값 범위까지, 의심 부분 지적).
  도메인 스킬 없이 일반 판단으로 수행.
- **출력**: 대화에 요약 + 심각도 표기.
  - Critical : 반드시 수정
  - Warning  : 수정 권장
  - Info     : 제안/스타일

## 에이전트 2: PR 생성 (`pr-author`)

- **미션**: diff를 분석해 Title/Description을 작성하고 PR을 생성한다.
- **Title 컨벤션**: Conventional Commits (사용자 기존 커밋 규칙과 동일)
  - 형식: `<type>: <변경 요약 (한국어)>`
  - 타입: `feat` 추가 / `fix` 수정 / `refactor` 리팩터 / `docs` 문서 / `test` 테스트 / `chore` 잡무
  - 에이전트가 diff로 type 추론 + 한국어 요약 1줄.
  - 참고: https://www.conventionalcommits.org/
- **Description 목차** (6 섹션, 한국어):

      ## 요약
      - 무엇을 왜 바꿨는지 1~2줄

      ## 변경 사항
      - 주요 변경 bullet (파일/설정 단위)

      ## 변경 이유
      - 배경·맥락 (왜 필요했나)

      ## 영향 범위
      - 어떤 도구/환경/대시보드·알림에 영향이 가는지

      ## 검증 방법
      - 어떻게 확인했는지 (promtool check, 로컬 렌더, dry-run 등)

      ## 관련 링크
      - 관련 이슈·문서·대시보드 URL

- **생성 흐름**:
  1. 로컬 변경 확인.
  2. Title/Description 초안 작성 -> 사용자에게 보여줌.
  3. 승인 시: 브랜치 생성·push -> `gh pr create`로 PR 생성.
  4. 미승인/수정 요청 시 초안 수정.
- **전제**: `gh`(GitHub CLI) 설치 + 인증 필요. 미설정 시 셋업 안내.

## 파일 배치

```
commands/review.md          <- /review (diff 에이전트 오케스트레이션)
commands/pr.md              <- /pr     (PR 생성 에이전트 오케스트레이션)
agents/config-review.md     <- diff 리뷰 에이전트
agents/pr-author.md         <- PR 생성 에이전트
```

(dotfiles-claude 저장소 기준 경로. 배포 시 `~/.claude/`로 반영됨.)

## 미해결 / 셋업 필요

- `gh` 설치/인증 여부 미확인 — `/pr` 실제 동작 전 셋업 필요.
- 리뷰는 대화 요약으로 시작. 기록(파일 저장)이 필요해지면 추후 추가.
- 재사용 필요가 생기면 그때 규칙을 스킬로 추출(현재는 인라인).
