"""Copy only exact previously reviewed project artifact bytes; never execute them."""
import hashlib,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;SOURCE=Path('/private/tmp/atlas-control-partition-support-v1/source');OUT=SOURCE.parent/'retained-assets'
sys.dont_write_bytecode=True;sys.path.insert(0,str(SOURCE))
def digest(b):return hashlib.sha256(b).hexdigest()
def install(p,b):
 if p.exists():assert p.read_bytes()==b
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
report={'compiled_calls':0,'builds':0,'new_artifact_claim':False,'hill':[],'lade':[],'gaps':[]}
r=json.loads((SOURCE/'docs/ingestion/hill-abaqus2025/execution-v1/build-receipt.json').read_text())
for name,h in r['artifacts'].items():
 p=Path(name)
 if not p.is_file():report['gaps'].append({'profile':'hill','path':name,'expected':h,'reason':'Original exact receipt path unavailable'});continue
 b=p.read_bytes();assert digest(b)==h,name
 relative='generated/models.json'if name.endswith('/generated/models.json')else p.name
 target=OUT/'hill'/relative;install(target,b);report['hill'].append({'source':name,'retained_path':str(target),'sha256':h,'identity':'historical reviewed build only'})
from tools.provision_implicit_path_assets import authorized_index,selected_bytes,ARCHIVE
index,indexhash=authorized_index();selected=selected_bytes((SOURCE/ARCHIVE).read_bytes(),index['files'])
for name,b in selected.items():
 target=OUT/'lade'/name;install(target,b);report['lade'].append({'retained_path':str(target),'sha256':digest(b),'identity':'historical E5-bound qualified asset archive; no fresh common-runtime substitution'})
report['lade_index_sha256']=indexhash
(D/'retained-assets.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'hill_retained':len(report['hill']),'lade_retained':len(report['lade']),'gaps':len(report['gaps'])}))
