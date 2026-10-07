# Source from bash or zsh. Values come from this host's own environment.
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac

if [ -n "${SSH_CONNECTION:-}" ] || [ -n "${SSH_TTY:-}" ]; then
  export PLANNOTATOR_REMOTE=1
  export PLANNOTATOR_PORT="${PLANNOTATOR_PORT:-9999}"
fi
