#!/usr/bin/env python3
"""Install the selected agent files. Keep other host settings and auth in place."""

import argparse
import copy
import datetime
import json
import os
from pathlib import Path
import shlex
import shutil
import tempfile
import tomllib
import uuid

REPO = Path(__file__).resolve().parents[1]


def read_json(path):
    if not path.exists():
        if path.is_symlink():
            raise ValueError(f"Broken config link: {path}. Restore its target first.")
        return {}
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f"Cannot parse {path}: {error}. Fix the file and rerun --dry-run.") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def merge_settings(existing, selected, path=()):
    result = copy.deepcopy(existing)
    for key, value in selected.items():
        branch = path + (key,)
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_settings(result[key], value, branch)
        elif branch == ("permissions", "allow") and key in result:
            if not isinstance(result[key], list):
                raise ValueError("permissions.allow must be a list.")
            result[key] = list(dict.fromkeys(result[key] + value))
        else:
            result[key] = copy.deepcopy(value)
    return result


def runs_plannotator(group):
    for hook in group.get("hooks", []):
        if hook.get("type") == "command":
            command = shlex.split(hook.get("command", ""))
            if command and Path(command[0]).name == "plannotator":
                return True
    return False


def merge_hooks(existing, selected, other=None):
    result = copy.deepcopy(existing)
    for event, groups in selected.items():
        present = result.setdefault(event, [])
        if not isinstance(present, list):
            raise ValueError(f"hooks.{event} must be a list.")
        other_groups = [] if other is None else other.get(event, [])
        for group in groups:
            candidates = present + other_groups
            if group in candidates:
                continue
            if any(runs_plannotator(g) and g.get("matcher") == group.get("matcher")
                   for g in candidates):
                continue
            present.append(copy.deepcopy(group))
    return result


