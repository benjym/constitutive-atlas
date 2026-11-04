"""Pure prospective argv construction; does not read source/tool or execute anything."""
from pathlib import Path
P=Path(__file__).resolve().parent
COLLECTOR=P.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5/collector.py'
SOURCE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
WORK=Path('/private/tmp/atlas-baseline-current16-qualification-build-v1')
ROLE_KEYS={'cmake','native_cxx','emcmake','emcc'}

def source_freeze_argv(python,node,tools):
 assert Path(python).is_absolute() and Path(node).is_absolute() and set(tools)==ROLE_KEYS
 assert all(Path(x).is_absolute() for x in tools.values())
 return [python,'-B',str(COLLECTOR),'source-freeze','--repo',str(SOURCE),'--node',node,*[v for key in sorted(tools) for v in ('--tool',key+'='+tools[key])],'--output',str(P/'source-freeze-v1.json')]

def phase_argv(pre):
 assert pre['repo']==str(SOURCE) and pre['compiled_observations'] is False
 python=pre['python']['path'];node=pre['node']['path'];assert Path(python).is_absolute() and Path(node).is_absolute()
 freeze=P/'execution-freeze-v1.json';build=P/'actual-build-v1/receipt.json'
 return {
  'build':[python,'-B',str(P/'build.py'),'--source-freeze',str(P/'source-freeze-v1.json'),'--work',str(WORK),'--slot-handoff','unheld-baseline-five-native-then-wasm-v1'],
  'freeze':[python,'-B',str(COLLECTOR),'freeze','--repo',str(SOURCE),'--native',str(WORK/'native/atlas_solver'),'--module',str(WORK/'wasm/atlas.js'),'--wasm',str(WORK/'wasm/atlas.wasm'),'--node',node,'--build-receipt',str(build),'--source-freeze',str(P/'source-freeze-v1.json'),'--output',str(freeze)],
  'native':[python,'-B',str(COLLECTOR),'collect','--freeze',str(freeze),'--backend','native','--output',str(P/'native-v1')],
  'wasm':[python,'-B',str(COLLECTOR),'collect','--freeze',str(freeze),'--backend','wasm','--output',str(P/'wasm-v1')],
  'pair':[python,'-B',str(COLLECTOR),'assess-pair','--native',str(P/'native-v1'),'--wasm',str(P/'wasm-v1'),'--output',str(P/'pair-v1.json')]
 }
