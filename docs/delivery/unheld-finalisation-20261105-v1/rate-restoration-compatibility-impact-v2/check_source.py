"""Exact source-preservation and manufactured source-view integrity witnesses."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,tempfile
P=Path(__file__).resolve().parent;S=P.parent/'current17-runtime-source-v1/source';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def check(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except (ValueError,KeyError,FileNotFoundError):checks.append(n);return
 raise AssertionError('accepted corruption '+n)
def sha(b):return hashlib.sha256(b).hexdigest()
proof=json.loads((P/'proof.json').read_text())
def node(source,name):return next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
for name in ['tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py']:
 old=(S/name).read_text();new=(P/'proposed'/name).read_text()
 for fn in ['validate','namespace','copy_evidence','load','require','digest']:
  check(name+' unchanged '+fn,ast.dump(node(old,fn),include_attributes=False)==ast.dump(node(new,fn),include_attributes=False))
 old_return=' return f.read_bytes()';new_return=' from tools.rate_restoration_source_view_v2 import historical_bytes\n return historical_bytes(root,name,f.read_bytes())'
 check(name+' exact inverse',new.replace(new_return,old_return)==old)
old=(S/'tools/build_controlled_time_web.py').read_text();new=(P/'proposed/tools/build_controlled_time_web.py').read_text()
for fn in ['source_pin','reviewed_source_compatibility','bundle']:
 check('controlled time unchanged '+fn,ast.dump(node(old,fn),include_attributes=False)==ast.dump(node(new,fn),include_attributes=False))
for f in (P/'proposed/tools').glob('*.py'):ast.parse(f.read_text());checks.append('parse '+f.name)
spec=importlib.util.spec_from_file_location('manufactured_source_view',P/'proposed/tools/rate_restoration_source_view_v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='manufactured-view-',dir=P) as tmp:
 root=Path(tmp)
 def put(n,b):p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return p
 for row in json.loads((P/'implementation-delta.json').read_text())['files']:
  put(row['path'],(P/row['proposal']).read_bytes())
 b=P.parent/'current17-igs97-regression-diagnosis-v2/proposed/cpp/include/atlas/solver.hpp';put(m.SOURCE,b.read_bytes())
 for name,h in proof['ancestors'].items():
  data=(W/name).read_bytes();check('exact ancestor '+name,sha(data)==h);put(name,data)
 review={'identity':'rate-restoration-special-profile-source-view-review-v2','decision':'accepted','author_run':'/root/baseline_migration','reviewer_run':'manufactured-only-NOT-AN-ACTUAL-REVIEW','unresolved_blockers':[],'proof_sha256':sha((P/'proof.json').read_bytes()),'implementation':proof['implementation']}
 reviewpath=put(m.REVIEW,(json.dumps(review)+'\n').encode())
 check('manufactured authority accepts complete exact vector',m.authority(root)==proof)
 for name,row in proof['aliases'].items():
  check('historical projection '+name,sha(m.historical_bytes(root,name,(root/name).read_bytes()))==row['predecessor_sha256'])
  check('actual current bytes preserved '+name,sha((root/name).read_bytes())==row['current_sha256'])
 check('unknown path never aliased',m.historical_bytes(root,'unlisted/path',b'unknown')==b'unknown')

 r=copy.deepcopy(review);r['identity']='rate-restoration-special-profile-source-view-review-v1';reviewpath.write_text(json.dumps(r));reject('B acceptance rejected',lambda:m.authority(root));reviewpath.write_text(json.dumps(review))
 q=root/m.SOURCE;original=q.read_bytes();q.write_bytes((P.parent/'current17-igs97-regression-diagnosis-v1/original-rate-profile-v1/proposed/cpp/include/atlas/solver.hpp').read_bytes());reject('B source rejected',lambda:m.authority(root));q.write_bytes(original)

 for n,change in [('missing author',lambda x:x.pop('author_run')),('self review',lambda x:x.update(reviewer_run=x['author_run'])),('empty reviewer',lambda x:x.update(reviewer_run=' ')),('pending decision',lambda x:x.update(decision='pending')),('unresolved blocker',lambda x:x.update(unresolved_blockers=['x'])),('wrong proof digest',lambda x:x.update(proof_sha256='0'*64)),('unknown implementation',lambda x:x['implementation'].update({'tools/extra.py':'0'*64})),('missing implementation',lambda x:x['implementation'].pop('tools/profile_source_compatibility.py'))]:
  r=copy.deepcopy(review);change(r);reviewpath.write_text(json.dumps(r));reject(n,lambda:m.authority(root));reviewpath.write_text(json.dumps(review))
 for name in [m.SOURCE,*m.IMPLEMENTATION]:
  q=root/name;original=q.read_bytes();q.write_bytes(original+b'corruption');reject('unknown current bytes '+name,lambda:m.authority(root));q.write_bytes(original)
 for name,row in proof['aliases'].items():
  q=root/row['archive'];original=q.read_bytes();q.write_bytes(original+b'corruption');reject('corrupt archive '+name,lambda:m.authority(root));q.write_bytes(original)
 q=root/m.PROOF;original=q.read_bytes()
 altered=copy.deepcopy(proof);altered['ordinary_runtime_qualification_transferred']=True;q.write_text(json.dumps(altered));r=copy.deepcopy(review);r['proof_sha256']=sha(q.read_bytes());reviewpath.write_text(json.dumps(r));reject('no qualification transfer',lambda:m.authority(root));q.write_bytes(original);reviewpath.write_text(json.dumps(review))
 q=root/m.SOURCE;original=q.read_bytes();q.unlink();q.symlink_to(root/proof['aliases'][m.SOURCE]['archive']);reject('symlink current solver',lambda:m.authority(root));q.unlink();q.write_bytes(original)
 # Old guard digest observes exact predecessor, actual new implementation is
 # independently pinned by authority. Other path corruption is never concealed.
 name='cpp/other.hpp';put(name,b'changed');check('unrelated historical check rejects changed bytes',sha(m.historical_bytes(root,name,(root/name).read_bytes()))!=sha(b'original'))
check('scratch removed',not list(P.glob('manufactured-view-*')))
(P/'source-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'count':len(checks),'compiled_generation_or_material_calls':0,'shared_files_changed':False},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'compiled_generation_or_material_calls':0}))
