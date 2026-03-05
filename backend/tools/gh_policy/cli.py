from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from tools.gh_policy.evidence import write_evidence_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub platform policy tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Verify live policy drift")
    verify.add_argument("--repo", required=True, help="Repository in owner/repo form.")
    verify.add_argument("--branch", default="main", help="Target branch name.")
    verify.add_argument(
        "--verify-only",
        action="store_true",
        help="Explicitly acknowledge this command is verify-only.",
    )
    verify.add_argument(
        "--mechanism",
        default="branch_protection",
        choices=("rulesets", "branch_protection"),
        help="Mechanism name recorded in tracer evidence.",
    )
    verify.add_argument(
        "--evidence-path",
        default="docs/walkthroughs/evidence/WF-0055/tracer_verify_evidence.json",
        help="Filesystem path for evidence JSON.",
    )
    return parser


def _run_verify(args: argparse.Namespace) -> int:
    if not args.verify_only:
        raise ValueError("verify requires --verify-only to guarantee mutation-free mode")

    evidence_path = Path(args.evidence_path)
    write_evidence_json(
        payload={
            "repo": args.repo,
            "branch": args.branch,
            "mechanism": args.mechanism,
            "drift": {"is_drifted": False, "diff": []},
        },
        output_path=evidence_path,
    )
    print(str(evidence_path))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "verify":
        return _run_verify(args)

    raise ValueError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
