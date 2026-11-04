"""Source-only derivation. No model import, generation or executable invocation."""
from pathlib import Path
import ast,hashlib
P=Path(__file__).resolve().parent
OLD=P.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5'
s=(OLD/'collector.py').read_text()
start=s.index('def source_freeze(');end=s.index('class Transport:')
s=s[:start]+(P/'reuse-provenance.py.txt').read_text()+'\n\n'+s[end:]
start=s.index('def collect(')
s=s[:start]+(P/'per-call-bindings.py.txt').read_text()+'\n\n'+s[start:]
s=s.replace("assert f['identity']=='baseline-five-prospective-execution-freeze-v1'","assert f['identity']=='baseline-five-current17-reused-execution-freeze-v1'")
s=s[:s.index('def main():')]+'''def main():
 if sys.flags.optimize:raise RuntimeError('qualification requires assertions enabled')
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
 freeze_parser=sub.add_parser('reuse-freeze')
 for name in ['repo','handoff','review','output']:freeze_parser.add_argument('--'+name,type=Path,required=True)
 for name in ['handoff-sha256','review-sha256']:freeze_parser.add_argument('--'+name,required=True)
 c=sub.add_parser('collect');c.add_argument('--freeze',type=Path,required=True);c.add_argument('--backend',choices=['native','wasm'],required=True);c.add_argument('--output',type=Path,required=True)
 pair=sub.add_parser('assess-pair')
 for name in ['native','wasm','output']:pair.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();{'reuse-freeze':reuse_freeze,'collect':collect,'assess-pair':assess_pair}[a.action](a)
if __name__=='__main__':main()
'''
(P/'collector-reuse.py').write_text(s)
for name in ['policy.json','wasm-cli.mjs']:(P/name).write_bytes((OLD/name).read_bytes())
