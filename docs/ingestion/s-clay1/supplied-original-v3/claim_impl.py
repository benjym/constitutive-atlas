from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent
p=R/'IMPLEMENTATION_PLAN.md';b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
r=subprocess.run(['rg','-l','-F',h,'catalogue','docs','tools','schemas','tests','-g','*.json','-g','!**/source-snapshots/**','-g','!docs/ingestion/s-clay1/supplied-original-v3/claim-v3.json'],cwd=R,capture_output=True,text=True)
assert r.returncode==1,r.stdout
q=R/'catalogue/source-snapshots'/h/'IMPLEMENTATION_PLAN.md';q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
s='''\n- [-] **IMPL-s-clay1-candidate-v3** — Coordinator /root owns NEW supplied-original-v3/candidate/, contract/profile/reference/gate/check records in supplied-original-v3/ and ignored .local/s-clay1-delivery-v3/ isolated generated/source/build resources. Complete original constantM3D law, v0.3 residual realization; no reduced triaxial or fabricated later extension. Pure Python validation/codegeneration/reference work now authorized; generic shared code stays read-only. No compiled/build/browser slot from this handoff; separate fresh serial claim required. E0–E8 umbrella remains open.\n'''
assert p.read_bytes()==b;p.write_bytes(b+s.encode())
(O/'implementation-claim.json').write_text(json.dumps({'before':h,'archive':str(q.relative_to(R)),'after':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'IMPL-s-clay1-candidate-v3','compiled_execution':False},indent=2)+'\n')
