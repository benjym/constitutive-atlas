"""Package checked evidence envelopes only; never rerun scientific checkers or copy raw artifacts."""
import copy,hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas.evidence import validate_record,verify_manifest_files
from atlas.model import ROOT

RESEARCH_BINDINGS=(
 ('barodesy-clay-2017','models/research/barodesy2017/body-zero-spin.json','barodesy2017-runtime-v1'),
 ('barodesy-clay-2017','models/research/barodesy2017/body-zero-spin.json','barodesy2017-integration-v1'),
 ('barodesy-clay-2017','models/research/barodesy2017/body-zero-spin.json','barodesy2017-hydro-ad-v1'),
 ('barodesy-clay-2017','models/research/barodesy2017/body-zero-spin.json','barodesy2017-wider-integration-v1'),
 ('hypoplastic-clay-2013','models/research/clay2013/hypoplastic-clay-2013-research.json','clay2013-integration-v1'),
 ('hypoplastic-clay-2014','models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json','clay2014-rates-v1'),
 ('hypoplastic-clay-2014','models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json','clay2014-paths-v1'),
 ('hypoplastic-generalized-igs-2024','models/research/gis2024/hp-extracted-asbs-gis-2024-research.json','gis2024-coupled-rates-v1'),
 ('hypoplastic-generalized-igs-2024','models/research/gis2024/hp-extracted-asbs-gis-2024-research.json','gis2024-integration-v1'),
)
FLAGS=('public_admission','complete_model','scientific_review','experimental_validation','integration','AD','source_repair','finite_integration_verified')
def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def read_bytes(root,relative):
 p=Path(relative)
 if p.is_absolute()or '..'in p.parts:raise ValueError('unsafe evidence export path')
 target=(root/p).resolve()
 if not target.is_relative_to(root)or not target.is_file():raise ValueError('missing/unsafe evidence export file: '+str(relative))
 return target.read_bytes()
