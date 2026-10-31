"""Retain source-bound opaque transport before the separate exact assessor."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def collect(role):
 freeze=HERE/'prospective-freeze.json';f=json.loads(freeze.read_text());buildpath=HERE/(role+'-build.json');build=json.loads(buildpath.read_text());rawpath=HERE/(role+'-raw.json');out=HERE/(role+'-execution.json');assert not rawpath.exists()and not out.exists()
 for name,pin in f['files'].items():assert sha(ROOT/name)==pin,name
 for a in build['artifacts'].values():assert sha(Path(a['path']))==a['sha256']
 if role=='native':
  argv=[build['artifacts']['native']['path']];text=(HERE/'requests.tsv').read_text();p=subprocess.run(argv,input=text,text=True,capture_output=True,timeout=60);raw={'argv':argv,'stdin':text,'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode};rawpath.write_text(json.dumps(raw)+'\n')
 else:
  argv=['node',str(HERE/'collect_wasm.mjs'),build['artifacts']['loader']['path'],str(HERE/'requests.tsv'),str(rawpath)];p=subprocess.run(argv,text=True,capture_output=True,timeout=60)
 out.write_text(json.dumps({'role':role,'argv':argv,'freeze_sha256':sha(freeze),'build_sha256':sha(buildpath),'raw_sha256':sha(rawpath)if rawpath.exists()else None,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
 for name,pin in f['files'].items():assert sha(ROOT/name)==pin,name
 for a in build['artifacts'].values():assert sha(Path(a['path']))==a['sha256']
 assert p.returncode==0,'failed transport retained'
if __name__=='__main__':p=argparse.ArgumentParser();p.add_argument('role',choices=('native','wasm'));collect(p.parse_args().role)
