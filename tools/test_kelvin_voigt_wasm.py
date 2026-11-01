"""Run the frozen Kelvin–Voigt requests through the common Wasm ABI."""
import argparse,json,subprocess
from pathlib import Path
from test_kelvin_voigt_native import BASE,ROOT,study

def main():
    p=argparse.ArgumentParser();p.add_argument('--module',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    study.verify_freeze()
    if a.output.exists():raise ValueError('Refuse to replace qualification evidence')
    a.output.mkdir(parents=True)
    subprocess.run(['node',str(BASE/'collect_wasm.mjs'),str(a.module.resolve()),str(BASE/'cases.json'),str(a.output/'raw.json')],check=True,timeout=1800)
    report=study.assess(json.loads((BASE/'cases.json').read_text())['cases'],json.loads((a.output/'raw.json').read_text()))
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
