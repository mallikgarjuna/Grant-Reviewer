# WF-0056 Evidence Bundle

## Layout
- `live-run-index.md` (canonical live-run metadata registry with checksums)
- `tracer_verify_evidence.json` (legacy placeholder path; do not use for final live evidence)
- `apply_evidence.json` (legacy placeholder path; do not use for final live evidence)
- `rollback_evidence.json` (legacy placeholder path; do not use for final live evidence)
- `snapshots/`
- `checksums.sha256`

## Fallback Storage Layout
If workflow artifacts are unavailable, store local captures in the same structure under:
- `docs/walkthroughs/evidence/WF-0056/fallback/`

## Checksum Commands
- Generate evidence checksums:
  - `cd docs/walkthroughs/evidence/WF-0056 && sha256sum tracer_verify_evidence.json apply_evidence.json rollback_evidence.json > checksums.sha256`
- Generate snapshot checksums:
  - `cd docs/walkthroughs/evidence/WF-0056/snapshots && sha256sum *.json > snapshot_checksums.sha256`
- Generate canonical live-run checksum payload for verify-main:
  - `python3 - <<'PY'`
  - `import hashlib, json, subprocess`
  - `raw = subprocess.check_output(['gh','run','view','22735688979','--json','databaseId,url,headSha,workflowName,jobs'], text=True)`
  - `data = json.loads(raw)`
  - `payload = {'workflow_run_id': data['databaseId'], 'run_url': data['url'], 'commit_sha': data['headSha'], 'workflow': data['workflowName'], 'linked_artifacts': [job['url'] for job in data.get('jobs', [])]}`
  - `canon = json.dumps(payload, separators=(',', ':'), sort_keys=True)`
  - `print(hashlib.sha256(canon.encode()).hexdigest())`
  - `PY`

## Required Proof Fields
Every final evidence payload recorded in walkthrough must expose:
- `workflow_run_id`
- run URL
- `commit_sha`
- `evidence_sha256`
- `linked_artifacts`
