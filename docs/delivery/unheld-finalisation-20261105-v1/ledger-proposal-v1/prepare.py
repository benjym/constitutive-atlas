"""Propose five ledgers/archive originals only. No source installation."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3];N=P.parent;W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');PREFIX='docs/delivery/unheld-finalisation-20261105-v1/'
IDS=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97']
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(x):return (json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
refs={'package':'package-review-v1','numerical':'current16-qualification-result-review-v1','examples':'nine-example-result-review-v1','controlled':'controlled-path-refresh-review-v1/actual-results-v1','overlay':'current-main-overlay-review-v1'}
pins={}
for name,directory in refs.items():
 for file in ['decision.json','manifest.json']:
  q=N/directory/file;pins[name+'_'+file]={'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q.read_bytes())}
for file in ['RESOURCES.json','source-export-v1/receipt.json','package-inventory-v1.json','overlay-install-v1.json','nine-example-install-v1.json','qualification-observations-v1.json','controlled-path-observations-v1.json','cache-copy-v1.json']:
 q=N/file;pins[file]={'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q.read_bytes())}
package=json.loads((N/'package-review-v1/decision.json').read_text());numerical=json.loads((N/'current16-qualification-result-review-v1/decision.json').read_text());examples=json.loads((N/'nine-example-result-review-v1/decision.json').read_text());controlled=json.loads((N/'controlled-path-refresh-review-v1/actual-results-v1/decision.json').read_text())
assert package['status']=='accepted' and numerical['decision']==examples['decision']=='accepted' and controlled['status']=='accepted'
assert not package['blocking_findings'] and not numerical['unresolved_blockers'] and not examples['unresolved_blockers'] and not controlled['blocking_findings']
resources=json.loads((N/'RESOURCES.json').read_text());changes=[];missing=[]
for mid in IDS:
 path=f'docs/ingestion/{mid}/DELIVERY.md';source=W/path
 if not source.is_file():missing.append(path);continue
 old=source.read_bytes();oldsha=sha(old);archive=f'catalogue/source-snapshots/{oldsha}/{path}';ap=P/'proposed'/archive;ap.parent.mkdir(parents=True,exist_ok=True);ap.write_bytes(old)
 modelpath=f'models/{mid}.json';model=(W/modelpath).read_bytes();reviewpath=f'catalogue/agent-reviews/{mid}-v03-agent-v1.json';review=(W/reviewpath).read_bytes();record=json.loads(review);assert record['model']['sha256']==sha(model) and record['status']=='accepted'
 def link(relative,label):return f'[{label}](../../delivery/unheld-finalisation-20261105-v1/{relative})'
 top=f'''# {mid} — current delivery snapshot (2026-11-05)

This snapshot supersedes the delivery status of the verbatim historical ledger below. It is a proposed coordinator tracking update, not a new scientific review or publication receipt.

- Umbrella: `MODEL-{mid}`; delivery coordinator `/root`; proposed tracking author `/root/baseline_migration`.
- Exact current candidate: `{modelpath}`, schema0.3, SHA-256 `{sha(model)}`.
- Exact scientific authority: [{reviewpath.split('/')[-1]}](../../../{reviewpath}), SHA-256 `{sha(review)}`. Its named source/numerical scope and limitations remain unchanged; historical legacy approvals do not transfer.
- Current ordinary catalogue: `{numerical['catalogue_hash']}`; sixteen ordinary models. Source base: current-main `6b957b866c977263fad0c02be4216c7f9170cf5b` plus independently accepted exact overlay/metadata/example/controlled-source deltas. No root/shared or source installation is performed by this proposed ledger.

## Current E0–E8 status

- [X] **E0 — Claim/scope:** coordinator-owned five-model current-release scope and independent child reviews recorded on the live board; bounded explicit source/build handoffs retained.
- [X] **E1 — Sources:** exact primary-source crosswalk/receipts, private-original rights boundaries and independent accepted v0.3 source review retained. Broader parameter, preparation, calibration and experimental claims remain outside approval.
- [X] **E2 — Contract:** actual current schema0.3 definition declares explicit formulation, fixed-frame/zero-spin effective-stress Mandel conventions, caller-supplied persistent initialization and finite six-component strain-path loading. It is no longer an in-memory crosswalk alone.
- [X] **E3 — Definition:** exact hash above is the declarative v0.3 candidate; no model-specific handwritten kernel. Its genuine exact independent E5 record binds the source-supported transcription.
- [X] **E4 — Native/Wasm:** {link('current16-qualification-result-review-v1/decision.json','accepted actual current-sixteen result review')} binds current native/Wasm artifacts, generated/described catalogue identity and unchanged five-model suite:701 original reference cases per backend,42 interface cases/87 interface calls, original rollback/recovery/finite-loading gates. This does not scientifically approve the other eleven models or extend arbitrary-path accuracy.
- [X] **E5 — Independent agent approval:** exact accepted v0.3 record above is the scientific authority. Current active registry supersedes the five legacy registrations, preserving the other25 ordered approval objects; original registry/model/review bytes and explicit supersession history remain exact.
- [X] **E6 — Atlas/source package integration:** {link('package-review-v1/decision.json','accepted full-package integration review')} binds actual package inventory1549 files/1,109,907,607 bytes,16 ordinary models,15 reviewer-counted engine roles,30 active approvals,33 public review projections,26 registered SQLite reviews and unchanged43 scoped cases. Reader profiles, source/evidence links, prior public models/S-CLAY1/VIBE and exact new definitions are checked. {link('nine-example-result-review-v1/decision.json','Accepted nine actual examples')} and {link('controlled-path-refresh-review-v1/actual-results-v1/decision.json','controlled-path actual result review')} supply separate exact dependent receipts. Full package acceptance is not browser or live delivery.
- [-] **E7 — Actual browser qualification:** pending completion and independent acceptance of current-package browser evidence. Verify the actual visible public profile/default/named example, readable units/technical disclosure, import/export/exact replay, invalid-input export blocking, reset/recovery and narrow viewport. No browser success is inferred from source/package tests.
- [ ] **E8 — Verified live delivery:** pending release-source identity, authorized publication/CI/Pages success and exact live asset/model-run checks. No deployment or successful live current-v0.3 delivery is claimed by this snapshot.

## Current evidence and remaining handoff

| Authority | SHA-256 | Bounded claim |
| --- | --- | --- |
'''
 for name,label in [('numerical','Current native/Wasm'),('examples','Nine actual named examples'),('controlled','Controlled-path dependencies'),('package','Actual full package')]:
  d=pins[name+'_decision.json'];m=pins[name+'_manifest.json'];top+=f"| [{label}](../../../{d['path']}) | `{d['sha256']}`; manifest `{m['sha256']}` | Exact accepted decision scope only; no experimental/browser/live transfer. |\n"
 top+='''
The nine examples are new actual response envelopes; the original four labels/descriptions/requests are retained and old envelopes remain historical. Native/Wasm selected physical fields retain the original1e-10 parity budget, other channels are exact, same-backend replay is exact excluding elapsed_ms, and all45 pure parser negatives/backend pass. Historical response differences are diagnostic only; no old-to-new tolerance or zero-difference gate was invented.

The package reviewer independently accepted retained dependency guards and current-source controlled-path results. Maxwell and other reused published assets retain their original qualified identities; no arbitrary receipt repinning is authorized. Preserve all original native/build metadata failures, reviewer failures, historical package/browser/CI failures and source archives.

Next coordinator action: finish actual current-package browser qualification and its separate review; append a distinct hash-bound E7 result, then perform only the authorized release/live operation with exact source/package identity and append E8 evidence. Keep the umbrella open until E8 is actually verified.

## Resource and cleanup accounting

Coordinator resources are tracked in [RESOURCES.json](../../delivery/unheld-finalisation-20261105-v1/RESOURCES.json), with exact build/package pins in the accepted decisions above. Its timestamped entries are historical observations; stale “active/pending” text is not a fresh process/cleanup assertion. Retain:

- `/private/tmp/atlas-baseline-delivery-20261105/source` and original `current-main.tar` source archive until release consumers and durable recovery finish.
- `/private/tmp/atlas-baseline-current16-qualification-build-v1` native/Wasm artifacts and owned `em-cache`, until exact artifact/generation/receipt retention and consumers finish.
- `/private/tmp/atlas-baseline-delivery-20261105/source/.local/controlled-path-refresh-20261105-v1` until required artifacts/raw qualification receipts are durably retained and package/live consumers finish; retained numerical outputs also exist in the delivery packet.
- `/private/tmp/atlas-baseline-delivery-20261105/site-v1`, current1549-file package, until actual browser/live consumers finish and exact recovery is verified.
- `output/playwright/baseline-five-e7-20261105-v1` actual-browser evidence and parent-owned npm/private cache resources; exact current state remains coordinator-owned.

No path removal, reclaimed-space claim, preview termination or process-state assertion was made by the ledger author. This author created only proposed text/archive/check files, no build/cache/process/temp resources. Parent must record exact ownership/active consumers/status/evidence references and durable lossless retention before cleanup; preserve private originals, unique failures, measurements and `paper/`. These resources remain retained, not abandoned or implicitly disposable.

## Historical ledger retained verbatim

The following records the prior exact legacy candidate/task and its then-pending gates. Its historical limitations/failures remain evidence; its obsolete current-state statements do not override the 2026-11-05 snapshot above. Exact original bytes are also retained at `'''+archive+'''`.

---

'''
 out=P/'proposed'/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(top.encode()+old)
 for target,payload,pre in [(path,out,oldsha),(archive,ap,None)]:
  actual=W/target
  if target==archive and actual.is_file():assert actual.read_bytes()==old;continue
  changes.append({'path':target,'preimage_sha256':pre,'sha256':sha(payload.read_bytes()),'bytes':payload.stat().st_size,'mode':'100644','proposal':payload.relative_to(P).as_posix()})
(P/'source-delta.json').write_bytes(dump({'scope':'proposed five current E0-E6 tracking snapshots; E7/E8 pending; no installation','files':changes}))
(P/'evidence-pins.json').write_bytes(dump(pins));(P/'resource-snapshot.json').write_bytes(dump({'source':pins['RESOURCES.json'],'snapshot':resources,'interpretation':'timestamped retained resource inventory; no fresh liveness or cleanup assertion'}));(P/'missing-paths.json').write_bytes(dump(missing));assert not missing
print(json.dumps({'model_ledgers':len(IDS),'missing':missing,'proposed_operations':len(changes),'bytes':sum(r['bytes'] for r in changes)},indent=2))
