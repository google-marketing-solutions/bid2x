# Technical debt register

This document tracks known code-quality issues and planned incremental fixes
for the bid2x / budget2x repository. It supports the workflow in
[PR_GUIDE.md](PR_GUIDE.md): one focused pull request at a time, starting with
low-risk modules and moving toward orchestration code.

**How to use this doc**

- Open one GitHub issue (or PR) per row when you start work.
- Mark items done by linking the merged PR next to the entry.
- Prefer behavior-neutral cleanup before refactors that change runtime logic.

**Phase status**

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | CI, ruff, pytest, contributor docs | Done on branch `phase-1-ci-only` |
| 2 | Per-file cleanup (this register) | Done on branch `integrate/phase-2` |
| 3 | Cross-cutting refactors (logging, config object, deps) | In progress on `phase-3/config-object` |
| 4 | New features | Not started |

---

## Cross-cutting issues

These span multiple files and should be addressed gradually, not in one PR.

| Issue | Impact | Suggested approach |
|-------|--------|-------------------|
| **Module-level global state** | Hard to test; import order matters | Introduce a config object; stop mutating `bid2x_var` from args/env/main |
| **`global app` in `main.py`** | Side effects at import; Cloud Event vs CLI share state | Lazy-init app inside `main()` / entry handlers |
| **Import-time execution in `main.py`** | `process_command_line_args()` and `create_objects_from_json_file()` run on import | Move behind `if __name__ == '__main__'` or explicit bootstrap |
| **`print()` for operational output** | No log levels; noisy in Cloud Run | Replace with `logging` module file-by-file (~170 calls in `bid2x/`) |
| **No unit tests beyond smoke tests** | Regressions caught only manually or in prod | Add tests per module as each file is cleaned up |
| **Ruff import sorting (`I`) disabled** | Inconsistent import order | Enable per file during Phase 2 cleanup |
| **Legacy `oauth2client`** | Deprecated; duplicates `google-auth` | Migrate auth in dedicated PR after tests exist |
| **Pinned dependencies (2023 era)** | Security / compatibility drift | Upgrade in small PRs (`pip-audit`, one dependency family at a time) |
| **Placeholder defaults in `bid2x_var`** | Easy to run with invalid IDs/URLs by mistake | Document clearly; consider required-config validation |
| **`distutils.util.strtobool` in `bid2x_env.py`** | Removed from stdlib in Python 3.12+ | Replace with small local helper or `distutils` shim |

---

## `bid2x/` Python modules

Ordered by suggested cleanup sequence (small leaf files first).

### `bid2x_var.py` (~124 lines) — Priority: high / next

| Item | Severity | Notes |
|------|----------|-------|
| `TRACE` and `DEBUG` default to `True` | Medium | Verbose logging in production deployments |
| `JSON_AUTH_FILE` assigned twice (lines 53 and 85) | Low | Second assignment wins; confusing for readers |
| `SERVICE_ACCOUNT_EMAIL` assigned twice (lines 54 and 88) | Low | Different placeholder values |
| All configuration is mutable module globals | Medium | Args, env, JSON, and app all write here |
| Placeholder IDs and spreadsheet key | Low | Expected for samples; document or validate at startup |

**Suggested PR themes:** fix duplicate assignments; set safer debug defaults; add tests for enum values and bounds (extend existing smoke tests).

---

### `bid2x_platform.py` (~53 lines) — Priority: low

| Item | Severity | Notes |
|------|----------|-------|
| Copyright header says "Google Inc." | Low | Other modules use "Google LLC" |
| Abstract methods lack return type hints | Low | `__str__`, `process_script`, `top_level_copy` |
| `print_dataframe` uses `print()` | Low | Candidate for logging when this file is touched |

**Suggested PR themes:** docstrings and typing only (no behavior change).

---

### `bid2x_env.py` (~103 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Mutates `bid2x_var` globals | Medium | Same pattern as `bid2x_args.py` |
| Uses deprecated `distutils.util.strtobool` | Medium | Breaks on Python 3.12+ without shim |
| No tests for env parsing | Medium | Bool/int coercion errors possible at runtime |
| Inconsistent spacing in `os.getenv(...)` calls | Low | Style only |

