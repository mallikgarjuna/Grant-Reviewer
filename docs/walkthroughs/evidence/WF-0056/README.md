# WF-0056 Evidence Bundle

## Layout
- `tracer_verify_evidence.json`
- `apply_evidence.json`
- `rollback_evidence.json`
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

## Required Proof Fields
Every final evidence payload recorded in walkthrough must expose:
- `workflow_run_id`
- run URL
- `commit_sha`
- `evidence_sha256`
- `linked_artifacts`
