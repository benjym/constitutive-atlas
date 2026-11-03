"""Opt-in frozen corpus-only native runner. Default/--inspect executes no test code."""
from pathlib import Path
import hashlib,json,sys
from prepare_runners import prepare,HERE,ROOT
proof=prepare(False)
assert proof==json.loads((HERE/'runner-delta-proof.json').read_text()),'Frozen runner proof changed'
if '--execute' not in sys.argv:
 print(json.dumps(proof,indent=2));raise SystemExit(0)
if '--inspect' in sys.argv:raise SystemExit('Choose inspect or explicit execution, not both')
sys.argv.remove('--execute');entry=next(x for x in proof['runners'] if x['kind']=='native');source=(HERE/entry['snapshot']).read_text();original=ROOT/entry['original_path']
# Preserve original __file__, root-relative fixture paths, unittest discovery and all gate code.
sys.path.insert(0,str(ROOT));globals()['__file__']=str(original)
exec(compile(source,str(original),'exec'),globals(),globals())