def toml_value(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(json.dumps(k) + " = " + toml_value(v)
                                  for k, v in value.items()) + " }"
    raise TypeError(f"Unsupported TOML value: {type(value).__name__}")


def write_toml(value):
    text = "\n".join(json.dumps(k) + " = " + toml_value(v)
                     for k, v in value.items()) + "\n"
    if tomllib.loads(text) != value:
        raise ValueError("TOML merge changed a value. No files have been installed.")
    return text


def managed_block(existing, body):
    start = "# BEGIN agent-env"
    end = "# END agent-env"
    block = start + "\n" + body.rstrip() + "\n" + end + "\n"
    if start in existing or end in existing:
        if existing.count(start) != 1 or existing.count(end) != 1:
            raise ValueError("Invalid agent-env block. Repair its markers before installing.")
        first = existing.index(start)
        last = existing.index(end, first) + len(end)
        if last < len(existing) and existing[last] == "\n":
            last += 1
        return existing[:first] + block + existing[last:]
    gap = "\n" if existing and not existing.endswith("\n") else ""
    return existing + gap + block


def text_at(path):
    if path.is_symlink() and not path.exists():
        raise ValueError(f"Broken config link: {path}. Restore its target first.")
    return path.read_text() if path.exists() else ""


def read_toml(path):
    try:
        return tomllib.loads(text_at(path))
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Cannot parse {path}: {error}. Fix the file and rerun --dry-run.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    parser.add_argument("--home", type=Path, help="Target home; useful for an isolated trial")
    parser.add_argument("--codex-home", type=Path, help="Override the host's CODEX_HOME")
    parser.add_argument("--shell", choices=["both", "bash", "zsh", "none"], default="both")
    args = parser.parse_args()
    home = (Path.home() if args.home is None else args.home.expanduser()).resolve()
    if args.codex_home is not None:
        codex_home = args.codex_home.expanduser().resolve()
    elif args.home is None and "CODEX_HOME" in os.environ:
        if not os.environ["CODEX_HOME"]:
            parser.error("CODEX_HOME is empty; unset it or give --codex-home.")
        codex_home = Path(os.environ["CODEX_HOME"]).expanduser().resolve()
    else:
        codex_home = home / ".codex"

    manifest = read_json(REPO / "manifest.json")
    operations = []

    def link(source, target):
        if not source.exists():
            raise ValueError(f"Missing package file: {source}.")
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        operations.append(("link", target, source))

    def content(target, text):
        if target.exists() and target.read_text() == text:
            return
        operations.append(("write", target, text))

    def json_content(target, value):
        # Keep an existing file's format when its values match.
        if target.exists() and read_json(target) == value:
            return
        content(target, json.dumps(value, indent=2, ensure_ascii=False) + "\n")

    for name in manifest["skills"]:
        if not name or Path(name).name != name:
            raise ValueError(f"Invalid skill folder name: {name!r}.")
        source = REPO / "skills" / name
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"Missing skill entry point: {source / 'SKILL.md'}.")
        link(source, home / ".agents/skills" / name)
        link(source, home / ".claude/skills" / name)
    for target in [home / ".claude/CLAUDE.md", codex_home / "AGENTS.md"]:
        link(REPO / "instructions/AGENTS.md", target)
    link(REPO / "claude/agents/pawel-writer.md", home / ".claude/agents/pawel-writer.md")

    target = home / ".claude/settings.json"
    existing = read_json(target)
    selected = read_json(REPO / "claude/settings.json")
    selected_hooks = selected.pop("hooks")
    claude = merge_settings(existing, selected)
    # An enabled Plannotator plugin already supplies the plan hook.
    plugins = claude.get("enabledPlugins", {})
    if not plugins.get("plannotator@plannotator", False):
        claude["hooks"] = merge_hooks(claude.get("hooks", {}), selected_hooks)
    json_content(target, claude)

    config_path = codex_home / "config.toml"
    original_config = read_toml(config_path)
    selected_config = read_toml(REPO / "codex/config.toml")
    codex = merge_settings(original_config, selected_config)
    hook_path = codex_home / "hooks.json"
    existing_hooks = read_json(hook_path)
    hook_groups = existing_hooks.get("hooks", {})
    selected_hooks = read_json(REPO / "codex/hooks.json")["hooks"]
    if "hooks" in codex:
        codex["hooks"] = merge_hooks(codex["hooks"], selected_hooks, hook_groups)
    else:
        existing_hooks["hooks"] = merge_hooks(hook_groups, selected_hooks)
        json_content(hook_path, existing_hooks)
    if codex != original_config:
        content(config_path, write_toml(codex))

    rule_path = codex_home / "rules/default.rules"
    rules = text_at(rule_path)
    for rule in (REPO / "codex/rules/default.rules").read_text().splitlines():
        if rule not in rules.splitlines():
            rules += ("\n" if rules and not rules.endswith("\n") else "") + rule + "\n"
    content(rule_path, rules)
    target = home / ".plannotator/config.json"
    json_content(target, merge_settings(read_json(target), read_json(REPO / "plannotator/config.json")))

    link(REPO / "shell/gitconfig", home / ".config/agent-env/gitconfig")
    link(REPO / "shell/shell.sh", home / ".config/agent-env/shell.sh")
    target = home / ".gitconfig"
    include = "[include]\n\tpath = " + json.dumps(str(home / ".config/agent-env/gitconfig"))
    content(target, managed_block(text_at(target), include))
    shells = ["bash", "zsh"] if args.shell == "both" else [args.shell]
    for shell in shells:
        if shell != "none":
            target = home / (".bashrc" if shell == "bash" else ".zshrc")
            content(target, managed_block(text_at(target), '. "$HOME/.config/agent-env/shell.sh"'))

    if not operations:
        print("No changes needed.")
        return
    if args.dry_run:
        for kind, target, _ in operations:
            print(f"{kind}: {target}")
        print(f"Dry run: {len(operations)} changes; no files written.")
        return

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = home / ".local/state/agent-env/backups" / (stamp + "-" + uuid.uuid4().hex[:8])
    backup.mkdir(parents=True, mode=0o700)
    backup.chmod(0o700)
    changes = []
    for index, (kind, target, value) in enumerate(operations):
        saved = backup / f"{index:03d}"
        existed = target.exists() or target.is_symlink()
        if existed:
            if target.is_dir() and not target.is_symlink():
                shutil.copytree(target, saved, symlinks=True)
            else:
                shutil.copy2(target, saved, follow_symlinks=False)
        changes.append({"path": str(target), "backup": saved.name if existed else None})
        (backup / "changes.json").write_text(json.dumps(changes, indent=2) + "\n")
        target.parent.mkdir(parents=True, exist_ok=True)
        if kind == "link":
            if target.is_dir() and not target.is_symlink():
                # Move the old folder into the backup; its files remain intact.
                shutil.rmtree(saved)
                os.replace(target, saved)
            temporary = target.with_name(target.name + ".agent-env-" + uuid.uuid4().hex[:8])
            temporary.symlink_to(value, target_is_directory=value.is_dir())
            os.replace(temporary, target)
        else:
            with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(value)
            temporary.chmod(0o600)
            os.replace(temporary, target)
    print(f"Installed {len(manifest['skills'])} skills and settings ({len(operations)} changes).")
    print(f"Host-local backup: {backup}")
    print("Open a new shell. In Codex, use /hooks to review and trust the Plannotator hook.")


if __name__ == "__main__":
    main()
