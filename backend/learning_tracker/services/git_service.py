"""
Git 提交记录读取服务
"""

import subprocess
import re
from datetime import date
from typing import Optional
from backend.learning_tracker.core.config import tracker_settings


class GitService:
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or tracker_settings.GIT_PROJECT_PATH

    def _run(self, cmd: list[str]) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Git error: {e}"

    def get_commits(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        fmt = "%H||%s||%an||%ai"
        cmd = ["git", "log", f"--pretty=format:{fmt}", f"-n={limit}"]
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")
        output = self._run(cmd)
        if not output or "Git error" in output:
            return []
        commits = []
        for line in output.split("\n"):
            if not line.strip():
                continue
            parts = line.split("||")
            if len(parts) < 4:
                continue
            commit_hash, message, author, date_str = parts[0], parts[1], parts[2], parts[3]
            if keyword and keyword.lower() not in message.lower():
                continue
            commits.append({
                "hash": commit_hash[:8],
                "message": message,
                "author": author,
                "date": date_str[:10],
            })
        return commits

    def get_commits_by_date(self, target_date: str) -> list[dict]:
        return self.get_commits(since=target_date, until=target_date)

    def get_today_commits(self) -> list[dict]:
        return self.get_commits_by_date(date.today().isoformat())

    def get_weekly_stats(self) -> dict:
        import datetime
        today = date.today()
        week_ago = today - datetime.timedelta(days=7)
        commits = self.get_commits(since=week_ago.isoformat(), limit=100)
        return {"total_commits": len(commits), "commits": commits}
