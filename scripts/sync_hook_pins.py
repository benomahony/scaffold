"""Sync pinned pre-commit hook revisions from the live config into the template.

Run after `prek update` has bumped `.pre-commit-config.yaml`; this copies the
new `rev:` values into the scaffold template so `sc upgrade` distributes them.
"""

import re
from pathlib import Path

_REPO_RE = re.compile(r"^\s*- repo:\s*(\S+)\s*$")
_REV_RE = re.compile(r"^(\s*rev:\s*)(\S+)(.*)$")

CONFIG = Path(".pre-commit-config.yaml")
TEMPLATE = Path("src/scaffold/templates/base/.pre-commit-config.yaml.j2")


def load_revs(text: str) -> dict[str, str]:
    assert text is not None, "Config text must not be None"
    assert len(text) > 0, "Config text must not be empty"

    revs: dict[str, str] = {}
    repo: str | None = None
    for line in text.splitlines():
        repo_match = _REPO_RE.match(line)
        if repo_match:
            repo = repo_match.group(1)
            continue
        rev_match = _REV_RE.match(line)
        if rev_match and repo is not None and repo != "local":
            revs[repo] = rev_match.group(2)
            repo = None
    return revs


def sync_template(text: str, revs: dict[str, str]) -> str:
    assert text is not None, "Template text must not be None"
    assert revs, "Must have at least one revision to sync"

    out: list[str] = []
    repo: str | None = None
    for line in text.splitlines(keepends=True):
        repo_match = _REPO_RE.match(line)
        if repo_match:
            repo = repo_match.group(1)
        rev_match = _REV_RE.match(line)
        if rev_match and repo in revs:
            line = f"{rev_match.group(1)}{revs[repo]}{rev_match.group(3)}\n"
            repo = None
        out.append(line)
    return "".join(out)


def main() -> None:
    assert CONFIG.exists(), f"{CONFIG} must exist"
    assert TEMPLATE.exists(), f"{TEMPLATE} must exist"

    revs = load_revs(CONFIG.read_text())
    TEMPLATE.write_text(sync_template(TEMPLATE.read_text(), revs))


if __name__ == "__main__":
    main()
