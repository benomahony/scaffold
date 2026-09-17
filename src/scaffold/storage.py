from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class CommandResult(BaseModel):
    repo_path: str
    repo_name: str
    command: str
    timestamp: datetime
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str
    git_commit: str | None = None


class ResultStorage:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self.storage_dir = storage_dir or Path.home() / ".scaffold"
        self.status_file = self.storage_dir / "repo_status.jsonl"

        assert self.status_file.name == "repo_status.jsonl", "Status file must be the results log"
        assert self.status_file.parent == self.storage_dir, "Status file must live in storage dir"

    def save_result(self, result: CommandResult) -> None:
        assert result.repo_path, "Result must carry a repo path"
        assert result.command in ("pytest", "prek"), "Result command must be pytest or prek"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        with open(self.status_file, "a") as f:
            f.write(result.model_dump_json() + "\n")

    def load_results(
        self,
        command: str | None = None,
        repo_path: str | None = None,
        limit: int | None = None,
    ) -> list[CommandResult]:
        assert command in (None, "pytest", "prek"), "Command filter must be a known command"
        assert self.status_file.suffix == ".jsonl", "Results log must be a jsonl file"

        if not self.status_file.exists():
            return []

        results = []
        with open(self.status_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                result = CommandResult.model_validate_json(line)

                if command and result.command != command:
                    continue
                if repo_path and result.repo_path != repo_path:
                    continue

                results.append(result)

                if limit and len(results) >= limit:
                    break

        return results

    def get_latest_by_repo(self, command: str) -> dict[str, CommandResult]:
        assert command, "Command must not be empty"
        assert command in ("pytest", "prek"), "Command must be pytest or prek"

        results = self.load_results(command=command)

        latest: dict[str, CommandResult] = {}
        for result in results:
            repo = result.repo_path
            if repo not in latest or result.timestamp > latest[repo].timestamp:
                latest[repo] = result

        return latest
