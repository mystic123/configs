#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
    exec python3 "$repo_dir/scripts/install.py" "$@"
  fi
fi
if command -v uv >/dev/null 2>&1; then
  exec uv run --no-project --python 3.12 python "$repo_dir/scripts/install.py" "$@"
fi
echo 'Install Python 3.11+ or uv, then run install.sh again.' >&2
exit 1
