"""Three serial, single-attempt native calls. Preserve raw output before interpretation."""
import argparse, datetime, hashlib, json, pathlib, subprocess

def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    base=pathlib.Path(__file__).resolve().parent;out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=False)
    freeze=json.loads((base/'freeze.json').read_text())
    for name,h in freeze['files'].items(): assert sha(base/name)==h,name
    pins=json.loads((base/'source-pins.json').read_text());exe=pins['artifact']['path'];assert sha(exe)==pins['artifact']['sha256']
    for r in json.loads((base/'requests.json').read_text()):
        d=out/r['id'];d.mkdir();wire=d/'controls.txt';wire.write_text(','.join(r['controls_bits']))
        cmd=[exe,'--mode','run-research-controls','--model',r['model'],'--parameters',','.join(map(repr,r['parameters'])),'--initial',','.join(map(repr,r['initial'])),'--protocol',str(r['protocol']),'--integration-settings',r['settings_csv'],'--laboratory-controls-file',str(wire)]
        receipt={'command':cmd,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'artifact_sha256':sha(exe),'freeze_sha256':sha(base/'freeze.json')};dump(d/'receipt.json',receipt)
        with (d/'stdout.json').open('wb') as stdout,(d/'stderr.txt').open('wb') as stderr:
            p=subprocess.run(cmd,stdout=stdout,stderr=stderr,check=False)
        receipt.update(returncode=p.returncode,finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),stdout_sha256=sha(d/'stdout.json'),stderr_sha256=sha(d/'stderr.txt'));dump(d/'receipt.json',receipt)
        print(r['id'],p.returncode,flush=True)
if __name__=='__main__':main()
