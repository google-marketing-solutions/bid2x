# Pull request guide

This project improves incrementally so reviews stay small and low-risk.

## Scope

- Prefer **one primary file** per pull request.
- Two small, closely related files (for example `bid2x_model.py` and
  `bid2x_gtm_model.py`) are acceptable when the change is clearly paired.
- Keep each pull request focused on a single theme: lint cleanup, tests,
  logging, or a behavior change — not several at once.

## Labels and descriptions

Use the pull request description to state:

1. **Theme** — for example "no behavior change", "bug fix", or "new feature".
2. **Files touched** — list the primary module(s).
3. **Test plan** — how you verified the change.

For tech-debt work, call out explicitly when behavior should be unchanged.

## Local checks before opening a PR

From the repository root:

```bash
pip install -e ".[dev]"
python -m compileall -q bid2x
python -m ruff check bid2x
python -m pytest
```

CI runs the same checks on every pull request.

## Suggested improvement order

Work through modules from small leaf files toward orchestration code:

1. `bid2x_var.py`, `bid2x_platform.py`, `bid2x_env.py`
2. `bid2x_util.py`, model modules, `auth/bid2x_auth.py`
3. `bid2x_args.py`, `bid2x_application.py`, `main.py`
4. `bid2x_gtm.py`, `bid2x_dv.py`, `bid2x_spreadsheet.py`
5. `budget2x/budget2x.js`

Track larger efforts in GitHub issues and link each pull request to the issue
it addresses. See [TECH_DEBT.md](TECH_DEBT.md) for the file-by-file backlog.
