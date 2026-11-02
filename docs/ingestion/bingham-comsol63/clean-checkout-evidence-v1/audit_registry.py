"""All registry definitions/reviews/supporting paths, source-only comparison."""
from pathlib import Path
import hashlib,json,sys
R=Path(sys.argv[1]).resolve();sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
rows=[];reads={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for a in json.loads((R/'catalogue/approved-models.json').read_text())['models']:
 if a.get('status')!='approved':continue
 review=a.get('review',{});ctx=review.get('path') if review.get('kind')=='agent-model-review' else None
 items=[('definition',a['definition']),*[(k,{'path':v}) for k,v in review.items() if k in ['path','decisions'] and isinstance(v,str)],*[('supporting',x) for x in a.get('supporting_files',[])]]
 if isinstance(a.get('dossier'),str):items.append(('dossier',{'path':a['dossier']}))
 for role,item in items:
  n=item['path'];h=item.get('sha256');record={'approval':a['id'],'role':role,'path':n,'expected':h}
  try:
   p=checked_receipt(R,ctx,n,h) if role=='supporting' and ctx else R/n
   assert not Path(n).is_absolute() and '..' not in Path(n).parts and p.resolve().is_relative_to(R);actual=sha(p);assert h is None or actual==h
   record.update(passed=True,resolved=p.relative_to(R).as_posix(),sha256=actual);reads[p.relative_to(R).as_posix()]=actual
  except Exception as e:record.update(passed=False,error_type=type(e).__name__,error=str(e).replace(str(R),'<ROOT>'))
  rows.append(record)
report={'passed':all(x['passed'] for x in rows),'approval_count':len({x['approval'] for x in rows}),'path_checks':len(rows),'inputs':reads,'records':rows,'compiler_material_calls':0};Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['inputs','records']},indent=2));sys.exit(0 if report['passed'] else 1)
