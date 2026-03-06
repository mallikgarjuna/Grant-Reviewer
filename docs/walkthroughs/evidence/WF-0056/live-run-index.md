# WF-0056 Live Run Index

Canonical registry for live-run metadata captured from GitHub Actions and normalized into a deterministic checksum payload.

## verify-main

- workflow_run_id: `22735688979`
- run_url: `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22735688979`
- workflow: `verify-platform-policy`
- commit_sha: `771ebe9b8362fda24febdab4b943749d131c8011`
- linked_artifacts:
  - `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22735688979/job/65936340391`
- evidence_sha256: `0a5a5ee0c9cfd7b555f1932ff1c244c6dfc146435faab30a1d56298a0b412a2d`

Reproduce checksum:

```bash
python3 - <<'PY'
import hashlib
import json
import subprocess

raw = subprocess.check_output(
    ["gh", "run", "view", "22735688979", "--json", "databaseId,url,headSha,workflowName,jobs"],
    text=True,
)
data = json.loads(raw)
payload = {
    "workflow_run_id": data["databaseId"],
    "run_url": data["url"],
    "commit_sha": data["headSha"],
    "workflow": data["workflowName"],
    "linked_artifacts": [job["url"] for job in data.get("jobs", [])],
}
canon = json.dumps(payload, separators=(",", ":"), sort_keys=True)
print(hashlib.sha256(canon.encode()).hexdigest())
PY
```
