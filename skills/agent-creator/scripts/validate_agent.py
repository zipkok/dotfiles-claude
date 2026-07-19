#!/usr/bin/env python3
"""Validate an agents/*.md file against this repo's local convention.

이 저장소의 실제 관례(최소 frontmatter: name/description/tools만, color·XML
<example> 없음, 한국어 본문, name==파일명)를 기준으로 검증한다. 일반 Claude Code
플러그인 컨벤션(model/color 필수 등)과는 다르다 — references/writing-guide.md 참고.

"description이 호출자/시점을 담고 있는가" 같은 의미론적 판단은 이 스크립트가
아니라 SKILL.md의 LLM 자기검토 단계에서 다룬다. 여기서는 결정적 체크만 한다.
"""

import argparse
import re
import sys
from pathlib import Path

# 이 파일은 의도적으로 PyYAML에 의존하지 않는다 — 이 저장소의 agent.md frontmatter는
# 항상 평평한 스칼라 키:값 목록이므로(중첩 map 없음), 외부 의존성 없는 손파서로 충분하다.
# (skill-creator의 quick_validate.py는 yaml.safe_load를 쓰는데, 이 환경엔 PyYAML이
# 기본 설치돼 있지 않아 그대로 포팅하면 즉시 깨진다 — 의도적으로 다른 선택을 한 것.)

ALLOWED_KEYS = {"name", "description", "tools", "model"}
DIRECT_PATH_ALLOWED_KEYS = {"model"}
BLOCK_SCALAR_INDICATORS = (">", "|", ">-", "|-")


def split_frontmatter(content: str) -> tuple[str, str]:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter가 없습니다 (여는 --- 없음)")
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("frontmatter가 닫히지 않았습니다 (닫는 --- 없음)")
    frontmatter_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:]).lstrip("\n")
    return frontmatter_text, body


def parse_frontmatter(frontmatter_text: str) -> dict:
    """평평한 YAML frontmatter를 손파싱한다.

    각 키의 값은 {"type": "scalar"|"list", "value": str|list[str]}로 반환한다.
    중첩 map, 여러 줄 list-of-dict 등 복잡한 구조는 이 저장소 관례에서 쓰이지
    않으므로 지원하지 않는다 — 그런 구조가 나오면 "list"로 뭉뚱그려 반환해도
    검증 목적(스칼라인지 아닌지 판별)에는 충분하다.
    """
    lines = frontmatter_text.split("\n")
    fields: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line.startswith((" ", "\t")):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue

        key, _, rest = line.partition(":")
        key = key.strip()
        value = rest.strip()

        if not value:
            # 값이 비어 있음 — 다음 줄이 들여쓰기된 "- " 목록이면 YAML 배열
            list_items = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- "):
                list_items.append(lines[j].strip()[2:].strip())
                j += 1
            if list_items:
                fields[key] = {"type": "list", "value": list_items}
                i = j
                continue
            fields[key] = {"type": "scalar", "value": ""}
            i += 1
            continue

        if value in BLOCK_SCALAR_INDICATORS:
            continuation = []
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  ") or lines[j].startswith("\t")):
                continuation.append(lines[j].strip())
                j += 1
            fields[key] = {"type": "scalar", "value": " ".join(continuation)}
            i = j
            continue

        fields[key] = {"type": "scalar", "value": value.strip('"').strip("'")}
        i += 1

    return fields


