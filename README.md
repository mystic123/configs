# Personal configs

Generic personal settings. Credentials, keys, sign-in state and project settings
stay on each machine.

## Claude Code and Codex over SSH

The [agent-env setup](agent-env/README.md) contains shared instructions, 35 skills,
CLI settings, Plannotator hooks and a small shell/Git setup.

Install it on the remote host with:

```sh
git clone https://github.com/mystic123/configs.git "$HOME/src/configs"
cd "$HOME/src/configs/agent-env"
./install.sh --dry-run
./install.sh
```

See its README for tool installation, fresh sign-in, backups and SSH port
forwarding. Plannotator reviews open in the local browser; the remote host needs
no browser automation. The installer merges selected settings and leaves the
host's authentication in place.

## Shell and Mac settings

| File | Purpose |
| --- | --- |
| `zshrc` | Current generic shell preferences, optional Oh My Zsh and tool setup |
| `p10k.zsh` | Current Powerlevel10k prompt settings |
| `vimrc` | Vim settings; these still match the source machine |
| `ghostty/config` | Combined active Ghostty settings, including SSH integration and key bindings |
| `maccy/preferences.plist` | Selected Maccy UI, shortcut, search and storage-limit preferences |
| `maccy/apply.py` | Applies those Maccy preferences without replacing other host data |

The root shell files are optional personal settings. The SSH agent installer
uses its own small shell file and does not replace `~/.zshrc` with this version.
Keep machine-specific paths and project environment variables outside this repo.

Rectangle settings have been removed because the app is no longer used.
Window management now uses the source machine's native macOS features.
The old iTerm exports have also been removed; Ghostty is the current terminal.

The shell uses Powerlevel10k when its Oh My Zsh theme is installed, and uses
the saved `~/.p10k.zsh` settings when present. Otherwise it uses the installed
Oh My Zsh default theme, or plain zsh if Oh My Zsh is absent. Install selected
plugins and tools separately; their caches and runtime files are not included.

## Restore Ghostty on macOS

From this checkout:

```sh
mkdir -p "$HOME/Library/Application Support/com.mitchellh.ghostty"
cp ghostty/config "$HOME/Library/Application Support/com.mitchellh.ghostty/config"
```

Back up an existing config before replacing it. Reload Ghostty with
Command+Shift+comma. This combines the settings from the source machine's XDG
and macOS config files, which Ghostty loads in that order. The macOS file loads
last. No font, theme, environment variables, credentials or machine paths are
copied from app state. [Ghostty configuration](https://ghostty.org/docs/config)

## Restore Maccy on macOS

Install and launch Maccy once, then quit it. From this checkout:

```sh
python3 maccy/apply.py --dry-run
python3 maccy/apply.py
```

The script supports both sandboxed and non-sandboxed preference locations and
writes each selected key with `defaults`. It preserves the other preferences.
The plist contains 15 settings, including the popup, pin, delete and preview
shortcuts, fuzzy search, automatic paste, visible controls, window size/position,
enabled clipboard formats and the 500-item history limit. The limit is a
setting; no clipboard contents or pinned items are included.

Ghostty and Maccy are desktop settings. The SSH agent installer does not apply
them. [Maccy](https://github.com/p0deje/Maccy)
