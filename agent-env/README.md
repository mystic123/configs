# Agent environment for SSH

Personal, generic Claude Code and Codex setup. This repo contains instructions,
35 skills, CLI preferences, Plannotator settings, and a small shell/Git setup.
It assumes that the remote host has no browser automation.

The repo contains no credentials, keys, auth caches, browser profiles, service
connections, project settings, trusted-project lists, conversation history,
memories, or machine-specific paths. Sign in on each host after installation.

## Install the tools on the remote host

Use native builds for that host. Install Git, GitHub CLI (`gh`), `rg`, `jq`,
Node.js, and Python 3.11+ through the host's package manager. `uv` can supply
Python if the system Python is older. `tmux` is optional, but useful for sessions
that need to survive an SSH disconnect.

Install the agents and the Plannotator binary:

```sh
curl -fsSL https://claude.ai/install.sh | bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
curl -fsSL https://plannotator.ai/install.sh | bash -s -- --minimal
```

Use Plannotator's `--minimal` install: this repo supplies the skills and hooks.
There is no need to install its Claude plugin as well.

Install `uv` if needed:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new shell so installed tools appear on `PATH`. Check the core tools:

```sh
claude --version
codex --version
plannotator review --help
gh --version
```

Use current Claude and Codex releases: these settings include recent effort,
UI, and hook options. Install project languages and build tools when a project
needs them; this repo does not install a project's dependencies.

