# WF-0056 Live Run Index

Canonical registry for live-run metadata captured from GitHub Actions and normalized into a deterministic checksum payload.

## verify-main

- workflow_run_id: `22751018925`
- run_url: `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925`
- workflow: `platform-policy-live-rehearsal`
- commit_sha: `97aab2008c4c5aa33da016af87c333fc7c541145`
- linked_artifacts:
  - `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404391`
  - `artifact:wf-0056-verify-evidence#5792531332`
  - `artifact_digest=sha256:3cee1b3d8e58138bae5b236c0e2bca4a00500f2c3ec6ef030a3cff4c4ac1a6a1`
- evidence_sha256: `4300ab4c1d431a47c34a1e5011aed542f276480becfd8af3431199ed431bdc80`

## apply-rehearsal

- workflow_run_id: `22751018925`
- run_url: `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925`
- workflow: `platform-policy-live-rehearsal`
- commit_sha: `97aab2008c4c5aa33da016af87c333fc7c541145`
- linked_artifacts:
  - `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404369`
  - `artifact:wf-0056-apply-evidence#5792531122`
  - `artifact_digest=sha256:f8c7312c417d58009de6428aa79bafa93d018e0098e99b5eb5d9b6d576c9c9bd`
  - `artifact:wf-0056-apply-snapshot#5792531279`
  - `artifact_digest=sha256:dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef`
- evidence_sha256: `c38e899015690a0e6f2ee67d32f4ce0861701910b41c1019642eba06c5f6faf0`

## rollback-rehearsal

- workflow_run_id: `22751018925`
- run_url: `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925`
- workflow: `platform-policy-live-rehearsal`
- commit_sha: `97aab2008c4c5aa33da016af87c333fc7c541145`
- linked_artifacts:
  - `https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404382`
  - `annotation:Unable to download artifact(s): Artifact not found for name: wf-0056-apply-snapshot`
  - `annotation:No files were found with the provided path: docs/walkthroughs/evidence/WF-0056/rollback_evidence.json`
  - `source_snapshot_digest=sha256:dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef`
- evidence_sha256: `fa3b0b1f5f10546ad565c3af2cda0bd05e3306f8a0e8c56c3982b427d794b182`

Reproduce checksum:

```bash
python3 - <<'PY'
import hashlib
import json
import subprocess

raw = subprocess.check_output(
    ["gh", "run", "view", "22751018925", "--json", "databaseId,url,headSha,workflowName,jobs"],
    text=True,
)
data = json.loads(raw)
payload = {
    "workflow_run_id": data["databaseId"],
    "run_url": data["url"],
    "commit_sha": data["headSha"],
    "workflow": data["workflowName"],
    "operation": "apply-rehearsal",
    "linked_artifacts": [
        "https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404369",
        "artifact:wf-0056-apply-evidence#5792531122",
        "artifact:wf-0056-apply-snapshot#5792531279",
    ],
}
canon = json.dumps(payload, separators=(",", ":"), sort_keys=True)
print(hashlib.sha256(canon.encode()).hexdigest())
PY
```
