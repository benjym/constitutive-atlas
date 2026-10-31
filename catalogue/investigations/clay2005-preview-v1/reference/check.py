"""Reproduce own frozen source-only references. No Atlas imports/evaluation."""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from decimal import Decimal as D,localcontext

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root,packet):
 manifest=json.loads((packet/'manifest.json').read_text())
 for n,s in manifest['files'].items():assert sha(packet/n)==s,n
 with tempfile.TemporaryDirectory(prefix='atlas-isotropic-reference-')as td:
  tmp=Path(td);f=tmp/'prospective-freeze.json';r=tmp/'references.json'
  subprocess.run([sys.executable,'-B',str(packet/'freeze.py'),'--root',str(root),'--output',str(f)],check=True,capture_output=True,text=True)
  assert f.read_bytes()==(packet/f.name).read_bytes()
  subprocess.run([sys.executable,'-B',str(packet/'reference.py'),'--root',str(root),'--packet',str(tmp),'--output',str(r)],check=True,capture_output=True,text=True)
  result=json.loads(r.read_text());assert result==json.loads((packet/r.name).read_text());assert result['all_checks_passed']
  assert len(result['precision_results']['160']['cases'])==5
  for row in result['precision_results']['160']['cases']:
   p,e=D(row['p']),D(row['e']);assert p>0 and e>=0
   assert row['state'][:3]==[row['p']]*3 and all(D(x)==0 for x in row['state'][3:6])
   with localcontext()as ctx:
    ctx.prec=160;assert D(row['budget_stress_absolute_Pa'])==D('1e-5')*max(D(1),p)
   assert D(row['budget_void_absolute'])==D('1e-6')
 print(json.dumps({'freeze_reproduced':True,'references_reproduced':True,'manifest_passed':True,'five_cases':True,'all_checks_passed':True,'compiled_calls':0,'Atlas_imports':False},sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();main(a.root,Path(__file__).resolve().parent)
