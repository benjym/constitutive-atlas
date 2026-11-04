from pathlib import Path
import ast, hashlib, json
P=Path(__file__).resolve().parent
BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
OLD=P.parents[2]/'unheld-finalisation-20261102-v1/baseline-integration-v2/proposed/atlas/research.py'
def function(source,name):
 node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==name)
 return '\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
base=(BASE/'atlas/research.py').read_text(); old=OLD.read_text()
new=base.replace(function(base,'approved_definitions'),function(old,'approved_definitions'))
a='''                    from .agent_review import approval_entry
                    expected = approval_entry(file, root=ROOT)
                    if any(approval.get(key) != value for key, value in expected.items()):'''
b='''                    from .review_export import collect
                    projected, _, _ = collect(ROOT, {approval['model_id']})
                    matching = [row for row in projected if row['record_path'] == review['path']
                                and row['registered_approval_id'] == approval['id']]
                    if len(matching) != 1 or matching[0]['status'] != 'accepted':'''
assert new.count(a)==1
new=new.replace(a,b)
out=P/'proposed/atlas/research.py';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(new)
assert ast.parse(new)
(P/'base.json').write_text(json.dumps({'path':'atlas/research.py','preimage_sha256':hashlib.sha256(base.encode()).hexdigest(),'sha256':hashlib.sha256(new.encode()).hexdigest()},indent=2)+'\n')
print('Prepared exact two bounded research.py changes')
