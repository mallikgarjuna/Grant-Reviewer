import subprocess
import pytest
import os

def run_hook(args):
    """Run the hook script via subprocess and return result."""
    # Find project root relative to this test file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(test_dir, "..", ".."))
    script_path = os.path.join(project_root, "scripts", "hooks", "check_agents_md.py")
    return subprocess.run(["python3", script_path] + args, capture_output=True, text=True)

@pytest.fixture
def temp_agents_file(tmp_path):
    def _create(lines, trailing_newline=True):
        f = tmp_path / "AGENTS.md"
        content = "\n".join(["line"] * lines)
        if trailing_newline and lines > 0:
            content += "\n"
        f.write_text(content)
        return str(f)
    return _create

def test_check_agents_md_valid_under_limit(temp_agents_file):
    f = temp_agents_file(40)
    result = run_hook([f])
    assert result.returncode == 0

def test_check_agents_md_valid_exact_limit(temp_agents_file):
    # 45 lines + 1 trailing newline
    f = temp_agents_file(45, trailing_newline=True)
    result = run_hook([f])
    assert result.returncode == 0

def test_check_agents_md_invalid_over_limit(temp_agents_file):
    f = temp_agents_file(46)
    result = run_hook([f])
    assert result.returncode == 1
    assert "exceeds" in result.stderr.lower()

def test_check_agents_md_invalid_no_file():
    result = run_hook(["non_existent_file.md"])
    assert result.returncode == 1
