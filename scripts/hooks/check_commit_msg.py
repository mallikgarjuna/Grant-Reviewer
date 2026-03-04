import sys
import re
import os

def check_commit_msg(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Commit message file {filepath} not found.", file=sys.stderr)
        return 1

    with open(filepath, 'r') as f:
        content = f.read().strip()

    if not content:
        print("Error: Commit message is empty.", file=sys.stderr)
        return 1

    first_line = content.split('\n')[0]

    # Exceptions
    if first_line.startswith("Merge branch") or first_line.startswith("Revert"):
        return 0

    # Standard format: WF-XXXX: <slug> — Task <N> — <short title>
    # Requirement: ^WF-\d{4}.*:
    pattern = r'^WF-\d{4}.*: '
    if re.match(pattern, first_line):
        return 0

    print(f"Error: Invalid commit message prefix. Must start with 'WF-XXXX: ' or be a Merge/Revert. (Current: {first_line})", file=sys.stderr)
    return 1

def main():
    if len(sys.argv) < 2:
        # Pre-commit passes the file path as the first argument
        sys.exit(0) # Or handled differently

    sys.exit(check_commit_msg(sys.argv[1]))

if __name__ == "__main__":
    main()
