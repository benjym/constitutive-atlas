import pathlib,json,hashlib,tarfile,sys
profile=sys.argv[1];R=pathlib.Path('/Users/bmar5496/code/constitutive-atlas/docs/investigations/control-partition-derivative-v1');D=R/('current-profile-actual-'+profile+'-v3');B=pathlib.Path('/private/tmp/atlas-control-partition-profile-execution-v3')/profile;E=B/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((R/'current-profile-execution-v3/plan.json').read_text());p=next(x for x in plan['profiles']if x['profile']==profile)
receipts={x.name:json.loads(x.read_text())for x in(E/'stage-receipts').glob('*.json')}
assert len(receipts)==2*len(p['steps']) and all(q['passed']is True for q in receipts.values())
for st in p['steps']:
 proc=json.loads((E/'processes'/st['stage']/'process.json').read_text());assert proc['returncode']==0 and proc['argv']==st['argv'] and proc['cwd']==st['cwd']
 if 'assess'in st['stage']or'paired'in st['stage']:
  f=E/'processes'/st['stage']/'stdout';(D/(st['stage']+'.stdout')).write_bytes(f.read_bytes())
archive=D/('complete-'+profile+'-evidence.tar.gz');members={}
with tarfile.open(archive,'w:gz')as t:
 for f in sorted(B.rglob('*')):
  if f.is_file():
   n=str(f.relative_to(B));members[n]=sha(f);t.add(f,arcname=n,recursive=False)
with tarfile.open(archive)as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest()for m in t.getmembers()if m.isfile()}
assert actual==members
(D/'archive-receipt.json').write_text(json.dumps(dict(identity='current-'+profile+'-complete-actual-v3',archive=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,members=members,verified=True),indent=2)+'\n')
(D/'actual-summary.json').write_text(json.dumps(dict(identity='current-'+profile+'-actual-v3',stages=len(p['steps']),strict_pre_post_receipts=len(receipts),all_processes_exit_zero=True,source_files=2722,tool_files=6821,scope='Unchanged original native/Wasm source/transaction/paired gates; actual independent review pending. Not full MD/model/website approval.'),indent=2)+'\n')
(D/'README.md').write_text('# Fresh '+profile+' regression\n\nAll '+str(len(p['steps']))+' exact reviewed plan stages and '+str(len(receipts))+' strict source/tool/pre/post receipts passed. Original source/transaction/paired assessors returned success. Complete build/generated/artifact/raw/process evidence is retained in the verified archive. Unchanged collector transport limitations from the prospective plan apply.\n\nIndependent actual review remains pending; no full MD/model/website approval.\n')
(D/'retention-script.py').write_bytes(pathlib.Path(__file__).read_bytes())
(D/'manifest.json').write_text(json.dumps(dict(identity='current-'+profile+'-actual-v3',files={str(f.relative_to(D)):sha(f)for f in sorted(D.rglob('*'))if f.is_file()}),indent=2)+'\n')
h=sha(D/'manifest.json');print(json.dumps(dict(manifest=h,members=len(members),bytes=archive.stat().st_size)))
with pathlib.Path('/Users/bmar5496/code/constitutive-atlas/IMPLEMENTATION_PLAN.md').open('a')as f:f.write('\n  REGRESS-current-'+profile+'-profile-v3 slot RELEASED2026-11-02: exact'+str(len(p['steps']))+'stagesnativeTHENWasmPASS, all'+str(len(receipts))+'strictsource/tool/prepostreceiptsPASS, originalsource/transaction/pairedassessorsPASS. Completebuild/generated/artifact/raw/processarchiveverified; actualmanifest'+h+'. No numericalchanges; independentactualprofile reviewpending; no activeownedcompiledprocess. Queuedownersmayfreshclaim.\n')
