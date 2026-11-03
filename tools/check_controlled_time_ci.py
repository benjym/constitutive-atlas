#!/usr/bin/env python3
"""Verify frozen controlled-time CI sources/plans; capture bytes without execution."""
import argparse,hashlib,json,os,platform,sys
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'docs/ingestion/vibe-2026/controlled-time-ci-v1'
INPUTS={
 'docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/manifest.json':'5eb8953d084061633b09160a6708d71907efb39482bf5857657a7f10c05d4d01',
 'docs/ingestion/vibe-2026/numerical-qualification-v1/source-manifest-v2.json':'bd73a00ace2f559f4396a4c8866c6d46bce43a4e275b7455255a9b90c7eef22b',
 'docs/ingestion/vibe-2026/mainatlas-implementation-v1/source-manifest-v3.json':'8d96f1496e42e8661335b42d198bb54b30b0a4b84c671eba23f4416402818996',
 'docs/ingestion/vibe-2026/controlled-time-qualification-v1/source-manifest-v3.json':'f5162e5332747c2a9b00d327608ab4fcd01cbdcef95ba83ce51488d847ffb76f'}
SELECTED={'docs/ingestion/vibe-2026/mainatlas-implementation-v1/source-manifest-v3.json':{'web/controlled-time-engine.mjs'}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe_relative(name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Expected repository-relative pin: '+name)
 return ROOT/p

def verify(report):
 checks=[]
 for name,expected in INPUTS.items():
  p=safe_relative(name);assert sha(p)==expected,name
  data=json.loads(p.read_text())
  selected=SELECTED.get(name);pins=[pin for pin in data['files'] if selected is None or pin['path'] in selected]
  if selected is not None:assert {pin['path'] for pin in pins}==selected
  for pin in pins:assert sha(safe_relative(pin['path']))==pin['sha256'],pin['path']
  checks.append(dict(path=name,sha256=expected,verified_files=[pin['path'] for pin in pins],selection='Only executed engine; inactive UI/packager source is outside backend CI closure' if selected else 'all manifest files'))
 manifest=PACKET/'source-manifest-v1.json'
 if manifest.exists():
  frozen=json.loads(manifest.read_text())
  for pin in frozen['files']:assert sha(safe_relative(pin['path']))==pin['sha256'],pin['path']
  checks.append(dict(path=str(manifest.relative_to(ROOT)),sha256=sha(manifest),files=len(frozen['files'])))
 else:raise ValueError('CI source freeze missing')
 oldpath=ROOT/'docs/ingestion/vibe-2026/numerical-qualification-v1/plan-v2.json';old=json.loads(oldpath.read_text());new=json.loads((PACKET/'plan-v3.json').read_text());proof=json.loads((PACKET/'portable-plan-proof.json').read_text())
 assert sha(oldpath)==proof['original_sha256'];assert sha(PACKET/'plan-v3.json')==proof['portable_sha256']
 reverse=deepcopy(new);reverse['identity']=old['identity']
 for delta in proof['path_changes']:
  assert new['source_files'][delta['index']]['path']==delta['after'];reverse['source_files'][delta['index']]['path']=delta['before']
 assert reverse==old and (json.dumps(reverse,indent=2)+'\n').encode()==oldpath.read_bytes()
 assert new['identity']=='vibe2026-backend-qualification-v3-portable-pin-paths'
 for pin in new['source_files']:assert sha(safe_relative(pin['path']))==pin['sha256'],pin['path']
 result=dict(status='pass-source-only',compiled_calls=0,input_manifests=checks,portable_plan_sha256=proof['portable_sha256'],points=len(new['points']),histories=len(new['histories']),invalid_contexts=len(new['invalid_cases']),path_changes=len(proof['path_changes']),reverse_original_byte_identity=True)
 write_new(report,result);return result

def write_new(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(data,f,indent=2);f.write('\n')

def capture(output,paths):
 # Always-run byte capture intentionally does not execute tools or import a model.
 files=[];missing=[]
 for raw in paths:
  p=safe_relative(raw)
  if not p.exists():missing.append(raw);continue
  candidates=[p] if p.is_file() else sorted(x for x in p.rglob('*') if x.is_file())
  for f in candidates:files.append(dict(path=str(f.relative_to(ROOT)),sha256=sha(f),bytes=f.stat().st_size))
 data=dict(kind='controlled-time-ci-executed-byte-receipt-v1',github_sha=os.environ.get('GITHUB_SHA'),run_id=os.environ.get('GITHUB_RUN_ID'),python=sys.version,platform=platform.platform(),collector='tools/check_controlled_time_ci.py',collector_sha256=sha(__file__),files=files,missing_paths=missing)
 write_new(output,data);return dict(status='captured-existing-bytes-only',files=len(files),missing_paths=missing)

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);v=sub.add_parser('verify');v.add_argument('--report',type=Path,required=True);c=sub.add_parser('capture');c.add_argument('--output',type=Path,required=True);c.add_argument('paths',nargs='+');a=p.parse_args()
 print(json.dumps(verify(a.report) if a.mode=='verify' else capture(a.output,a.paths),indent=2))
if __name__=='__main__':main()
