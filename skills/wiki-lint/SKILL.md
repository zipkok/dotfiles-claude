---
name: wiki-lint
description: Use when the user asks for wiki health check - triggers on "lint", "점검", "정리", "건강 체크" or periodically after multiple ingests to maintain wiki quality
---

# Wiki Lint

위키의 건강 상태를 점검하고 문제를 보고하는 프로세스.

## Wiki 루트

`/Users/woobs/Repository/llm_wiki/LLM_Wiki`

모든 경로는 이 루트 기준. 어떤 프로젝트에서든 이 절대 경로로 접근한다.

## 점검 항목

| 항목 | 설명 | 심각도 |
|------|------|--------|
| 고아 페이지 | 어디서도 `[[링크]]`되지 않은 페이지 | ⚠️ |
| 깨진 링크 | 존재하지 않는 페이지를 참조하는 `[[링크]]` | 🔴 |
| 모순 정보 | 페이지 간 상충하는 내용 | 🔴 |
| index 누락 | `wiki/index.md`에 등록되지 않은 페이지 | ⚠️ |
| 출처 누락 | 출처 섹션이 비어있는 페이지 | 💡 |
| 빈 페이지 | 내용이 거의 없는 페이지 | 💡 |

## 프로세스

1. `wiki/` 전체 스캔
2. 모든 `[[링크]]` 수집 → 깨진 링크 확인
3. 각 페이지의 인바운드 링크 수 확인 → 고아 페이지 식별
4. index.md와 실제 페이지 목록 비교
5. 보고서 출력

## 보고서 형식

```markdown
# 🔍 Wiki Lint 보고서 (YYYY-MM-DD)

## 요약
- 총 페이지: N개
- 문제 발견: N개

## 🔴 Critical
- [내용]

## ⚠️ Warning
- [내용]

## 💡 Suggestion
- [내용]

## ✅ 건강한 항목
- [내용]
```

## 자동 수정

사용자 승인 시 다음을 자동 수정:
- index.md에 누락 페이지 추가
- 깨진 링크 제거 또는 페이지 생성 제안
- changelog에 lint 수행 기록
