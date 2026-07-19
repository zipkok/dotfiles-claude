"""Shared utilities for agent-creator scripts."""

from pathlib import Path

REPO_AGENTS_DIR = Path(__file__).resolve().parents[3] / "agents"


def parse_agent_md(agent_path: Path) -> dict:
    """Parse an agents/*.md file.

    Returns a dict with:
      - name: str (frontmatter `name`, or the filename stem if absent)
      - description: str ("" if absent — direct-path agents have none)
      - tools: str ("" if absent)
      - model: str ("" if absent)
      - body: str (everything after the closing `---`)
      - content: str (full file content)
      - selectable: bool (True if it has both name and description —
        i.e. it's a candidate for Task-tool subagent_type selection.
        False for direct-path agents like exec-interviewer.md that are
        invoked by file path and have no frontmatter description at all.)
    """
    content = agent_path.read_text()
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{agent_path.name}: frontmatter가 없습니다 (여는 --- 없음)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError(f"{agent_path.name}: frontmatter가 닫히지 않았습니다 (닫는 --- 없음)")

    frontmatter_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:]).lstrip("\n")

    fields = {"name": "", "description": "", "tools": "", "model": ""}
    other_keys = []
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key == "description" and value in (">", "|", ">-", "|-"):
            continuation: list[str] = []
            i += 1
            while i < len(frontmatter_lines) and (
                frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")
            ):
                continuation.append(frontmatter_lines[i].strip())
                i += 1
            fields["description"] = " ".join(continuation)
            continue

        value = value.strip('"').strip("'")
        if key in fields:
            fields[key] = value
        else:
            other_keys.append(key)
        i += 1

    name = fields["name"] or agent_path.stem
    selectable = bool(fields["name"] and fields["description"])

    return {
        "name": name,
        "description": fields["description"],
        "tools": fields["tools"],
        "model": fields["model"],
        "other_keys": other_keys,
        "body": body,
        "content": content,
        "selectable": selectable,
        "path": str(agent_path),
    }


def list_repo_agents(agents_dir: Path | None = None, exclude_name: str | None = None) -> list[dict]:
    """Parse every agents/*.md in the repo's real agents/ directory.

    Skips files that fail to parse (reports to caller via the `error` key
    instead of raising, so one malformed file doesn't block the others).
    """
    agents_dir = agents_dir or REPO_AGENTS_DIR
    results = []
    for path in sorted(agents_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        try:
            parsed = parse_agent_md(path)
        except ValueError as e:
            results.append({"path": str(path), "error": str(e)})
            continue
        if exclude_name and parsed["name"] == exclude_name:
            continue
        results.append(parsed)
    return results
