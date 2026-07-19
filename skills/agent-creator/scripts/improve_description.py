#!/usr/bin/env python3
"""Improve an agent's description based on trigger-eval results.

_call_claude() 메커니즘은 skill-creator의 improve_description.py와 동일하다
(claude -p subprocess, 세션 인증 재사용). 프롬프트 내용은 새로 썼다 — 여기서
최적화하는 대상은 "available_skills 목록에서의 트리거 여부"가 아니라 "Task
도구의 subagent_type 선택 시, 소수의 형제·built-in 후보 사이에서 이 이름이
고정된 상대들을 이기는가"이므로 프레이밍 자체가 다르다.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.utils import parse_agent_md


def _call_claude(prompt: str, model: str | None, timeout: int = 300) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, env=env, timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exited {result.returncode}\nstderr: {result.stderr}")
    return result.stdout


def improve_description(
    agent_name: str,
    agent_body: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    model: str,
    test_results: dict | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
) -> str:
    failed_triggers = [r for r in eval_results["results"] if r["should_trigger"] and not r["pass"]]
    false_triggers = [r for r in eval_results["results"] if not r["should_trigger"] and not r["pass"]]

    train_score = f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"
    if test_results:
        test_score = f"{test_results['summary']['passed']}/{test_results['summary']['total']}"
        scores_summary = f"Train: {train_score}, Test: {test_score}"
    else:
        scores_summary = f"Train: {train_score}"

    prompt = f"""당신은 Claude Code 서브에이전트 "{agent_name}"의 frontmatter `description` 필드를
최적화하고 있습니다.

이 저장소에서 서브에이전트는 Claude Code의 Task 도구가 `subagent_type`을 고를 때
description 텍스트만 보고 선택됩니다. 스킬의 available_skills 목록처럼 넓은
후보군과 경쟁하는 게 아니라, **이 저장소의 실제 형제 에이전트 몇 개 + 몇 개의
built-in 에이전트(general-purpose, Explore, Plan) + "위임하지 않음(none)"**이라는
소수의 고정된 후보 사이에서 골라지는 구조입니다. 그래서 스킬 description처럼
공격적으로 "이럴 때도 꼭 써라"식 문구를 넣는 건 오히려 잘못된 상황에서도 이
에이전트가 뽑히는 오탐(false trigger)을 늘립니다.

이 저장소의 실제 관례상 description은 항상 두 부분으로 구성됩니다:
1. **무엇을 하는지** — 이 에이전트의 역할/능력을 한두 문장으로
2. **누가/언제 호출하는지** — 어떤 상황에서, 누가(사용자가 직접, 다른 워크플로우가,
   메인 루프가) 이 에이전트를 부르는지

현재 description:
<current_description>
"{current_description}"
</current_description>

현재 점수 ({scores_summary}):
<scores_summary>
"""
    if failed_triggers:
        prompt += "선택되지 않음 (선택됐어야 하는데 실패):\n"
        for r in failed_triggers:
            other_picks = [p for p in r.get("picks", []) if p != agent_name]
            picks_note = f" (대신 선택된 후보: {', '.join(set(other_picks))})" if other_picks else ""
            prompt += f'  - "{r["query"]}" ({r["triggers"]}/{r["runs"]}회 선택됨){picks_note}\n'
        prompt += "\n"

    if false_triggers:
        prompt += "잘못 선택됨 (선택되지 말았어야 하는데 선택됨):\n"
        for r in false_triggers:
            prompt += f'  - "{r["query"]}" ({r["triggers"]}/{r["runs"]}회 선택됨)\n'
        prompt += "\n"

    if history:
        prompt += "이전 시도들 (반복하지 말고 구조적으로 다른 방식을 시도하세요):\n\n"
        for h in history:
            train_s = f"{h.get('train_passed', h.get('passed', 0))}/{h.get('train_total', h.get('total', 0))}"
            test_s = f"{h.get('test_passed', '?')}/{h.get('test_total', '?')}" if h.get("test_passed") is not None else None
            score_str = f"train={train_s}" + (f", test={test_s}" if test_s else "")
            prompt += f'<시도 {score_str}>\n'
            prompt += f'description: "{h["description"]}"\n'
            prompt += "</시도>\n\n"

    prompt += f"""</scores_summary>

