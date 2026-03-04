import sys
import os

def check_file(filepath, max_lines=45):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.", file=sys.stderr)
        return 1

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = len(lines)
    if count > max_lines:
        print(f"Error: {filepath} exceeds {max_lines} lines (current: {count}).", file=sys.stderr)
        print("Please consolidate instructions or move them to specific code modules to keep AGENTS.md concise.", file=sys.stderr)
        return 1
    return 0

def main():
    exit_code = 0
    for arg in sys.argv[1:]:
        if check_file(arg) != 0:
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
