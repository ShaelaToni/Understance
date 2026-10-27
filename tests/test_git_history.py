import subprocess

from understance.adapters.git_history import GitHistory


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_git_runs_with_repo_supplied_programs_switched_off():
    command = GitHistory().command("sample_app/api.py")
    assert command[:8] == [
        "git",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.pager=cat",
        "-c",
        "diff.external=",
        "--no-pager",
    ]
    assert "--no-textconv" in command
    assert command[-2:] == ["--", "sample_app/api.py"]


def test_reads_the_last_commit_and_date_of_each_file(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "first")
    found = GitHistory().last_changes(tmp_path, ["pkg/a.py", "pkg/missing.py"])
    assert list(found) == ["pkg/a.py"]
    commit, date = found["pkg/a.py"]
    assert len(commit) >= 7
    assert date[:2] == "20"


def test_a_folder_that_is_not_a_repository_gives_no_history(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    assert GitHistory().last_changes(tmp_path, ["a.py"]) == {}
