"""Saved-only dispatch of exact existing CI preset/reference gates before review."""
import argparse,ast,hashlib,json,os,sys,textwrap
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();ROOT=Path(os.environ['ATLAS_QUALIFICATION_SOURCE']).resolve();output=Path(os.environ['ATLAS_QUALIFICATION_OUTPUT']).resolve();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
sys.path.insert(0,str(ROOT));from tests.test_maxwell import assess
raw=(ROOT/'tools/check_maxwell_ci.py').read_text();start=raw.index("    presets=json.loads((output/'presets.json').read_text())");end=raw.index('    if source_manifest()!=before',start);block=textwrap.dedent(raw[start:end]);tree=ast.parse(raw);assignment=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PRESETS'for t in n.targets));PRESETS=ast.literal_eval(assignment.value);cases=json.loads((ROOT/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text())['cases']
exec(compile(block,'exact-frozen-Maxwell-preset-assessment','exec'),globals());report={'passed':True,'preset_errors_Pa':preset_errors,'cases':len(presets),'gate_source_sha256':hashlib.sha256(raw.encode()).hexdigest(),'gate_block_sha256':hashlib.sha256(block.encode()).hexdigest(),'scope':'Saved raw preset data only; no package, build review or approval claim'};a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
