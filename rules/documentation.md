# 문서화

## 프로젝트 문서

- 프로젝트 관련 문서는 `docs/` 디렉토리에 작성한다
- 설계 문서, 기술 결정, 가이드 등 프로젝트 지식을 축적한다
- `docs/specs/` — 기능/변경 단위 설계 문서. 구현 전에 먼저 기록하고, 구현은 별도 세션에서 진행
- `docs/adrs/` — Architecture Decision Record. 결정 1개 = 파일 1개, 순차 번호(`0001-제목.md`), Nygard
  형식(Title/Status/Context/Decision/Consequences). 작성 후 변경 금지 — 뒤집히면 새 ADR을 만들고 이전
  것은 `Superseded by [#NNNN]`으로 표시
- `docs/rfc/` — 여러 입장을 수렴해 합의된 결론에 도달하는 논의 문서. 폴더 단위 순차 번호
  (`0001-주제/`), 폴더 안에 spec/plan/result/review 4단계 파일. `ship-discussion` 스킬이 자동 생성
- `docs/` 루트 — 프로젝트 가이드, 개념/배경 참고 문서, 온보딩 문서 (특정 spec·adr·rfc에 속하지 않는 지식)

## 변경 이력

- `CHANGELOG.md`에 모든 변경사항을 기록한다
- 형식: 기능별, 작업별로 날짜와 함께 기록 (릴리스 노트 역할)
- 카테고리: 추가 / 변경 / 수정 / 삭제
