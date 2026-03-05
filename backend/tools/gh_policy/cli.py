from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tools.gh_policy.apply import run_apply
from tools.gh_policy.policy_schema import load_expected_policy
from tools.gh_policy.rollback import run_rollback
from tools.gh_policy.verify import run_verify

WF0056_EVIDENCE_ROOT = "../docs/walkthroughs/evidence/WF-0056"
WF0056_VERIFY_EVIDENCE_PATH = f"{WF0056_EVIDENCE_ROOT}/tracer_verify_evidence.json"
WF0056_APPLY_EVIDENCE_PATH = f"{WF0056_EVIDENCE_ROOT}/apply_evidence.json"
WF0056_ROLLBACK_EVIDENCE_PATH = f"{WF0056_EVIDENCE_ROOT}/rollback_evidence.json"
WF0056_SNAPSHOT_DIR = f"{WF0056_EVIDENCE_ROOT}/snapshots"
MAIN_BRANCH = "main"
POLICY_REHEARSAL_BRANCH = "policy-rehearsal"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub platform policy tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Verify live policy drift")
    verify.add_argument("--repo", required=True, help="Repository in owner/repo form.")
    verify.add_argument("--branch", default=MAIN_BRANCH, help="Target branch name.")
    verify.add_argument(
        "--verify-only",
        action="store_true",
        help="Explicitly acknowledge this command is verify-only.",
    )
    verify.add_argument(
        "--offline",
        action="store_true",
        help="Use deterministic offline fixture mode (for local testing).",
    )
    verify.add_argument(
        "--mechanism",
        default="branch_protection",
        choices=("rulesets", "branch_protection"),
        help="Mechanism name recorded in tracer evidence.",
    )
    verify.add_argument(
        "--evidence-path",
        default=WF0056_VERIFY_EVIDENCE_PATH,
        help="Filesystem path for evidence JSON.",
    )
    verify.add_argument(
        "--expected-policy-path",
        default="../config/platform_policy/main_policy.yaml",
        help="Expected policy definition path.",
    )

    apply_cmd = subparsers.add_parser("apply", help="Apply expected policy with safeguards")
    apply_cmd.add_argument("--repo", required=True, help="Repository in owner/repo form.")
    apply_cmd.add_argument("--branch", default=POLICY_REHEARSAL_BRANCH, help="Target branch name.")
    apply_cmd.add_argument(
        "--apply-intent",
        action="store_true",
        help="Explicitly confirm mutation intent.",
    )
    apply_cmd.add_argument(
        "--evidence-path",
        default=WF0056_APPLY_EVIDENCE_PATH,
        help="Filesystem path for apply evidence JSON.",
    )
    apply_cmd.add_argument(
        "--snapshot-dir",
        default=WF0056_SNAPSHOT_DIR,
        help="Directory to store rollback snapshots.",
    )
    apply_cmd.add_argument(
        "--expected-policy-path",
        default="../config/platform_policy/main_policy.yaml",
        help="Expected policy definition path.",
    )

    rollback = subparsers.add_parser("rollback", help="Rollback policy from snapshot")
    rollback.add_argument("--repo", required=True, help="Repository in owner/repo form.")
    rollback.add_argument("--branch", default=POLICY_REHEARSAL_BRANCH, help="Target branch name.")
    rollback.add_argument(
        "--snapshot-path",
        required=True,
        help="Snapshot artifact path generated during apply preflight.",
    )
    rollback.add_argument(
        "--evidence-path",
        default=WF0056_ROLLBACK_EVIDENCE_PATH,
        help="Filesystem path for rollback evidence JSON.",
    )
    return parser


def _run_verify(args: argparse.Namespace) -> int:
    exit_code = run_verify(
        repo=args.repo,
        branch=args.branch,
        expected_policy_path=Path(args.expected_policy_path),
        evidence_path=Path(args.evidence_path),
        offline=bool(args.offline),
    )
    print(str(args.evidence_path))
    return exit_code


def _run_apply(args: argparse.Namespace) -> int:
    if args.branch == MAIN_BRANCH:
        print("apply forbids --branch main during WF-0056 live rehearsal", file=sys.stderr)
        return 1
    if args.branch != POLICY_REHEARSAL_BRANCH:
        print(
            f"apply requires --branch {POLICY_REHEARSAL_BRANCH} during WF-0056 live rehearsal",
            file=sys.stderr,
        )
        return 1

    expected_policy_path = Path(args.expected_policy_path)
    expected_policy = load_expected_policy(expected_policy_path)
    available_check_contexts = set(expected_policy["required_checks"])

    exit_code = run_apply(
        repo=args.repo,
        branch=args.branch,
        expected_policy_path=expected_policy_path,
        evidence_path=Path(args.evidence_path),
        snapshot_dir=Path(args.snapshot_dir),
        apply_intent=args.apply_intent,
        available_check_contexts=available_check_contexts,
        can_mutate=True,
    )
    print(str(args.evidence_path))
    return exit_code


def _run_rollback(args: argparse.Namespace) -> int:
    snapshot_path = Path(args.snapshot_path)
    if not snapshot_path.exists():
        print(f"snapshot path does not exist: {snapshot_path}", file=sys.stderr)
        return 1

    exit_code = run_rollback(
        repo=args.repo,
        branch=args.branch,
        snapshot_path=snapshot_path,
        evidence_path=Path(args.evidence_path),
    )
    print(str(args.evidence_path))
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "verify":
        return _run_verify(args)
    if args.command == "apply":
        return _run_apply(args)
    if args.command == "rollback":
        return _run_rollback(args)

    raise ValueError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
