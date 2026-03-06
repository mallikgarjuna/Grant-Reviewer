from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

pytestmark = [pytest.mark.no_db]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _guard_script() -> Path:
    return _repo_root() / "scripts" / "check_docs_sanitization.sh"


def _run_guard(cwd: Path) -> subprocess.CompletedProcess[str]:
    return _run_guard_with_env(cwd)


def _run_guard_with_env(
    cwd: Path,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = None
    if env_overrides:
        env = {**subprocess.os.environ, **env_overrides}
    return subprocess.run(
        ["bash", str(_guard_script())],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_wf0058_docs_sanitization_guard_runs_from_repo_root() -> None:
    result = _run_guard(_repo_root())

    assert result.returncode == 0
    assert "[docs-sanitization] PASS" in result.stdout


def test_wf0058_docs_sanitization_guard_runs_from_backend_cwd() -> None:
    result = _run_guard(_repo_root() / "backend")

    assert result.returncode == 0
    assert "[docs-sanitization] PASS" in result.stdout


def test_wf0058_docs_sanitization_guard_fails_on_forbidden_term(tmp_path: Path) -> None:
    target = tmp_path / "target.md"
    target.write_text("This line mentions Codex.", encoding="utf-8")

    result = _run_guard_with_env(
        _repo_root(),
        env_overrides={"DOCS_SANITIZATION_TARGETS": str(target)},
    )

    assert result.returncode == 1
    assert "[docs-sanitization] FAILED" in result.stdout
