import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

REPO = Path(__file__).resolve().parents[1]
SENTINEL = "HOST_ONLY_SYNTHETIC_TEST_DATA"


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent-env-test-")
        self.addCleanup(self.temp.cleanup)
        self.home = (Path(self.temp.name) / "home").resolve()
        self.home.mkdir()

    def write(self, name, content):
        path = self.home / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def install(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(REPO / "scripts/install.py"), "--home", str(self.home), *args],
            capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def snapshot(self):
        result = {}
        for path in self.home.rglob("*"):
            name = str(path.relative_to(self.home))
            if path.is_symlink():
                result[name] = ("link", str(path.readlink()))
            elif path.is_file():
                result[name] = ("file", path.read_bytes(), path.stat().st_mode)
            elif path.is_dir():
                result[name] = ("directory", path.stat().st_mode)
        return result

    def seed_host(self):
        self.write(".claude/settings.json", json.dumps({
            "hostSetting": {"keep": True},
            "env": {"HOST_VALUE": SENTINEL},
            "permissions": {"allow": ["Bash(host-tool *)"], "deny": ["Bash(denied-tool *)"]},
            "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "host-hook"}]}]},
        }))
        self.write(".codex/config.toml", '''host_setting = "keep"
[mcp_servers.host_service]
url = "https://example.invalid/mcp"
[mcp_servers.host_service.http_headers]
Authorization = "HOST_ONLY_SYNTHETIC_TEST_DATA"
[projects."/srv/example"]
trust_level = "trusted"
''')
        self.write(".codex/hooks.json", json.dumps({
            "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "host-hook"}]}]},
        }))
        self.write(".gitconfig", '[user]\n\tname = Host User\n\temail = host@example.invalid\n')
        self.write(".bashrc", "export HOST_SHELL_VALUE=keep\n")
        self.write(".agents/skills/host-skill/SKILL.md", "Host skill stays in place.\n")
        self.write(".claude/skills/gh-stack/SKILL.md", "Old selected skill.\n")
        self.write(".claude/skills/gh-stack/helper.txt", "Old helper stays in backup.\n")
        protected = [".codex/auth.json", ".claude/.credentials.json", ".ssh/id_ed25519",
                     ".codex/history.jsonl", ".claude/settings.local.json"]
        return {name: self.write(name, SENTINEL).read_bytes() for name in protected}

    def test_dry_run_writes_nothing(self):
        self.seed_host()
        before = self.snapshot()
        result = self.install("--dry-run")
        self.assertIn("no files written", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_second_install_makes_no_changes(self):
        self.seed_host()
        self.install()
        before = self.snapshot()
        result = self.install()
        self.assertIn("No changes needed", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_existing_plugin_and_inline_hook_are_reused(self):
        self.seed_host()
        claude_path = self.home / ".claude/settings.json"
        claude = json.loads(claude_path.read_text())
        claude["enabledPlugins"] = {"plannotator@plannotator": True}
        claude_path.write_text(json.dumps(claude))
        codex_path = self.home / ".codex/config.toml"
        codex_path.write_text(codex_path.read_text() + '''
[[hooks.Stop]]
[[hooks.Stop.hooks]]
type = "command"
command = "/usr/local/bin/plannotator"
timeout = 345600
''')
        self.install()
        claude = json.loads(claude_path.read_text())
        self.assertNotIn("PermissionRequest", claude["hooks"])
        codex = tomllib.loads(codex_path.read_text())
        self.assertEqual(len(codex["hooks"]["Stop"]), 1)
        hooks = json.loads((self.home / ".codex/hooks.json").read_text())
        self.assertNotIn("Stop", hooks["hooks"])
        self.assertIn("SessionStart", hooks["hooks"])

    def test_bad_config_fails_before_any_writes(self):
        self.seed_host()
        self.write(".codex/config.toml", "not valid = [\n")
        before = self.snapshot()
        result = self.install(success=False)
        self.assertIn("TOMLDecodeError", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_merge_preserves_host_state_and_auth(self):
        protected = self.seed_host()
        self.install()
        for name, original in protected.items():
            self.assertEqual((self.home / name).read_bytes(), original, name)
        claude = json.loads((self.home / ".claude/settings.json").read_text())
        self.assertEqual(claude["env"]["HOST_VALUE"], SENTINEL)
        self.assertTrue(claude["hostSetting"]["keep"])
        self.assertIn("Bash(host-tool *)", claude["permissions"]["allow"])
        self.assertEqual(claude["permissions"]["deny"], ["Bash(denied-tool *)"])
        self.assertIn("SessionStart", claude["hooks"])
        codex = tomllib.loads((self.home / ".codex/config.toml").read_text())
        self.assertEqual(codex["mcp_servers"]["host_service"]["http_headers"]["Authorization"], SENTINEL)
        self.assertEqual(codex["projects"]["/srv/example"]["trust_level"], "trusted")
        self.assertEqual(codex["host_setting"], "keep")
        self.assertEqual(codex["model"], "gpt-6-astra")
        skills = json.loads((REPO / "manifest.json").read_text())["skills"]
        for name in skills:
            source = REPO / "skills" / name / "SKILL.md"
            for root in [".agents/skills", ".claude/skills"]:
                self.assertTrue(source.samefile(self.home / root / name / "SKILL.md"))
        self.assertTrue((self.home / ".agents/skills/host-skill/SKILL.md").is_file())
        backups = list((self.home / ".local/state/agent-env/backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o700)
        changes = json.loads((backups[0] / "changes.json").read_text())
        old = next(c for c in changes if c["path"] == str(self.home / ".claude/skills/gh-stack"))
        self.assertEqual((backups[0] / old["backup"] / "helper.txt").read_text(), "Old helper stays in backup.\n")
        git_email = subprocess.check_output(
            ["git", "config", "--file", str(self.home / ".gitconfig"), "--get", "user.email"], text=True,
        )
        self.assertEqual(git_email.strip(), "host@example.invalid")
        git_branch = subprocess.check_output(
            ["git", "config", "--includes", "--file", str(self.home / ".gitconfig"), "--get", "init.defaultBranch"],
            text=True,
        )
        self.assertEqual(git_branch.strip(), "main")


if __name__ == "__main__":
    unittest.main()
