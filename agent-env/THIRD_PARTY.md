# Skill sources

The package contains local copies of the selected skills. `manifest.json`
records source paths and installed folder hashes where the source machine's
skill lock provided them. A folder hash is not an upstream commit ID.

| Files | Source | Licence file |
| --- | --- | --- |
| 25 engineering and productivity skill folders | [mattpocock/skills](https://github.com/mattpocock/skills) | `licenses/mattpocock-skills-MIT.txt` |
| Six `plannotator*` skill folders | [backnotprop/plannotator](https://github.com/backnotprop/plannotator) | `licenses/plannotator-APACHE.txt`, `licenses/plannotator-MIT.txt` |
| `gh-stack` | [github/gh-stack](https://github.com/github/gh-stack/tree/v0.0.8/skills/gh-stack) | `licenses/gh-stack-MIT.txt` |
| `visual-explainer` | [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer/tree/0cc6f15452c455a05fb7fceb036d0da31387c69c/plugins/visual-explainer) | `licenses/visual-explainer-MIT.txt` |

`visual-explainer` comes from commit
`0cc6f15452c455a05fb7fceb036d0da31387c69c`. It supplies the general visual path
used by `plannotator-visual-explainer`.

The common Plannotator launchers have local changes: plain command instructions
for both agents, Claude allowed-tool declarations, last-message ordering,
approval handling and review argument support. Their existing Codex invocation
policies remain in place.

`creating-skills`, `pawel-design-doc-writer`, the Claude writing agent and P's
shared prompt come from local personal configuration. The source lock has no
upstream record for those files.

The installer and shell setup are local additions for this transfer package.