def parse(value):return json.loads(value,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite evidence JSON')))
def text(value,label):
 if type(value)is not str:raise ValueError(label+' must be a string')
 return value
def strings(value,label):
 if type(value)is not list or any(type(x)is not str for x in value):raise ValueError(label+' must be strings')
 return copy.deepcopy(value)
def current_definition(root,path,expected):
 target=(root/path).resolve()
 if not target.is_relative_to(root):raise ValueError('definition escapes repository')
 if target.exists()and not target.is_file():raise ValueError('definition is not a file')
 actual=sha_bytes(target.read_bytes())if target.is_file()else None
 return actual==expected,actual

def bundle(destination,root=ROOT,*,bindings=RESEARCH_BINDINGS):
 """Return/write evidence.json plus exact original JSON at evidence-records/<path>.

 Integrity checks are read-only and complete before destination writes. Missing,
 changed or unsafe artifacts in any selected receipt fail packaging. Historical
 numerical outcomes remain visible even when their current definitions differ.
 """
 root=Path(root).resolve();destination=Path(destination)
 if not(root/'catalogue/evidence').is_dir():raise ValueError('numerical evidence directory missing')
 catalogue=parse(read_bytes(root,'catalogue/manifest.json'))
 models=catalogue.get('models');
 if type(models)is not list:raise ValueError('catalogue model list missing')
 ids=[m.get('id')for m in models]
 if any(type(x)is not str for x in ids)or len(set(ids))!=len(ids):raise ValueError('invalid/duplicate catalogue IDs')
 by_id={m['id']:m for m in models};records=[];originals={};selected=set()
 def entry(catalogue_id,definition,path,raw,kind,expected,record):
  if catalogue_id not in by_id:raise ValueError('evidence has no canonical catalogue entry: '+catalogue_id)
  if Path(definition).is_absolute()or '..'in Path(definition).parts:raise ValueError('unsafe definition binding')
  match,actual=current_definition(root,definition,expected)
  result=dict(catalogue_id=catalogue_id,definition_path=definition,definition_sha256=expected,current_definition_sha256=actual,definition_current=match,record_path=path,record_sha256=sha_bytes(raw),kind=kind,outcome=record.get('outcome'),scope='',limitations=[],admission_flags={k:copy.deepcopy(record[k])for k in FLAGS if k in record},catalogue_status=by_id[catalogue_id].get('status'))
  if result['outcome']is not None:text(result['outcome'],'outcome')
  originals[path]=raw;records.append(result);return result
 for path in sorted((root/'catalogue/evidence').glob('*.json')):
  relative=path.relative_to(root).as_posix();raw=read_bytes(root,relative);record=parse(raw)
  if record.get('kind')!='numerical-evidence':
   if relative=='catalogue/evidence/source-archive-map.json'and record.get('version')=='immutable-source-archive-map-0.1':continue
   if record.get('kind')=='source-review':continue
   raise ValueError('unsupported top-level evidence envelope: '+relative)
  checked=validate_record(path,root=root,current=False)
  if checked!=record or read_bytes(root,relative)!=raw:raise ValueError('evidence envelope changed during validation')
  mid=record['model']['id'];e=entry(mid,'models/'+mid+'.json',relative,raw,'numerical-evidence',record['model']['definition_sha256'],record)
  e['scope']=text(record['scope'],'scope');e['limitations']=strings(record['limitations'],'limitations')
  e['details']={'executor':copy.deepcopy(record['executor']),'source_commit':record['source_commit'],'created_at':record['created_at']}
 for catalogue_id,definition,packet in bindings:
  relative='catalogue/investigations/'+packet+'/manifest.json'
  if relative in selected:raise ValueError('duplicate research binding')
  selected.add(relative);raw=read_bytes(root,relative);manifest=parse(raw)
  files=manifest.get('files');dependencies=manifest.get('dependencies',{})
  if type(files)is not dict or type(dependencies)is not dict:raise ValueError('unsupported research manifest maps: '+relative)
  if any(k in files and files[k]!=v for k,v in dependencies.items()):raise ValueError('conflicting manifest receipt pins')
  checked=verify_manifest_files(root,relative)
  if checked!=manifest or read_bytes(root,relative)!=raw:raise ValueError('research manifest changed during validation')
  pins=dependencies|files
  if definition not in pins:raise ValueError('research definition absent from manifest receipt: '+relative)
  e=entry(catalogue_id,definition,relative,raw,'research-manifest',pins[definition],manifest)
  # No inferred "passed": manifests without an explicit outcome export null.
  e['scope']=text(next((manifest[k]for k in('scope','source_variant','variant')if k in manifest),''),'scope')
  e['limitations']=strings(manifest.get('limitations',manifest.get('limits',[])),'limitations')
  if 'replay_policy'in manifest:e['limitations'].append(text(manifest['replay_policy'],'replay_policy'))
  e['details']={k:copy.deepcopy(v)for k,v in manifest.items()if k not in ('files','dependencies','scope','source_variant','variant','limitations','limits',*FLAGS,'outcome')}
 omitted=sorted(p.relative_to(root).as_posix()for p in(root/'catalogue/investigations').glob('*/manifest.json')if p.relative_to(root).as_posix()not in selected)
 index={'schema_version':'0.1','kind':'catalogue-evidence-index','coverage_note':'Top-level numerical evidence envelopes are auto-discovered, including historical failed outcomes. Research coverage is restricted to explicit canonical-catalogue/definition/manifest bindings; other investigation manifests and source-review records are omitted. Checked receipts establish retained-file integrity only: no scientific checker, binary, experimental validation or admission is rerun. Missing manifest scope/limitations are left empty; complete retained metadata is supplied in details.','coverage':{'numerical_record_directory':'catalogue/evidence','research_manifest_allowlist':sorted(selected),'omitted_investigation_manifests':omitted,'scientific_rerun':False},'records':records}
 encoded=(json.dumps(index,indent=2,allow_nan=False)+'\n').encode()
 # Replace only this exporter's private subtree; preserve builder-owned assets.
 if destination.is_symlink()or(destination/'evidence.json').is_symlink():raise ValueError('evidence export destination is a symlink')
 destination.mkdir(parents=True,exist_ok=True);record_dest=destination/'evidence-records'
 if record_dest.is_symlink():raise ValueError('evidence record destination is a symlink')
 if record_dest.exists():shutil.rmtree(record_dest)
 for path,raw in originals.items():
  target=record_dest/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 (destination/'evidence.json').write_bytes(encoded)
 return index

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();bundle(a.destination,a.root)
