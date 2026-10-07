#!/usr/bin/env python3
"""Check the selected package for missing files, host state and secret patterns."""

import json
from pathlib import Path
import re
import tomllib

repo = Path(__file__).resolve().parents[1]
manifest = json.loads((repo / "manifest.json").read_text())
names = manifest["skills"]
assert len(names) == len(set(names)) == 35, "Expected 35 distinct selected skills."
assert set(names) == {p.name for p in (repo / "skills").iterdir() if p.is_dir()}
for name in names:
    text = (repo / "skills" / name / "SKILL.md").read_text()
    assert text.startswith("---\n"), f"Missing frontmatter: {name}"
    assert re.search(r"^name: " + re.escape(name) + r"\s*$", text, re.M), name

claude = json.loads((repo / "claude/settings.json").read_text())
allowed_claude = {"model", "alwaysThinkingEnabled", "effortLevel", "modelSettings",
                  "attribution", "tui", "skipDangerousModePermissionPrompt",
                  "skipAutoPermissionPrompt", "env", "permissions", "hooks"}
assert set(claude) <= allowed_claude, "Unselected Claude settings found."
assert set(claude["env"]) == {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"}
assert all("kubectl" not in rule and "mcp__" not in rule for rule in claude["permissions"]["allow"])
codex = tomllib.loads((repo / "codex/config.toml").read_text())
allowed_codex = {"model", "model_reasoning_effort", "plan_mode_reasoning_effort",
                 "approval_policy", "sandbox_mode", "service_tier", "personality",
                 "tool_output_token_limit", "features", "tui"}
assert set(codex) <= allowed_codex, "Unselected Codex settings found."
assert codex["features"]["chronicle"] is False
for relative in ["codex/hooks.json", "plannotator/config.json"]:
    json.loads((repo / relative).read_text())

forbidden_names = {"auth.json", ".credentials.json", "settings.local.json",
                   "id_rsa", "id_ed25519", "linear.env"}
patterns = {
    "source host path": r"/Users/|/opt/homebrew|/Applications/",
    "removed project state": r"withcoral|lagoon-local|Phoebe|nqscreen",
    "credential signature": r"(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----)",
}
checked = 0
errors = []
for path in repo.rglob("*"):
    relative = path.relative_to(repo)
    if ".git" in relative.parts or "__pycache__" in relative.parts:
        continue
    if path.is_symlink():
        errors.append(f"Package contains a symlink: {relative}")
        continue
    if not path.is_file():
        continue
    checked += 1
    if path.name in forbidden_names or path.name == ".env" or path.suffix in {".pem", ".key"}:
        errors.append(f"Excluded host file: {relative}")
    # This check's regex strings are rules, not transferred host data.
    if path == Path(__file__).resolve():
        continue
    text = path.read_text(errors="replace")
    for label, pattern in patterns.items():
        if re.search(pattern, text):
            errors.append(f"{label}: {relative}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {len(names)} skills; settings allowlists and {checked} package files checked.")
print("No excluded host files, source-host paths, project-state markers or known credential signatures found.")
