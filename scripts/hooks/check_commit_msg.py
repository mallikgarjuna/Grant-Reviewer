import sys
import re
import os

WF_PREFIX_PATTERN = re.compile(r"^WF-\d{4}.*: ")
MAINTENANCE_PREFIX_PATTERN = re.compile(r"^(fix|chore): ")


def check_commit_msg(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Commit message file {filepath} not found.", file=sys.stderr)
        return 1

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    if not content:
        print("Error: Commit message is empty.", file=sys.stderr)
        return 1

    first_line = content.split('\n')[0]

    # Exceptions
    if first_line.startswith("Merge branch") or first_line.startswith("Revert"):
        return 0

    # Accepted formats:
    # - WF-XXXX: <slug> — Task <N> — <short title>
    # - fix: <short title>
    # - chore: <short title>
    if WF_PREFIX_PATTERN.match(first_line) or MAINTENANCE_PREFIX_PATTERN.match(first_line):
        return 0

    print(f"Error: Invalid commit message prefix. (Current: '{first_line}')", file=sys.stderr)
    print(
        "Format must be: 'WF-XXXX: <slug> — Task <N> — <short title>' or "
        "'fix: <short title>' or 'chore: <short title>'",
        file=sys.stderr,
    )
    print("Exceptions: 'Merge branch ...' or 'Revert ...'", file=sys.stderr)
    return 1

def main():
    if len(sys.argv) < 2:
        # Pre-commit passes the file path as the first argument
        sys.exit(0) # Or handled differently

    sys.exit(check_commit_msg(sys.argv[1]))

if __name__ == "__main__":
    main()
