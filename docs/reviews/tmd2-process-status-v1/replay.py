"""Replay saved process-status witness; never invoke a solver or download data."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.benchmark_tmd2 import normalize, verify_process_observations
SOURCE=ROOT/'docs/benchmarks/kfs-tmd2-research-range-v1'

def main():
    with tempfile.TemporaryDirectory(prefix='tmd2-process-replay-') as directory:
        out=Path(directory)
        shutil.copytree(SOURCE/'inputs',out/'inputs')
        shutil.copytree(SOURCE/'observations',out/'observations')
        assert verify_process_observations(out/'inputs',out/'observations')==['tmd2-400','tmd2-800','tmd2-1600']
        data=out/'KFS-TMD2.json'
        data.write_text(json.dumps(normalize(ROOT/'data/raw/KFS-TMD1-5.zip'),indent=2,allow_nan=False)+'\n')
        pins=json.loads((out/'inputs/source-pins.json').read_text())
        pins['data']['sha256']=hashlib.sha256(data.read_bytes()).hexdigest()
        (out/'inputs/source-pins.json').write_text(json.dumps(pins))
        path=out/'observations/tmd2-400/receipt.json'
        receipt=json.loads(path.read_text());receipt['returncode']=23;path.write_text(json.dumps(receipt))
        result=subprocess.run([sys.executable,str(out/'inputs/assess.py'),'--observations',str(out/'observations'),'--data',str(data),'--output',str(out/'results')],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        summary=json.loads((out/'results/summary.json').read_text())
        assert summary['source_pass'] and summary['refinement_pass']
        assert summary['paths'][0]['returncode']==23
        try: verify_process_observations(out/'inputs',out/'observations')
        except ValueError as exc:
            assert 'integer zero process returncode' in str(exc)
        else: raise AssertionError('Nonzero process was accepted')
        print('PASS: original saved frame accepted; old exit23 false pass reproduced; revised guard rejects; no backend calls.')

if __name__=='__main__':main()
