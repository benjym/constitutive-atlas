"""Source-only receipt, crosswalk structure and rational-witness reproduction."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root,packet):
 for n,h in json.loads((packet/'manifest.json').read_text())['files'].items():assert sha(packet/n)==h,n
 for n,h in json.loads((packet/'reviewed-inputs.json').read_text())['files'].items():assert sha(root/n)==h,n
 receipt=json.loads((packet/'source-receipt.json').read_text());pdf=Path(receipt['private_source']['path'])
 source_check='unavailable; pinned receipt retained'
 if pdf.exists():assert sha(pdf)==receipt['private_source']['sha256'];source_check='exact hash verified'
 actual=subprocess.run([sys.executable,'-B',str(packet/'algebra.py')],check=True,capture_output=True,text=True)
 assert json.loads(actual.stdout)==json.loads((packet/'check-results.json').read_text())
 c=json.loads((packet/'schema-crosswalk-v03.json').read_text());f=c['formulation'];assert c['schema_version']=='0.3'and 'integration'not in c
 assert set(f)=={'time_dependence','equation_form','kinematics','frame','objective_rate','tensor_representation','stress_sign','strain_sign','inputs','stress'}
 assert f['time_dependence']=='strain_path'and f['equation_form']=='strain_path_rate'and f['objective_rate']=='none'
 assert c['initialization']['required_state']==['sigma']and c['state'][0]['semantics']['role']=='persistent'
 print(json.dumps({'manifest':True,'retained_inputs_unchanged':True,'source':source_check,'rational_witnesses_reproduced':True,'explicit_v03_crosswalk_structure':True,'complete_model_validation':False,'compiled_calls':0,'scientific_admission':False},sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();main(a.root,Path(__file__).resolve().parent)
