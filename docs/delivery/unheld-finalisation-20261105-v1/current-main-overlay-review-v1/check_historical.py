"""Independent source-only historical/current approval selection witnesses."""
from pathlib import Path
import argparse,ast,copy,hashlib,json,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
checks=[]
def yes(ok,name):
 if not ok:raise AssertionError(name)
 checks.append(name)
def fn(tree,name):return next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name==name)
def normalized(node):return ast.dump(node,include_attributes=False)
def extract(node,scope):
 class RemoveImports(ast.NodeTransformer):
  def visit_ImportFrom(self,node):return ast.Pass()
  def visit_Import(self,node):return ast.Pass()
 out=ast.Module(body=[RemoveImports().visit(copy.deepcopy(node))],type_ignores=[]);exec(compile(ast.fix_missing_locations(out),'<owned-source-fixture>','exec'),scope);return scope[node.name]
def main():
 args=argparse.ArgumentParser();args.add_argument('--proposal',type=Path,required=True);a=args.parse_args()
 current=ast.parse((Path('/private/tmp/atlas-baseline-delivery-20261105/source/atlas/research.py')).read_text());proposal=ast.parse(a.proposal.read_text())
 accepted=ast.parse((ROOT/'docs/delivery/unheld-finalisation-20261102-v1/baseline-integration-v2/proposed/atlas/research.py').read_text())
 yes(normalized(fn(proposal,'approved_definitions'))==normalized(fn(accepted,'approved_definitions')),'exact previously accepted historical/current definition resolver AST')
 # Every other current source declaration remains unchanged, apart from the two explicitly scoped functions.
 strip=lambda t:ast.Module(body=[n for n in t.body if not(isinstance(n,ast.FunctionDef)and n.name in ['approved_definitions','export_database'])],type_ignores=[])
 yes(normalized(strip(current))==normalized(strip(proposal)),'all other current research declarations preserved')
 old=fn(current,'export_database');new=fn(proposal,'export_database');baseline=fn(accepted,'export_database')
 class NormalizeProjection(ast.NodeTransformer):
  def visit_If(self,node):
   if isinstance(node.test,ast.BoolOp)and 'agent_authority'in ast.unparse(node.test):
    # Compare all surrounding export logic unchanged, then separately require exact accepted complete projection block.
    return ast.Expr(value=ast.Constant(value='SCOPED_REVIEW_PROJECTION'))
   return self.generic_visit(node)
 yes(normalized(NormalizeProjection().visit(copy.deepcopy(old)))==normalized(NormalizeProjection().visit(copy.deepcopy(new))),'all current export logic outside scoped historical review projection preserved')
 getblock=lambda t:next(n for n in ast.walk(t)if isinstance(n,ast.If)and isinstance(n.test,ast.BoolOp)and 'agent_authority'in ast.unparse(n.test))
 yes(normalized(getblock(new))==normalized(getblock(baseline)),'exact accepted failclosed historical review projection block')
 evidence=ast.parse((ROOT/'atlas/evidence.py').read_text());checked=fn(evidence,'checked_receipt')
 class ValidationError(ValueError):pass
 with tempfile.TemporaryDirectory(prefix='owned-history-',dir=P)as temporary:
  root=Path(temporary);(root/'models').mkdir();(root/'catalogue').mkdir()
  h=lambda b:hashlib.sha256(b).hexdigest()
  oldbytes=json.dumps({'id':'baseline','version':'old'}).encode();newbytes=json.dumps({'id':'baseline','version':'new'}).encode()
  def row(identity,mid,data):return{'id':identity,'model_id':mid,'status':'approved','definition':{'path':'models/'+mid+'.json','sha256':h(data)}}
  original=[row('old','baseline',oldbytes),row('new','baseline',newbytes)]
  for mid in ['s-clay1','vibe-current']:
   data=json.dumps({'id':mid,'version':'current'}).encode();(root/'models'/ (mid+'.json')).write_bytes(data);original.append(row(mid,mid,data))
  registry=root/'catalogue/approved-models.json';archive=root/'catalogue/source-snapshots'/h(oldbytes)/'models/baseline.json';archive.parent.mkdir(parents=True);archive.write_bytes(oldbytes)
  sidecar=root/'catalogue/source-archive-map.json';canonical=root/'models/baseline.json'
  def reset(rows=None):
   canonical.unlink(missing_ok=True);canonical.write_bytes(newbytes);archive.write_bytes(oldbytes)
   registry.write_text(json.dumps({'models':original if rows is None else rows}));sidecar.write_text(json.dumps({'version':'immutable-source-archive-map-0.1','documents':{'catalogue/approved-models.json':h(registry.read_bytes())},'entries':[{'original_path':'models/baseline.json','sha256':h(oldbytes),'archived_path':archive.relative_to(root).as_posix()}]}))
  scope={'Path':Path,'json':json,'hashlib':hashlib,'ValidationError':ValidationError,'ROOT':root,'load':lambda p:json.loads(p.read_bytes()),'_sha':lambda p:h(p.read_bytes())}
  scope['checked_receipt']=extract(checked,scope);resolver=extract(fn(proposal,'approved_definitions'),scope)
  def rejects(name):
   try:resolver()
   except (ValidationError,ValueError,OSError):checks.append(name);return
   raise AssertionError('Accepted corruption: '+name)
  reset();definitions,records=resolver();yes(set(definitions)=={'baseline','s-clay1','vibe-current'}and definitions['baseline']['version']=='new'and len(records)==4,'historical record retained without approving oldbytes; current baseline/SCLAY/VIBE exact')
  reset();archive.unlink();rejects('missing historical archive rejects')
  reset();archive.write_bytes(b'corrupt');rejects('historical archive SHA drift rejects')
  reset();mapping=json.loads(sidecar.read_bytes());mapping['documents']['catalogue/approved-models.json']='0'*64;sidecar.write_text(json.dumps(mapping));rejects('registry document pin drift rejects')
  reset();mapping=json.loads(sidecar.read_bytes());mapping['entries'][0]['archived_path']='models/baseline.json';sidecar.write_text(json.dumps(mapping));rejects('nonintrinsic archive route rejects')
  reset();sidecar.unlink();rejects('missing archive map cannot silently approve historical bytes')
  reset();rows=copy.deepcopy(original);rows[0]['model_id']='wrong';reset(rows);rejects('historical modelID mismatch rejects')
  reset();rows=copy.deepcopy(original);rows[1]['id']='old';reset(rows);rejects('duplicate approval identity rejects')
  reset();rows=copy.deepcopy(original);rows[0]['definition']['path']='../outside.json';reset(rows);rejects('approval path traversal rejects')
  reset();rows=copy.deepcopy(original);rows[0]['definition']['path']=str(root/'models/baseline.json');reset(rows);rejects('absolute approval path rejects')
  reset();canonical.write_bytes(b'{}');rejects('current model hash drift cannot inherit historical approval')
  reset();outside=root/'outside.json';outside.write_bytes(newbytes);canonical.unlink();canonical.symlink_to(outside);rejects('canonical symlink outside model directory rejects')
  reset();rows=copy.deepcopy(original);pending=row('pending','pending',b'absent');pending['status']='pending';rows.append(pending);reset(rows);defs,records=resolver();yes(len(defs)==3 and len(records)==4,'pending absent definition not selected')
 yes(not list(P.glob('owned-history-*')),'owned fixtures fully cleaned')
 print(json.dumps({'identity':'current-main-overlay-independent-historical-source-witnesses-v1','status':'PASS','checks':len(checks),'names':checks,'numerical_model_or_module_calls':0,'fixture_cleanup':'complete'},indent=2))
if __name__=='__main__':main()
