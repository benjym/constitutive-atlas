"""Verify only source/context receipts, crosswalk structure and own exact fixtures."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root,packet):
 for n,h in json.loads((packet/'manifest.json').read_text())['files'].items():assert sha(packet/n)==h,n
 for n,h in json.loads((packet/'reviewed-inputs.json').read_text())['files'].items():assert sha(root/n)==h,n
 s=json.loads((packet/'source-receipt.json').read_text())['private_file'];p=Path(s['path']);source='unavailable; receipt retained'
 if p.exists():assert sha(p)==s['sha256'];source='exact hash verified'
 a=subprocess.run([sys.executable,'-B',str(packet/'check_fixtures.py'),'--check'],check=True,capture_output=True,text=True)
 c=json.loads((packet/'schema-crosswalk-v03.json').read_text());assert c['schema_version']=='0.3'and 'integration'not in c
 f=c['formulation'];assert set(f)=={'time_dependence','equation_form','kinematics','frame','objective_rate','tensor_representation','stress_sign','strain_sign','inputs','stress'}
 assert f['time_dependence']=='strain_path'and f['equation_form']=='incremental_residual'and f['stress']['scope']=='total'
 assert c['initialization']['required_state']==[x['name']for x in c['state']]==['sigma','ep']
 assert all(x['semantics']['role']=='persistent'for x in c['state'])
 print(json.dumps({'manifest':True,'retained_context_hashes':True,'source':source,'independent_fixture_reproduction':True,'explicit_v03_crosswalk_structure':True,'model_transcription_or_validation':False,'compiled_calls':0,'Atlas_imports':False,'scientific_admission':False},sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();main(a.root,Path(__file__).resolve().parent)
