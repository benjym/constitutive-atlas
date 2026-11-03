"""Pure exact reversal: preserve every previous validator assertion and test."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
s=(R/'tools/test_web_package.mjs').read_text()
a=s.index("import {createHash} from 'node:crypto';\n");b=s.index('export function validatePackage(directory){',a)
s=s[:a]+s[b:]
s=s.replace('{readFileSync,writeFileSync,existsSync,readdirSync}','{readFileSync,writeFileSync,existsSync}')
s=s.replace(" const separate=validateControlledTimeMembership(directory,catalogue.models,ids);\n assert.deepEqual(catalogue.models.filter(m=>m.executable&&!separate.includes(m.id)).map(m=>m.id).sort(),[...ids].sort(),'Executable catalogue differs from runtime');"," assert.deepEqual(catalogue.models.filter(m=>m.executable).map(m=>m.id).sort(),[...ids].sort(),'Executable catalogue differs from runtime');")
assert s.encode()==(P/'preimages/tools/test_web_package.mjs').read_bytes()
t=(R/'tests/test_web_package.mjs').read_text().split('\n// Pure source-backed sealing fixture:',1)[0]
t=t.replace('{mkdtempSync,mkdirSync,writeFileSync,rmSync,readFileSync,readdirSync,unlinkSync}','{mkdtempSync,mkdirSync,writeFileSync,rmSync}').replace('{validatePackage,validateControlledTimeMembership}','{validatePackage}')
assert t.encode()==(P/'preimages/tests/test_web_package.mjs').read_bytes()
unchanged=R/'tools/test_controlled_time_package.mjs'
report={'kind':'package-membership-exact-reversal-v1','validator_original_assertions_preserved':True,'all_original_tests_preserved':True,'actual_separate_replay_gate_unchanged':{'path':str(unchanged.relative_to(R)),'sha256':hashlib.sha256(unchanged.read_bytes()).hexdigest()},'engine_module_loads':0}
(P/'projection-proof-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
