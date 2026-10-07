# Generic personal shell settings. Keep project and host settings elsewhere.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"
COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="yyyy-mm-dd"

if [[ -f "$ZSH/oh-my-zsh.sh" ]]; then
  ZSH_THEME="robbyrussell"
  if [[ -d "${ZSH_CUSTOM:-$ZSH/custom}/themes/powerlevel10k" ]]; then
    ZSH_THEME="powerlevel10k/powerlevel10k"
  fi
  plugins=()
  for agent_config_plugin in brew colored-man-pages fzf-zsh-plugin git git-extras git-flow zsh-autosuggestions zsh-syntax-highlighting; do
    if [[ -d "$ZSH/plugins/$agent_config_plugin" || -d "${ZSH_CUSTOM:-$ZSH/custom}/plugins/$agent_config_plugin" ]]; then
      plugins+=("$agent_config_plugin")
    fi
  done
  unset agent_config_plugin
  source "$ZSH/oh-my-zsh.sh"
else
  autoload -Uz compinit
  compinit
fi

HISTSIZE=10000000
SAVEHIST=10000000
HISTORY_IGNORE="(ls|cd|pwd|exit|cd)*"
setopt EXTENDED_HISTORY INC_APPEND_HISTORY SHARE_HISTORY
setopt HIST_IGNORE_DUPS HIST_IGNORE_ALL_DUPS HIST_SAVE_NO_DUPS HIST_REDUCE_BLANKS

[[ -f "$HOME/.p10k.zsh" ]] && source "$HOME/.p10k.zsh"
[[ -f "$HOME/.fzf.zsh" ]] && source "$HOME/.fzf.zsh"
[[ -d "$HOME/.docker/completions" ]] && fpath=("$HOME/.docker/completions" $fpath)

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

export NVM_DIR="$HOME/.nvm"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  source "$NVM_DIR/nvm.sh"
elif command -v brew >/dev/null 2>&1; then
  agent_config_brew_prefix="$(brew --prefix)"
  [[ -s "$agent_config_brew_prefix/opt/nvm/nvm.sh" ]] && source "$agent_config_brew_prefix/opt/nvm/nvm.sh"
  unset agent_config_brew_prefix
fi

export PYENV_ROOT="$HOME/.pyenv"
[[ -d "$PYENV_ROOT/bin" ]] && export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv >/dev/null 2>&1; then
  eval "$(pyenv init - zsh)"
fi
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

if command -v kubectl >/dev/null 2>&1; then
  alias k=kubectl
  source <(kubectl completion zsh)
  compdef _kubectl k
fi
alias cp='cp -i'
if command -v pygmentize >/dev/null 2>&1; then
  alias ccat='pygmentize -g'
fi

[[ -f "$HOME/.config/agent-env/shell.sh" ]] && source "$HOME/.config/agent-env/shell.sh"
