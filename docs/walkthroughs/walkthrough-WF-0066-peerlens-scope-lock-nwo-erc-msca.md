<!-- docs/walkthroughs/walkthrough-WF-0066-peerlens-scope-lock-nwo-erc-msca.md -->
# WF-0066 — PeerLens Scope Lock to NWO/ERC/MSCA

Artifact: walkthrough
Version: v0.1
Status: In progress
Last Updated: 2026-03-08

## Part A — Task 1 (Inspection Before Edits)

`phase_3_baseline_sha`: `d9f7d9df8900c07b7b90d1b1171b86db51b062ee`

Mission check was executed before any mission edit consideration and no contradiction was found.

### Named target set pre-state classification

| File | Pre-state | Classification | Evidence |
|---|---|---|---|
| `docs/parking_lot.md` | Active contradiction language still present in live planning surface. | `edit required` | `sed -n '/## 🟡 P1/,/## Rejected \\/ Ignored/p' docs/parking_lot.md \| rg -n "ZonMw\|remaining promised-program gap\|launch blocker\|broader promised-program expansion\|broader coverage remains part of the current commitment"` |
| `docs/logs/decisions.md` | AD 66.1 present and explicit scope-lock language already present. | `verified no-op` | `rg -n "AD 66\\.1\|broader promised-program expansion is not deferred" docs/logs/decisions.md` |
| `docs/memory/domain/project_docs.md` | No active contradiction-bearing line requiring scope correction in this WF. | `verified no-op` | inspection + no contradiction hit |
| `docs/mission.md` | Funded-program agnostic mission wording; no concrete contradiction with NWO/ERC/MSCA wedge. | `verified no-op` | `sed -n '1,120p' docs/mission.md` |

### Active contradiction-bearing locations to fix in Task 2

- P1 row #1 still plans a broader promised-program gap via ZonMw-equivalent expansion.
- P1 rationale snapshot still frames remaining promised-program gap as launch blocker/current blocker.
- P2 row #30 still conditions promotion on closing the remaining promised-program gap.

## Part A — Task 2 (Tracer Bullet Contradiction Rewrite)

Edited only `docs/parking_lot.md` contradiction-bearing live planning lines:
- P1 row #1 recommendation/title
- P1 rationale snapshot contradiction lines
- P2 row #30 promotion-gating wording

No edits were made to `docs/logs/decisions.md`, `docs/memory/domain/project_docs.md`, or `docs/mission.md`.

Task 2 verification:
- `sed -n '/## 🟡 P1/,/## Rejected \\/ Ignored/p' docs/parking_lot.md | rg -n "truthful|usefulness|NWO/ERC/MSCA|launch readiness"` -> pass
- `! sed -n "/## 🟡 P1/,/## Rejected \\/ Ignored/p" docs/parking_lot.md | rg -n "ZonMw|remaining promised-program gap|launch blocker|broader promised-program expansion|broader coverage remains part of the current commitment"` -> pass

Interim status for named targets:
- `docs/parking_lot.md`: `edited`
- `docs/logs/decisions.md`: pending final no-op confirmation
- `docs/memory/domain/project_docs.md`: pending final no-op confirmation
- `docs/mission.md`: pending final no-op confirmation
