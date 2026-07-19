#!/usr/bin/env python3
"""Run trigger-accuracy evaluation for an agent's description.

skill-creator의 run_eval.py는 실제 `claude -p`를 스킬이 등록된 상태로 돌려
Skill 도구 호출 여부를 관찰한다. 에이전트는 다르다 — `Task` 도구의
`subagent_type` 선택으로 트리거되는데, 이 저장소의 실제 형제 에이전트 중
일부(`pr-author`)는 브랜치 push·PR 생성 같은 부수효과가 있어 그 방식을 그대로
포팅하면 실측 루프가 실수로 부수효과를 일으킬 위험이 있다.

그래서 여기서는 **실제 도구 호출이 전혀 없는 순수 분류 프롬프트**로 트리거를
시뮬레이션한다: `claude -p`에 "사용자 요청 + 후보 서브에이전트 {name,
description} 목록"만 보여주고 어느 이름을 고를지 텍스트로만 답하게 한다.
skill-creator의 실측 방식보다 충실도가 낮은 프록시라는 점을 감안할 것 —
references/writing-guide.md와 SKILL.md에 이 트레이드오프를 명시했다.

반환 스키마는 skill-creator의 run_eval.py와 동일하게 유지한다
({query, should_trigger, trigger_rate, triggers, runs, pass} + summary) —
run_loop.py/improve_description.py/generate_report.py가 그대로 재사용된다.
"""

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.list_sibling_agents import build_candidate_set
from scripts.utils import parse_agent_md


def _shuffled_candidates(candidates: list[dict], query: str) -> list[dict]:
    """후보 순서를 쿼리별로 결정적으로 섞는다 (위치 편향 완화, 매 실행 재현 가능)."""
    seed = int(hashlib.sha256(query.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    shuffled = candidates.copy()
    rng.shuffle(shuffled)
    return shuffled


def _call_claude(prompt: str, model: str | None, timeout: int) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])
    # CLAUDECODE 환경변수를 제거해야 Claude Code 세션 안에서 claude -p를 중첩 실행할 수 있다
    # (대화형 터미널 충돌 방지용 가드라서 프로그래매틱 subprocess 사용은 안전하다).
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, env=env, timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exited {result.returncode}\nstderr: {result.stderr}")
    return result.stdout


def build_classification_prompt(query: str, candidates: list[dict]) -> str:
    candidate_lines = "\n".join(
        f"- name: {c['name']}\n  description: {c['description']}" for c in candidates
    )
    return f"""당신은 Claude Code의 서브에이전트 선택기(Task 도구의 subagent_type 결정)를
시뮬레이션합니다. 아래 사용자 요청과 후보 서브에이전트 목록(name + description)만
보고, 실제 선택기처럼 행동해 어떤 subagent_type에 위임할지(또는 위임하지 않을지)
판단하세요. 후보를 실제로 실행하지 마세요 — 이것은 순수 분류 작업입니다.

사용자 요청:
"{query}"

후보 서브에이전트:
{candidate_lines}

정확히 하나의 name만 아래 형식으로 답하세요. 다른 말은 하지 마세요.
<선택>{{name}}</선택>"""


def parse_selection(response: str, candidates: list[dict]) -> str:
    match = re.search(r"<선택>(.*?)</선택>", response, re.DOTALL)
    if match:
        picked = match.group(1).strip()
    else:
        picked = response.strip()

    names = {c["name"] for c in candidates}
    if picked in names:
        return picked
    # 관대한 폴백: 응답 안에 후보 이름이 정확히 하나만 등장하면 그것으로 간주
    found = [n for n in names if n in picked]
    if len(found) == 1:
        return found[0]
    return "none"


def run_single_query(
    query: str, candidates: list[dict], timeout: int, model: str | None,
) -> str:
    """분류 프롬프트를 1회 호출해 선택된 이름을 반환한다."""
    shuffled = _shuffled_candidates(candidates, query)
    prompt = build_classification_prompt(query, shuffled)
    response = _call_claude(prompt, model, timeout)
    return parse_selection(response, shuffled)


def run_eval(
    eval_set: list[dict],
    agent_name: str,
    description: str,
    sibling_candidates: list[dict],
    num_workers: int,
    timeout: int,
    runs_per_query: int = 3,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """평가 세트 전체를 돌려 결과를 반환한다.

    sibling_candidates는 대상 에이전트를 제외한 (형제 + built-in + none) 목록이며,
    여기에 현재 테스트 중인 description으로 대상 자신을 추가해 완전한 후보
    집합을 구성한다.
    """
    full_candidates = sibling_candidates + [{"name": agent_name, "description": description}]

    results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(run_single_query, item["query"], full_candidates, timeout, model)
                future_to_info[future] = (item, run_idx)

        query_picks: dict[str, list[str]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            query_picks.setdefault(query, [])
            try:
                query_picks[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_picks[query].append("none")

    for query, picks in query_picks.items():
        item = query_items[query]
        triggers = sum(1 for p in picks if p == agent_name)
        trigger_rate = triggers / len(picks)
        should_trigger = item["should_trigger"]
        did_pass = trigger_rate >= trigger_threshold if should_trigger else trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": triggers,
            "runs": len(picks),
            "pass": did_pass,
            "picks": picks,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "agent_name": agent_name,
        "description": description,
        "results": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for an agent description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--agent-path", required=True, help="Path to agents/<name>.md")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model for the classification call")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    agent_path = Path(args.agent_path)
    if not agent_path.exists():
        print(f"Error: agent file not found: {agent_path}", file=sys.stderr)
        sys.exit(1)

    parsed = parse_agent_md(agent_path)
    description = args.description or parsed["description"]
    sibling_candidates = build_candidate_set(parsed["name"])

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        agent_name=parsed["name"],
        description=description,
        sibling_candidates=sibling_candidates,
        num_workers=args.num_workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  [{status}] rate={r['triggers']}/{r['runs']} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
