import subprocess
import pytest
import os

def run_hook(commit_msg_file):
    """Run the hook script via subprocess and return result."""
    # Find project root relative to this test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(test_dir, "..", ".."))
    script_path = os.path.join(project_root, "scripts", "hooks", "check_commit_msg.py")
    return subprocess.run(["python3", script_path, commit_msg_file], capture_output=True, text=True)

@pytest.fixture
def temp_commit_msg_file(tmp_path):
    def _create(content):
        f = tmp_path / "COMMIT_EDITMSG"
        f.write_text(content)
        return str(f)
    return _create

def test_check_commit_msg_valid_wf_prefix(temp_commit_msg_file):
    f = temp_commit_msg_file("WF-0047: git-hooks-rule-enforcement — Task 1 — Implement AGENTS.md line count hook")
    result = run_hook(f)
    assert result.returncode == 0

def test_check_commit_msg_valid_merge(temp_commit_msg_file):
    f = temp_commit_msg_file("Merge branch 'main' into wf/WF-0047")
    result = run_hook(f)
    assert result.returncode == 0

def test_check_commit_msg_valid_revert(temp_commit_msg_file):
    f = temp_commit_msg_file("Revert \"WF-0047: some change\"")
    result = run_hook(f)
    assert result.returncode == 0

def test_check_commit_msg_valid_maintenance_chore_prefix(temp_commit_msg_file):
    f = temp_commit_msg_file("chore: bound phase 3 execution and align workflow docs")
    result = run_hook(f)
    assert result.returncode == 0

def test_check_commit_msg_valid_maintenance_fix_prefix(temp_commit_msg_file):
    f = temp_commit_msg_file("fix: allow maintenance branch commit messages")
    result = run_hook(f)
    assert result.returncode == 0

def test_check_commit_msg_invalid_prefix(temp_commit_msg_file):
    f = temp_commit_msg_file("Fixed a bug")
    result = run_hook(f)
    assert result.returncode == 1
    assert "invalid commit message prefix" in result.stderr.lower()
    assert "format must be" in result.stderr.lower()

def test_check_commit_msg_invalid_wf_format(temp_commit_msg_file):
    f = temp_commit_msg_file("WF-47: missed a digit")
    result = run_hook(f)
    assert result.returncode == 1

def test_check_commit_msg_no_file():
    result = run_hook("non_existent_file.txt")
    assert result.returncode == 1