Sources: [Claude setup](https://code.claude.com/docs/en/setup),
[Codex CLI](https://learn.chatgpt.com/docs/cli),
[Plannotator install](https://github.com/backnotprop/plannotator#install),
[uv install](https://docs.astral.sh/uv/getting-started/installation/).

## Install this setup

Keep the configs checkout at its installed path: instruction and skill links
point to its `agent-env/` folder.

```sh
git clone https://github.com/mystic123/configs.git "$HOME/src/configs"
cd "$HOME/src/configs/agent-env"
./install.sh --dry-run
./install.sh
```

The installer needs Python 3.11+ or `uv`. It uses only the Python standard
library. If it uses `uv`, `uv` supplies Python 3.12.

By default it adds one source block to both `~/.bashrc` and `~/.zshrc`. Choose
`--shell bash`, `--shell zsh`, or `--shell none` to change that. For a trial in
an empty directory, use `./install.sh --home /tmp/agent-env-trial`.

The installer:

- Links the 35 canonical skill folders into `~/.agents/skills` for Codex and
  `~/.claude/skills` for Claude. It leaves other skill names in place.
- Links one shared prompt to `~/.claude/CLAUDE.md` and the Codex home `AGENTS.md`.
- Adds the Claude writing agent.
- Merges selected settings into the host's existing config. Other keys remain
  in place, including host-local service settings. Existing Claude allow rules
  remain; the selected generic rules are added once.
- Adds Plannotator plan hooks. An existing direct Plannotator hook is reused.
  For Claude, an enabled `plannotator@plannotator` plugin supplies the plan hook,
  so the installer does not add a second one.
- Adds the three generic Codex command rules once.
- Adds Git preferences through an include file, without setting a name, email,
  signing key, credential helper, or remote URL.
- Adds `~/.local/bin` to `PATH`. In an SSH session, it sets Plannotator remote
  mode and uses port `9999` unless you have set another port.

`CODEX_HOME` and `--codex-home` are supported for Codex config, hooks, rules and
instructions. Skills use the documented user location, `~/.agents/skills`.
The installer does not copy legacy `~/.codex/skills` directories.

When TOML values change, the installer writes valid TOML with a normalised
format; comments and layout stay in the host-local backup. JSON formatting can
also change. A second install makes no changes when the setup already matches.

Before each replacement, the installer saves the old file, directory, or link
under `~/.local/state/agent-env/backups/<run>/`. That directory has mode `0700`.
`changes.json` maps each changed path to its backup; a null backup marks a new
path. Backups stay on that host and must not enter this repo or a transfer.

Open a new shell after installation.

## Sign in on the remote host

Start Claude and follow its sign-in flow. Open the printed sign-in link in your
local browser when the remote host cannot open one:

```sh
claude
```

For Codex, use device code login:

```sh
codex login --device-auth
```

Enable device code login in your ChatGPT security settings or workspace
permissions if needed. Open the link on your local machine and enter the code.

If device code login is unavailable, use a forwarded callback instead. Start a
local SSH connection with port `1455` forwarded, then run `codex login` on the
remote host and open its printed URL in your local browser:

```sh
# Local machine
ssh -L 1455:localhost:1455 user@host

# Remote host
codex login
```

Sign in to GitHub separately, then install the stack extension:

```sh
gh auth login
gh extension install github/gh-stack
```

These flows create new authentication on the host. This setup never copies
`auth.json`, Claude credentials, SSH keys, keychains, or browser cookies.

Source: [Codex headless authentication](https://learn.chatgpt.com/docs/auth).

## Use Plannotator over SSH

Forward the review port from your local machine:

```sh
ssh -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:9999:127.0.0.1:9999 user@host
```

The installed shell file sets these values for SSH sessions. For a shell that
has not loaded it, set them on the remote host:

```sh
export PLANNOTATOR_REMOTE=1
export PLANNOTATOR_PORT=9999
```

Start Claude or Codex inside that session. Plannotator serves the review on the
remote host. Open its printed `localhost:9999` URL in your **local** browser.
The remote host needs no Chrome installation, browser profile, extension, or
Playwright MCP server.

For a saved SSH alias, add only a port-forward line to that alias on your local
machine:

```sshconfig
Host devbox
    LocalForward 127.0.0.1:9999 127.0.0.1:9999
    ExitOnForwardFailure yes
```

Keep the host name, user and SSH authentication in your own local SSH config.
This repo does not transfer that config. If you choose another review port,
change both the forwarding rule and `PLANNOTATOR_PORT`. Use one active review
at a time on a given port.

On the first Codex launch, run `/hooks`, inspect the Plannotator hook, and trust
it. Codex requires review of new or changed user hooks. This repo does not copy
hook trust records or bypass that review.

Claude uses `/plannotator-last`, `/plannotator-annotate`, and
`/plannotator-review`; Codex uses the corresponding `$plannotator-*` skills.
Native plan review uses the installed hooks. The last-message skill runs its
command before any status message, so the review targets the prior answer.

HTML explanations also work through the local review browser.
`visual-explainer` is bundled because the general visual path in
`plannotator-visual-explainer` requires it. Its optional MCP server and browser
runtime are not installed. Browser automation, screenshots and video rendering
are outside this remote profile.

Sources: [Plannotator SSH setup](https://github.com/backnotprop/plannotator#remote--ssh--devcontainer),
[Codex hook review](https://learn.chatgpt.com/docs/hooks),
[Codex skill discovery](https://learn.chatgpt.com/docs/build-skills).

## Contents and changes from the source machine

See [manifest.json](manifest.json) for the exact skill list and source records.

The shared prompt omits the company-specific section and the old Windows process command.
It keeps P's general work protocol, communication preferences, Git rules and
verification requirements. The prompt also states the remote host's lack of a
browser and the local Plannotator review flow.

Claude uses Opus, thinking, high effort, fullscreen UI, agent teams and empty
commit/PR attribution. Its 17 selected allow rules omit Coral, Lagoon, the old
Mac browser script, and the duplicate grep rule. No kubectl approvals are in
the package.

Codex uses `gpt-6-astra`, `xhigh` reasoning, `on-request` approval,
`workspace-write`, pragmatic personality and P's status line. It keeps fresh
memory support and hooks enabled, with Chronicle and JS REPL disabled. It
omits project trust, service connections, desktop paths and sleep prevention.
No existing memory data is included.

The six Plannotator skills use one common set of instructions. The three
launchers use plain commands, retain Claude's allowed-tool declaration, and
preserve Codex's explicit-invocation metadata. Approval with notes stays
guidance, and review command arguments pass through.

Git preferences include default branch `main`, automatic push upstream setup,
merge-based pulls, the existing rebase instruction format and `hs` log alias.
Git identity and authentication remain host-local.

## Updates and checks

```sh
git pull --ff-only
./install.sh --dry-run
./install.sh
```

Linked instructions and skills update with the checkout. Rerun the installer
to merge changes to copied settings. Restart agent sessions after updates.

Run the installer checks from this checkout:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check.py
```

The checks use temporary home directories and synthetic host-local data. They
do not use your real credentials, start an agent session, or connect to a host.
Remote login and a real SSH review remain host setup checks.

Third-party skills keep their source records and licences in
[THIRD_PARTY.md](THIRD_PARTY.md) and `licenses/`.
