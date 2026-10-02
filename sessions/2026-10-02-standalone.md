# Standalone source inspection, 2026-10-02

[User report, 2026-10-02] `uvx pypatree@latest --flat` failed from both
`/Users/yberreby/code/CanViT` and `/Users/yberreby/code/CanViT/canvit-pytorch`
after the 0.5.0 publication. The user authorized merging and publishing the
release earlier in this session and requested a resumable checkpoint before
the laptop battery reaches 3%.

[Codex observation, 2026-10-02] The isolated uvx environment has no editable
metadata for CanViT. Version 0.5.0's discovery depends on that metadata, so
changing directories cannot repair the lookup. Earlier release checks installed
the inspected fixture into the tool's environment and missed this workflow.
PR https://github.com/yberreby/pypatree/pull/1 and tag v0.5.0 are already published;
do not repeat that release.

[Implementation, 2026-10-02] Branch `fix/standalone-inspection` prepares 0.6.0.
The CLI defaults to local source inspection through Griffe with inspection
disabled. Source discovery includes conventional layouts and monorepo
subprojects. The existing runtime backend is selected with `--runtime`.
Both backends share signature formatting and tree rendering. Source signatures
describe declarations; classes without a local or synthesized constructor use
an ellipsis. README.md is generated from README.md.in.

[Checks read by Codex, 2026-10-02] The uninstalled-monorepo regression first
failed against 0.5.0. Local `uv run just` subsequently exercised source/runtime
contracts, type checking, formatting, dogfooding, and README generation.
Built wheel and sdist installations ran on an uninstalled project, both with
their installed CLI and through uncached uvx. Source smoke runs inspected HTTPX,
Rich's console module, and Tyro without installing those projects. Earlier
candidate uvx runs emitted CanViT and its PyTorch subtree with no pypatree
diagnostics. Final built-artifact and published-package CanViT checks remain.

Checkout on the user's Mac:
`/Users/yberreby/.codex/worktrees/28d8/pypatree`.
Local evidence: that checkout's `outputs/standalone-2026-10-02/`.
Runtime/source tests are in `tests/test_cli.py` and `pypatree/source/test.py`.

## Resume the release

Read this record, CLAUDE.md, and the fresh Git diff before changing files.
Run these commands from `/Users/yberreby/.codex/worktrees/28d8/pypatree`:

```sh
pmset -g batt
git status --short
git fetch --all --prune
git log -5 --oneline
gh pr list --head fix/standalone-inspection --state all
gh run list --branch fix/standalone-inspection
```

Inspect actual workflow logs for the candidate SHA before merging. The reusable
checks cover Python 3.9–3.14 on Linux and 3.13 on macOS. When testing another
interpreter locally, use `UV_PYTHON=3.14 uv run just check`; setting only outer
`uv run --python` lets nested uv commands select .python-version again.

Before publication, exercise the built wheel directly:

```sh
cd /Users/yberreby/code/CanViT
uvx --no-cache --from /Users/yberreby/.codex/worktrees/28d8/pypatree/dist/pypatree-0.6.0-py3-none-any.whl pypatree --flat
cd /Users/yberreby/code/CanViT/canvit-pytorch
uvx --no-cache --from /Users/yberreby/.codex/worktrees/28d8/pypatree/dist/pypatree-0.6.0-py3-none-any.whl pypatree --flat
```

After the reviewed candidate passes, merge its PR, fetch origin/main, tag that
merge commit v0.6.0, and push the tag. The release workflow runs the checks,
builds distributions, and publishes through PyPI trusted publishing. Check
whether v0.6.0 already exists before tagging; a resumed session must not publish
twice. Read the actual publish log. Then run `uvx pypatree@latest --flat` from
both CanViT paths above and inspect stdout/stderr before reporting success.
Do not change either CanViT checkout or its environment to make inspection work.

Griffe compatibility findings: Python 3.9 resolves 1.14; newer interpreters can
resolve 2.x. `Class.keywords` exists in 2.x but not 1.14. Variadic parameters
carry synthetic defaults in Griffe, which must be omitted when converting to
inspect.Parameter. ExprName.iterate yields itself, so recursive expression
formatting must terminate at ExprName. The tests exercise those adapters.