def hangul_ratio(text: str) -> float:
    """코드펜스 밖 텍스트만 대상으로 한글/영문 비율을 계산한다."""
    without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    hangul = len(re.findall(r"[가-힣]", without_code))
    latin = len(re.findall(r"[A-Za-z]", without_code))
    total = hangul + latin
    if total == 0:
        return 1.0
    return hangul / total


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    content = path.read_text()
    try:
        frontmatter_text, body = split_frontmatter(content)
    except ValueError as e:
        return [str(e)], []

    frontmatter = parse_frontmatter(frontmatter_text)

    def get_scalar(key: str) -> str | None:
        """스칼라 값을 문자열로 반환한다. 키가 없으면 None, 리스트 타입이면 빈 문자열이 아닌 특수 마커."""
        field = frontmatter.get(key)
        if field is None:
            return None
        if field["type"] != "scalar":
            return None  # 리스트로 파싱된 경우 — 호출부에서 field["type"]로 별도 처리
        return field["value"]

    keys = set(frontmatter.keys())
    is_direct_path = "name" not in frontmatter and "description" not in frontmatter

    if is_direct_path:
        # 직접 호출형 에이전트 (예: exec-interviewer.md) — 트리거 검증 대상 아님
        unexpected = keys - DIRECT_PATH_ALLOWED_KEYS
        if unexpected:
            warnings.append(
                f"직접 호출형 에이전트로 보이는데 예상 밖 키가 있습니다: {', '.join(sorted(unexpected))}"
            )
        if not body.lstrip().startswith("#"):
            warnings.append("직접 호출형 에이전트는 보통 본문이 '# 제목'으로 시작합니다")
        warnings.append(
            "이 파일은 name/description이 없는 직접 호출형 에이전트로 판단되어 "
            "트리거 정확도 검증(run_eval.py) 대상에서 제외됩니다."
        )
        return errors, warnings

    # --- selectable agent 검증 (Task 도구의 subagent_type으로 선택 가능한 일반 에이전트) ---
    if "color" in keys:
        errors.append(
            "color 필드는 이 저장소에서 쓰지 않습니다 (일반 Claude Code 플러그인 "
            "컨벤션과 다름) — references/writing-guide.md 참고"
        )

    unexpected = keys - ALLOWED_KEYS
    unexpected -= {"color"}  # 위에서 이미 전용 메시지로 보고함
    if unexpected:
        errors.append(
            f"예상 밖 frontmatter 키: {', '.join(sorted(unexpected))} "
            f"(허용: {', '.join(sorted(ALLOWED_KEYS))})"
        )

    if "name" in frontmatter and frontmatter["name"]["type"] != "scalar":
        errors.append("name은 스칼라 문자열이어야 합니다 (리스트/맵이 아님)")
        name = None
    else:
        name = get_scalar("name")

    if not name:
        errors.append("name 필드가 없습니다")
    else:
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(
                f"name '{name}'은 kebab-case여야 합니다 (소문자·숫자·하이픈, 시작/끝/연속 하이픈 금지)"
            )
        if name != path.stem:
            errors.append(f"name('{name}')이 파일명('{path.stem}')과 일치하지 않습니다")

    if "description" in frontmatter and frontmatter["description"]["type"] != "scalar":
        errors.append("description은 스칼라 문자열이어야 합니다 (리스트/맵이 아님)")
        description = None
    else:
        description = get_scalar("description")

    if not description:
        errors.append("description 필드가 없습니다")
    else:
        if "<" in description or ">" in description:
            errors.append(
                "description에 꺾쇠괄호(< >)를 쓸 수 없습니다 — 이 저장소는 XML "
                "<example> 컨벤션을 쓰지 않습니다"
            )
        if len(description) < 20:
            warnings.append(
                "description이 매우 짧습니다 — \"무엇을 하는지 + 누가/언제 호출하는지\"를 "
                "담기에 부족할 수 있습니다 (writing-guide.md 참고)"
            )
        if len(description) > 1024:
            warnings.append(f"description이 깁니다 ({len(description)}자) — 1024자 이내를 권장합니다")

    if "tools" in frontmatter and frontmatter["tools"]["type"] != "scalar":
        warnings.append(
            "tools는 이 저장소에서 콤마로 구분한 하나의 문자열로 씁니다 "
            "(예: 'Bash, Read, Grep, Glob') — YAML 배열이 아닙니다"
        )

    if "model" in frontmatter and frontmatter["model"]["type"] != "scalar":
        warnings.append("model은 스칼라 문자열이어야 합니다")

    # --- 본문 체크 ---
    if not body.strip():
        errors.append("본문(시스템 프롬프트)이 비어 있습니다")
    elif len(body.strip()) < 20:
        errors.append("본문이 너무 짧습니다 (20자 미만)")

    if not re.search(r"^##\s*출력", body, re.MULTILINE):
        warnings.append(
            "'## 출력' / '## 출력 형식' 섹션이 안 보입니다 — 이 저장소 에이전트 대부분은 "
            "호출자가 그대로 파싱할 수 있는 엄격한 출력 템플릿으로 끝납니다"
        )
    elif not re.search(r"```", body):
        warnings.append("'## 출력' 섹션은 있지만 코드펜스(```)로 된 리터럴 템플릿이 안 보입니다")

    ratio = hangul_ratio(body)
    if ratio < 0.3:
        warnings.append(
            f"본문의 한글 비율이 낮습니다 ({ratio:.0%}) — rules/conventions.md는 "
            "대화·문서를 한국어로 쓰도록 규정합니다"
        )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="agents/*.md 파일을 이 저장소 컨벤션 기준으로 검증")
    parser.add_argument("path", type=Path, help="검증할 agent.md 경로")
    args = parser.parse_args()

    if not args.path.exists():
        print(f"파일을 찾을 수 없습니다: {args.path}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate(args.path)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\n{len(errors)}개 에러, {len(warnings)}개 경고 — 실패")
        sys.exit(1)
    elif warnings:
        print(f"\n0개 에러, {len(warnings)}개 경고 — 통과 (경고 확인 권장)")
        sys.exit(0)
    else:
        print("\n통과 — 문제 없음")
        sys.exit(0)


if __name__ == "__main__":
    main()