**Suggested PR themes:** replace `strtobool`; add unit tests with `monkeypatch`; no change to env var names.

---

### `bid2x_util.py` (~170 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| `google_dv_call` uses `print()` on errors | Medium | Should use logging |
| Return type `dict[Any]` is imprecise | Low | API responses vary by endpoint |
| Comment: generic spreadsheet call routine "when we remove gspread" | Low | Future refactor marker |
| GCS config read exists but integration incomplete in `main.py` | Medium | Config-from-GCS path not fully wired |

**Suggested PR themes:** logging + typing; tests for retry / error classification helpers.

---

### `bid2x_model.py` (~225 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| DV360 API calls embedded in model class | Medium | Blurs data model vs API client responsibilities |
| Uses `print()` in error paths | Low | |
| Overlapping fields/patterns with `bid2x_gtm_model.py` | Low | Opportunity for shared base or protocol |

**Suggested PR themes:** typing and docstrings first; defer structural split to later PR.

---

### `bid2x_gtm_model.py` (~126 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Duplicated zone metadata pattern vs `bid2x_model.py` | Low | `update_row`, `test_row`, etc. |
| No validation of row/column indices | Low | README notes no internal overlap checking |

**Suggested PR themes:** pair with `bid2x_model.py` for consistent `__str__` / repr only.

---

### `auth/bid2x_auth.py` (~189 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Class docstring describes "dog" attributes (placeholder text) | Low | Copy-paste artifact |
| Depends on deprecated `oauth2client` | High | Should migrate to `google-auth` |
| Overlapping methods (`auth_dv` vs `auth_dv_service`, sheets variants) | Medium | Consolidate in dedicated PR |
| `_scopes` typed as `str` but used as list | Low | Typing inaccuracy |

**Suggested PR themes:** fix docstrings first; auth library migration as separate tested PR.

---

### `bid2x_args.py` (~260 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Writes directly into `bid2x_var` module globals | Medium | Complicates testing |
| Large single function `process_command_line_args()` | Low | Could return a namespace/dataclass later |
| Import order not ruff-isort clean | Low | Fix when touching file |

**Suggested PR themes:** no behavior change; optional return-value refactor in Phase 3.

---

### `bid2x_application.py` (~265 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Hub class with many responsibilities | Medium | Auth, platform, sheet, zones, config copy |
| `auth: None` type hint inaccurate | Low | Should be `Bid2xAuth` |
| `top_level_copy` / `assign_vars_to_objects` mirror globals | Medium | Part of global-state problem |
| Uses `print()` for failures | Low | |

**Suggested PR themes:** typing and init clarity; defer architectural split.

---

### `main.py` (~435 lines) — Priority: high (after leaf modules)

| Item | Severity | Notes |
|------|----------|-------|
| Module-level bootstrap (lines 505–509) | High | Parses args and builds `app` on every import |
| `global app` shared by CLI and Pub/Sub entry | High | |
| GCS / remote config not implemented for Pub/Sub path | Medium | Comment at lines 85–87 |
| Invalid platform returns bare `return` (line 385) | Medium | Should raise or sys.exit with clear error |
| Docstring typo: "Scipts" | Low | |
| Long procedural `main()` with duplicated DV/GTM branches | Medium | Hard to test in isolation |
| Return type docstring says bool; function returns `int` | Low | |

**Suggested PR themes:** split entry points in small steps; defer GCS config to feature PR.

---

### `bid2x_gtm.py` (~647 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Large script-generation logic in one module | Medium | Hard to unit test |
| Regex and string-built JavaScript | Medium | Needs golden-file tests |
| ~23 `print()` calls | Low | |
| Lookup-table logic complexity | Medium | README: tested for 2–3 variables only |

**Suggested PR themes:** golden tests for generated JS snippets; logging pass.

---

### `bid2x_dv.py` (~1007 lines) — Priority: medium

| Item | Severity | Notes |
|------|----------|-------|
| Largest module; multiple responsibilities | High | List/create/update algorithms and script gen |
| ~36 `print()` calls | Low | |
| Temp-file based script upload | Low | Documented pattern; works but awkward locally |
| Import order not ruff-isort clean | Low | |

**Suggested PR themes:** split by function cluster (list vs update vs generate), one PR per cluster.

---

