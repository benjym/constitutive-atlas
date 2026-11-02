#!/usr/bin/env python3
"""Pure source/receipt checks; no material/package/browser calls."""
from pathlib import Path
import ast,collections,hashlib,json,subprocess,sys,tempfile,shutil
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[3]))
from atlas.evidence import checked_receipt

def parse_profile(path):
 s=path.read_text();prefix='export const modelProfiles = ';offset=s.index(prefix);return json.loads(s[offset+len(prefix):].rstrip().removesuffix(';'))
def check():
 checks=[]
 def record(label,condition):
  assert condition,label;checks.append(label)
 status=json.loads((P/'three-way-status.json').read_text())
 for f in ['catalogue/approved-models.json','catalogue/manifest.json']:
  b,a,c=[json.loads((P/'inputs'/side/f).read_text()) for side in ['base','interface','published']];m=json.loads((P/'proposed'/f).read_text());bm={r['id']:r for r in b['models']};am={r['id']:r for r in a['models']};cm={r['id']:r for r in c['models']};mm={r['id']:r for r in m['models']}
  record(f+' exact unique ID union',len(mm)==len(m['models']) and set(mm)==set(am)|set(cm))
  record(f+' unchanged all base entries',all(mm[k]==am[k]==cm[k]==bm[k] for k in bm if am[k]==bm[k] and cm[k]==bm[k]))
  record(f+' retained interface changes',all(mm[k]==v for k,v in am.items() if k not in bm or v!=bm[k]))
  record(f+' retained published changes',all(mm[k]==v for k,v in cm.items() if k not in bm or v!=bm[k]))
  for k,v in b.items():
   if k!='models':record(f+' metadata '+k,m[k]==a[k]==c[k]==v)
 b,a,c=[parse_profile(P/'inputs'/side/'web/model-profile-data.mjs') for side in ['base','interface','published']];m=parse_profile(P/'proposed/web/model-profile-data.mjs')
 record('profile exact unique ID union',set(m)==set(a)|set(c))
 record('profile original unchanged rows',all(m[k]==v for k,v in b.items() if a[k]==v and c[k]==v))
 record('profile exact interface changes',all(m[k]==v for k,v in a.items() if k not in b or v!=b[k]))
 record('profile exact published changes',all(m[k]==v for k,v in c.items() if k not in b or v!=b[k]))
 # Gate preservation: every prior/additional workflow command and all builder call ASTs remain.
 m=(P/'proposed/.github/workflows/verify.yml').read_text();mc=collections.Counter(x.strip() for x in m.splitlines() if x.strip())
 for side in ['base','interface','published']:
  cc=collections.Counter(x.strip() for x in (P/'inputs'/side/'.github/workflows/verify.yml').read_text().splitlines() if x.strip());record('workflow all '+side+' line multiplicities',all(mc[k]>=v for k,v in cc.items()))
 def calls(path):return collections.Counter(ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Call))
 mc=calls(P/'proposed/tools/build_web.py')
 for side in ['base','interface','published']:
  cc=calls(P/'inputs'/side/'tools/build_web.py');record('builder all '+side+' call ASTs',all(mc[k]>=v for k,v in cc.items()))
 app=(P/'proposed/web/app.js').read_text()
 for control in ['Interface2016','Perzyna','Bingham','Hill','Timed','Sls','KelvinVoigt','Orthotropic','Path','Maxwell','ImplicitPath']:
  record('app controller '+control,('setup'+control+'Laboratory(') in app)
 record('app interface technical branch retained',"entry.id==='hvwe2016-reconciled-fixed-local'" in app)
 record('app Perzyna technical branch retained',"entry.id==='perzyna-comsol63-mises-perfect-zero-spin-ode'" in app)
 for f in ['ROADMAP.md','docs/STATUS.md']:
  b=(P/'inputs/base'/f).read_bytes();a=(P/'inputs/interface'/f).read_bytes();c=(P/'inputs/published'/f).read_bytes();record(f+' exact both appendices',(P/'proposed'/f).read_bytes()==c+a[len(b):])
 for f in ['web/app.js','web/model-profile-data.mjs']:
  subprocess.run(['node','--check',str(P/'proposed'/f)],check=True,capture_output=True);checks.append(f+' Node syntax')
 for f in (P/'proposed').rglob('*'):
  if f.is_file():record('no merge marker '+str(f.relative_to(P/'proposed')),b'<<<<<<<' not in f.read_bytes())
 # Reproduce normal receipt resolution against changed live sources + exact originals.
 audit=json.loads((P/'receipt-pin-audit.json').read_text());record('all bounded pins resolved',audit['unresolved']==0)
 with tempfile.TemporaryDirectory(prefix='resolver-check-',dir=P) as temp:
  root=Path(temp)
  shutil.copytree(P/'proposed',root,dirs_exist_ok=True)
  for row in audit['rows']:
   target=root/row['document']
   if not target.exists():
    raw=subprocess.check_output(['git','show',status['refs'][row['side']]+':'+row['document']]);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
   selected=checked_receipt(root,row['document'],row['original_path'],row['sha256'])
   record('normal receipt '+row['document']+' '+row['original_path'],hashlib.sha256(selected.read_bytes()).hexdigest()==row['sha256'] and 'source-snapshots' in selected.parts)
 # Additive ledger-v3 map union must retain every original binding and exact archived source.
 ledger_path='docs/ingestion/hypoplastic-interface-2016/tracking-review-v1/source-archive-map.json'
 ledger=json.loads((P/'inputs/ledger-v3'/ledger_path).read_text());combined=json.loads((P/'proposed'/ledger_path).read_text())
 record('all seven ledger document pins retained',all(combined['documents'].get(k)==v for k,v in ledger['documents'].items()))
 record('both ledger archive entries retained',all(x in combined['entries'] for x in ledger['entries']))
 with tempfile.TemporaryDirectory(prefix='ledger-resolver-check-',dir=P) as temp:
  root=Path(temp);shutil.copytree(P/'proposed',root,dirs_exist_ok=True)
  for document,sha in ledger['documents'].items():
   raw=(P/'inputs/ledger-v3'/document).read_bytes();record('ledger document exact '+document,hashlib.sha256(raw).hexdigest()==sha)
   target=root/document;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
   data=json.loads(raw)
   def has(node,path,expected):
    if isinstance(node,dict):return node.get(path)==expected or (node.get('path')==path and node.get('sha256')==expected) or any(has(v,path,expected) for v in node.values())
    return isinstance(node,list) and any(has(v,path,expected) for v in node)
   for e in ledger['entries']:
    if has(data,e['original_path'],e['sha256']):
     selected=checked_receipt(root,document,e['original_path'],e['sha256']);record('ledger normal receipt '+document+' '+e['original_path'],hashlib.sha256(selected.read_bytes()).hexdigest()==e['sha256'])
 result={'passed':True,'source_only':True,'checks':len(checks),'items':checks,'registry_models':len(json.loads((P/'proposed/catalogue/approved-models.json').read_text())['models']),'catalogue_models':len(json.loads((P/'proposed/catalogue/manifest.json').read_text())['models']),'profiles':len(m) if isinstance(m,dict) else len(parse_profile(P/'proposed/web/model-profile-data.mjs')),'receipt_pins_checked':len(audit['rows']),'temporary_resolver_removed':True,'material_compiled_package_browser_calls':0}
 (P/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='items'}))
if __name__=='__main__':check()
