from pathlib import Path
import json,copy
p=Path(__file__).resolve().parent;x=json.loads((p/'default-run.json').read_text())
a=copy.deepcopy(x);a['identity']['definition_sha256']='0'*64;(p/'bad-identity.json').write_text(json.dumps(a))
a=copy.deepcopy(x);a['request']['context']['state'].pop('e');(p/'bad-context.json').write_text(json.dumps(a))
a=copy.deepcopy(x);a['result']['points'][-1]['context']['state']['eta']+=0.01;(p/'bad-result.json').write_text(json.dumps(a))
print('Prepared identity, missing-state and result tamper negatives from actual live export')
