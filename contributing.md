# How to Contribute

We would love to accept your patches and contributions to this project.

## Before you begin

### Sign our Contributor License Agreement

Contributions to this project must be accompanied by a
[Contributor License Agreement](https://cla.developers.google.com/about) (CLA).
You (or your employer) retain the copyright to your contribution; this simply
gives us permission to use and redistribute your contributions as part of the
project.

If you or your current employer have already signed the Google CLA (even if it
was for a different project), you probably don't need to do it again.

Visit <https://cla.developers.google.com/> to see your current agreements or to
sign a new one.

### Review our Community Guidelines

This project follows [Google's Open Source Community
Guidelines](https://opensource.google/conduct/).

## Contribution process

### Code Reviews

All submissions, including submissions by project members, require review. We
use [GitHub pull requests](https://docs.github.com/articles/about-pull-requests)
for this purpose.

### Incremental changes

For code quality and refactoring work, prefer small, reviewable pull requests.
See [docs/PR_GUIDE.md](docs/PR_GUIDE.md) for scope, local checks, and the
suggested order of improvements. Track known issues in
[docs/TECH_DEBT.md](docs/TECH_DEBT.md).

### Local checks

Before opening a pull request that touches `bid2x/` Python code, run:

```bash
pip install -e ".[dev]"
python -m compileall -q bid2x
python -m ruff check bid2x
python -m pytest
```

These checks also run automatically in GitHub Actions CI.
