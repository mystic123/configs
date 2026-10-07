#!/usr/bin/env python3
"""Apply selected Maccy preferences without replacing other host data."""

import argparse
from pathlib import Path
import plistlib
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
settings = plistlib.loads(Path(__file__).with_name("preferences.plist").read_bytes())
container = Path.home() / "Library/Containers/org.p0deje.Maccy"
domain = str(container / "Data/Library/Preferences/org.p0deje.Maccy") if container.is_dir() else "org.p0deje.Maccy"
commands = []
for key, value in settings.items():
    if isinstance(value, bool):
        typed = ["-bool", "true" if value else "false"]
    elif isinstance(value, int):
        typed = ["-int", str(value)]
    elif isinstance(value, float):
        typed = ["-float", str(value)]
    elif isinstance(value, str):
        typed = ["-string", value]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        typed = ["-array", *value]
    else:
        raise TypeError(f"Unsupported preference type for {key}: {type(value).__name__}")
    commands.append(["defaults", "write", domain, key, *typed])
if args.dry_run:
    print(f"Would apply {len(commands)} selected settings to {domain}; no writes.")
else:
    if sys.platform != "darwin":
        raise SystemExit("Run this on macOS, after installing and quitting Maccy.")
    for command in commands:
        subprocess.run(command, check=True)
    print(f"Applied {len(commands)} settings. Start Maccy to load them.")
