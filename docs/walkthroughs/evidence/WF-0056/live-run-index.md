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
- evidence_sha256: `0de58e3d9bd6ecc0b05e85a565b70559ebb4231bf158b87941cbb7fa167d098c`

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
- evidence_sha256: `5a7b47ecb17fba138fba3598036a7522c4dedc16725c8e3975b8f04b9ca4ef20`

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
- evidence_sha256: `7910bd5a97fdc96182efd66aac053fdee3f278566d2800920368cdac63173748`

Reproduce checksums:

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
payloads = {
    "verify-main": {
        "workflow_run_id": data["databaseId"],
        "run_url": data["url"],
        "commit_sha": data["headSha"],
        "workflow": data["workflowName"],
        "operation": "verify-main",
        "linked_artifacts": [
            "https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404391",
            "artifact:wf-0056-verify-evidence#5792531332",
        ],
    },
    "apply-rehearsal": {
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
    },
    "rollback-rehearsal": {
        "workflow_run_id": data["databaseId"],
        "run_url": data["url"],
        "commit_sha": data["headSha"],
        "workflow": data["workflowName"],
        "operation": "rollback-rehearsal",
        "linked_artifacts": [
            "https://github.com/mallikgarjuna/Grant-Reviewer/actions/runs/22751018925/job/65985404382",
            "annotation:Unable to download artifact(s): Artifact not found for name: wf-0056-apply-snapshot",
            "annotation:No files were found with the provided path: docs/walkthroughs/evidence/WF-0056/rollback_evidence.json",
            "source_snapshot_digest=sha256:dc40036c1f884fb2ab2b29495acfd4c18df2f3b191eb894a57e6c0fdce16aeef",
        ],
    },
}
for name, payload in payloads.items():
    canon = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    print(name, hashlib.sha256(canon.encode()).hexdigest())
PY
```