에이전트 본문 (역할 파악용, 수정 대상 아님):
<agent_body>
{agent_body}
</agent_body>

실패 사례를 바탕으로 더 정확하게 선택될 새 description을 작성하세요. 다만 개별
쿼리 문구를 하나하나 나열하며 과적합하지 마세요 — 실패에서 더 넓은 카테고리의
의도/상황을 일반화해서 뽑아내세요.

요구사항:
- **반드시 한국어**로 작성 (이 저장소의 언어 규칙)
- "무엇을 하는지 + 누가/언제 호출하는지" 2단 구조를 유지
- name, tools, 본문은 건드리지 않음 — description 텍스트만 새로 작성
- 1024자 하드 리밋 (여유 있게 그 아래로)
- 명령형보다는 "무엇을 한다 + 누가 언제 부른다" 서술형 (이 저장소 실제 예시들의 문체)

<새로운_description> 태그 안에 새 description 텍스트만 답하세요. 다른 말은 하지 마세요."""

    text = _call_claude(prompt, model)

    match = re.search(r"<새로운_description>(.*?)</새로운_description>", text, re.DOTALL)
    description = match.group(1).strip().strip('"') if match else text.strip().strip('"')

    transcript: dict = {
        "iteration": iteration,
        "prompt": prompt,
        "response": text,
        "parsed_description": description,
        "char_count": len(description),
        "over_limit": len(description) > 1024,
    }

    if len(description) > 1024:
        shorten_prompt = (
            f"{prompt}\n\n---\n\n이전 시도가 {len(description)}자로 1024자 하드 리밋을 "
            f"넘었습니다:\n\n\"{description}\"\n\n핵심 트리거 정보는 유지하면서 1024자 "
            f"이내로 줄여 다시 쓰세요. <새로운_description> 태그 안에만 답하세요."
        )
        shorten_text = _call_claude(shorten_prompt, model)
        match = re.search(r"<새로운_description>(.*?)</새로운_description>", shorten_text, re.DOTALL)
        shortened = match.group(1).strip().strip('"') if match else shorten_text.strip().strip('"')

        transcript["rewrite_prompt"] = shorten_prompt
        transcript["rewrite_response"] = shorten_text
        transcript["rewrite_description"] = shortened
        transcript["rewrite_char_count"] = len(shortened)
        description = shortened

    transcript["final_description"] = description

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"improve_iter_{iteration or 'unknown'}.json").write_text(
            json.dumps(transcript, indent=2, ensure_ascii=False)
        )

    return description


def main():
    parser = argparse.ArgumentParser(description="Improve an agent description based on eval results")
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON (from run_eval.py)")
    parser.add_argument("--agent-path", required=True, help="Path to agents/<name>.md")
    parser.add_argument("--history", default=None, help="Path to history JSON (previous attempts)")
    parser.add_argument("--model", required=True, help="Model for improvement")
    parser.add_argument("--verbose", action="store_true", help="Print thinking to stderr")
    args = parser.parse_args()

    agent_path = Path(args.agent_path)
    if not agent_path.exists():
        print(f"Error: agent file not found: {agent_path}", file=sys.stderr)
        sys.exit(1)

    eval_results = json.loads(Path(args.eval_results).read_text())
    history = json.loads(Path(args.history).read_text()) if args.history else []

    parsed = parse_agent_md(agent_path)
    current_description = eval_results["description"]

    if args.verbose:
        print(f"Current: {current_description}", file=sys.stderr)
        print(f"Score: {eval_results['summary']['passed']}/{eval_results['summary']['total']}", file=sys.stderr)

    new_description = improve_description(
        agent_name=parsed["name"],
        agent_body=parsed["body"],
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        model=args.model,
    )

    if args.verbose:
        print(f"Improved: {new_description}", file=sys.stderr)

    output = {
        "description": new_description,
        "history": history + [{
            "description": current_description,
            "passed": eval_results["summary"]["passed"],
            "failed": eval_results["summary"]["failed"],
            "total": eval_results["summary"]["total"],
            "results": eval_results["results"],
        }],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
