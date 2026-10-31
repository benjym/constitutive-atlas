"""Post-observation verification of three saved pre-integration rejections. No solver calls."""
import argparse,hashlib,json,pathlib

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('packet');ap.add_argument('--output');a=ap.parse_args();p=pathlib.Path(a.packet)
    read=lambda f:json.loads(f.read_text())
    freeze=read(p/'inputs/freeze.json')
    for name,h in freeze['files'].items():assert sha(p/'inputs'/name)==h,name
    audit=read(p/'source-audit/manifest.json')
    result={'kind':'post-observation saved-rejection assessment, not a replacement acceptance policy','material_calls':0,'freeze_sha256':sha(p/'inputs/freeze.json'),'requests':[],'source_comparison':'not evaluated: no material points','refinement':'not evaluated: no material points','experimental_errors':'not evaluated: no material points','scientific_admission':False}
    for r in read(p/'inputs/requests.json'):
        d=p/'observations'/r['id'];z=read(d/'stdout.json');receipt=read(d/'receipt.json')
        assert receipt['returncode']==1 and receipt['freeze_sha256']==sha(p/'inputs/freeze.json')
        assert sha(d/'stdout.json')==receipt['stdout_sha256'] and sha(d/'stderr.txt')==receipt['stderr_sha256']
        assert z['ok'] is False and z['points']==[] and z['message']=='control amplitude exceeds laboratory limit'
        for k in ['model','parameters','initial','protocol','steps','integration_settings']:assert z[k]==r[k],k
        assert z['loading']['controls_bits']==r['controls_bits'] and z['loading']['controls'][-1]==.25
        assert (d/'controls.txt').read_text()==','.join(r['controls_bits'])
        result['requests'].append({'id':r['id'],'requested_steps':r['steps'],'requested_target':.25,'returncode':1,'completed_points':0,'message':z['message']})
    text=json.dumps(result,indent=2)+'\n'
    if a.output:pathlib.Path(a.output).write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
