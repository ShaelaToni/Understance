import os
import subprocess
from pathlib import Path

# Switch off every program a repository can configure for git to run.
SAFE_GIT = [
    "git",
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.pager=cat",
    "-c",
    "diff.external=",
    "--no-pager",
]


class GitHistory:
    """Read each file's last commit and date from git; only reads the log."""

    def command(self, file: str) -> list[str]:
        return [*SAFE_GIT, "log", "-1", "--no-textconv", "--format=%h|%cI", "--", file]

    def last_changes(self, base: Path, files) -> dict[str, tuple[str, str]]:
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
        found = {}
        for file in sorted(files):
            try:
                result = subprocess.run(
                    self.command(file),
                    cwd=base,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                    env=env,
                )
            except (OSError, subprocess.TimeoutExpired):
                continue
            output = result.stdout.strip()
            if result.returncode == 0 and "|" in output:
                commit, date = output.split("|", 1)
                found[file] = (commit, date)
        return found
