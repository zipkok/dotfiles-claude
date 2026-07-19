#!/usr/bin/env python3
"""Build the fixed candidate set used by the trigger-accuracy loop.

후보 집합 = (이 저장소의 실제 selectable agents/*.md, 대상 제외)
          + (수동 유지되는 references/builtin-subagents.json)
          + (합성 "none" 옵션 — 위임 없이 메인 루프가 직접 처리)

run_loop.py의 한 실행(iteration 여러 번) 동안 이 집합은 고정되어야 한다 — 매번
다시 샘플링하면 반복 간 점수 변화가 description 변경 때문인지 후보 집합 변화
때문인지 구분할 수 없다. 그래서 이 스크립트는 한 번 호출해 결과를 캐시해두고
쓰는 용도로 설계되었다 (run_eval.py가 실행마다 다시 부르지 않고, run_loop.py가
루프 시작 전 한 번 계산해 넘긴다).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.utils import REPO_AGENTS_DIR, list_repo_agents

NONE_OPTION = {
    "name": "none",
    "description": "위임 없이 메인 대화 루프가 직접 처리하거나, 이 요청에 맞는 서브에이전트가 없음",
}

BUILTIN_PATH = Path(__file__).resolve().parent.parent / "references" / "builtin-subagents.json"


def build_candidate_set(target_name: str, agents_dir: Path | None = None) -> list[dict]:
    """대상 에이전트를 제외한 형제 selectable 에이전트 + built-in + none을 반환한다."""
    siblings = [
        {"name": a["name"], "description": a["description"]}
        for a in list_repo_agents(agents_dir, exclude_name=target_name)
        if "error" not in a and a["selectable"]
    ]

    builtin_data = json.loads(BUILTIN_PATH.read_text())
    builtins = builtin_data["agents"]

    return siblings + builtins + [NONE_OPTION]


def main():
    parser = argparse.ArgumentParser(description="트리거 테스트용 고정 후보 집합을 만든다")
    parser.add_argument("--target", required=True, help="후보에서 제외할 대상 에이전트 이름")
    parser.add_argument("--agents-dir", default=None, help="agents/ 디렉터리 경로 (기본: 저장소 실제 agents/)")
    args = parser.parse_args()

    agents_dir = Path(args.agents_dir) if args.agents_dir else REPO_AGENTS_DIR
    candidates = build_candidate_set(args.target, agents_dir)
    print(json.dumps(candidates, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