### `bid2x_spreadsheet.py` (~914 lines) — Priority: high

| Item | Severity | Notes |
|------|----------|-------|
| Largest integration surface (gspread + Sheets API) | High | |
| ~75 `print()` calls | Medium | |
| Comment: "Fast-follow to add unit tests" for nested loops (line 235) | High | Known gap |
| No validation of `test_row` / `update_row` overlap | Medium | Documented in README |
| Google Sheets cell character limit | Medium | Work in progress on branch `bid2x_spreadsheet.py-update` (50k truncation) — separate PR |
| Tight coupling to `bid2x_var` column constants | Low | |

**Suggested PR themes:** unit tests for nested-loop script logic first; cell limit PR separate; logging later.

---

## Infrastructure and deployment

| Item | Location | Severity | Notes |
|------|----------|----------|-------|
| Docker image uses full `python:3.11` not `slim` | `bid2x/Dockerfile` | Low | Larger image than necessary |
| No Dependabot config visible at repo root | — | Medium | GitHub reports many dependency alerts |
| `requirements.txt` pins 2023 packages | `bid2x/requirements.txt` | Medium | Includes legacy `oauth2client`, old `urllib3` |
| `install.sh` is long and imperative | `bid2x/install.sh` | Low | Hard to test; Cloud Shell oriented |
| No CI for `budget2x.js` | — | Low | Ads Script environment differs from Python CI |

---

## `budget2x/`

### `budget2x.js` (~583 lines) — Priority: low (after bid2x Python cleanup)

| Item | Severity | Notes |
|------|----------|-------|
| `TODO: Replace with your copy of the control sheet` (line 79) | Low | Sample placeholder |
| No lint/test in CI | Low | Google Ads Scripts runtime differs from Node |
| Separate codebase from bid2x Python | Low | Coordinate doc updates only |

**Suggested PR themes:** JSDoc and structure; keep changes separate from bid2x Python PRs.

---

## Open branches (not merged)

| Branch | Contents | Action |
|--------|----------|--------|
| `phase-1-ci-foundation` | CI, pytest, ruff, PR guide | Merge first |
| `bid2x_spreadsheet.py-update` | Sheets 50k cell writeback limit + mixed commits | Split/rebase; remove any `__pycache__` before PR |

---

## Suggested issue / PR checklist

Copy this when opening Phase 2 work:

```
[ ] Branch from latest main
[ ] One primary file (or paired small models)
[ ] Theme labeled: no behavior change | bug fix | feature
[ ] python -m compileall -q bid2x
[ ] python -m ruff check bid2x
[ ] python -m pytest
[ ] Test plan described in PR
[ ] Update this doc with merged PR link
```

### Phase 2 queue (recommended order)

1. [ ] `bid2x_var.py` — duplicates, debug defaults, tests
2. [ ] `bid2x_platform.py` — docs and typing
3. [ ] `bid2x_env.py` — `strtobool` replacement, env tests
4. [ ] `bid2x_util.py` — logging, helper tests
5. [ ] `bid2x_model.py` + `bid2x_gtm_model.py` — alignment
6. [ ] `auth/bid2x_auth.py` — docstrings, then oauth migration
7. [ ] `bid2x_args.py` — import sort, minor cleanup
8. [ ] `bid2x_application.py` — typing and init
9. [ ] `main.py` — entry-point / import side effects
10. [ ] `bid2x_gtm.py` — golden tests, logging
11. [ ] `bid2x_dv.py` — split into focused PRs
12. [ ] `bid2x_spreadsheet.py` — nested-loop tests, writeback limit
13. [x] `budget2x/budget2x.js` — placeholder and structure

### Phase 3 queue (cross-cutting)

1. [ ] `bid2x_config.py` — typed config object; CLI returns config instead of only mutating globals
2. [ ] Remaining `print()` → `logging` (spreadsheet, main, model modules)
3. [ ] `bid2x_dv.py` — deduplicate `inspect.stack()` caller-context helper
4. [ ] `bid2x_spreadsheet.py` — shared gspread retry helper
5. [ ] `auth/bid2x_auth.py` — migrate off deprecated `oauth2client`
6. [ ] Dependency refresh — one family per PR (`pip-audit`)
7. [ ] `bid2x/Dockerfile` — slim base image verification
