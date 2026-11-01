#!/usr/bin/env python3
"""Read-only exact receipt/replay and schema-fragment verification.
Only validates the schema keywords used by the selected fragments, not a model.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def fragment(value,schema):
    supported={'type','required','properties','additionalProperties','const','enum','pattern','items','description','minLength'}
    assert set(schema)<=supported, ('unsupported schema keywords',set(schema)-supported)
    if 'const' in schema:assert value==schema['const']
    if 'enum' in schema:assert value in schema['enum']
    if 'type' in schema:assert isinstance(value,{'object':dict,'array':list,'string':str}[schema['type']])
    if isinstance(value,dict):
        assert set(schema.get('required',[]))<=set(value)
        props=schema.get('properties',{})
        if schema.get('additionalProperties') is False:assert set(value)<=set(props)
        for key,item in value.items():
            if key in props:fragment(item,props[key])
    if 'minLength' in schema:assert len(value)>=schema['minLength']
    if 'pattern' in schema:assert re.search(schema['pattern'],value)
    if 'items' in schema:
        for item in value:fragment(item,schema['items'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');args=parser.parse_args()
    manifest=json.loads((HERE/'manifest.json').read_text())
    for name,digest in manifest['files'].items():assert sha(HERE/name)==digest,name
    cw=json.loads((HERE/'crosswalk.json').read_text())
    schema_path=ROOT/'schemas/model-v0.3.schema.json'
    assert sha(schema_path)==cw['target_schema_sha256'],'schema changed; reassess crosswalk'
    schema=json.loads(schema_path.read_text())
    profiles=schema['oneOf']
    profile=next(p for p in profiles if p['properties'].get('formulation',{}).get('properties',{}).get('equation_form',{}).get('const')=='strain_path_rate')
    fragment(cw['formulation'],profile['properties']['formulation'])
    fragment(cw['initialization'],profile['properties']['initialization'])
    assert cw['schema_version']=='0.3' and 'integration' not in cw
    assert set(cw['initialization']['required_state'])=={s['name'] for s in cw['state_proposal']}
    assert cw['formulation']['stress']['name']=='sigma'
    for state in cw['state_proposal']:
        fragment(state['semantics'],profile['properties']['state']['items']['properties']['semantics'])
    spec=importlib.util.spec_from_file_location('independent_algebra',HERE/'check_algebra.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.run()==json.loads((HERE/'check-results.json').read_text()),'saved replay differs'
    receipt=json.loads((HERE/'source-receipt.json').read_text())
    if args.source:
        private=Path(receipt['private_path'])
        assert private.stat().st_size==receipt['byte_count']
        assert sha(private)==receipt['sha256']
    print(json.dumps({'status':'pass','pinned_packet_files':len(manifest['files']),
        'schema_checks':'formulation, initialization and state-semantics fragments only; not a complete model validation',
        'algebra_groups':module.run()['group_count'],'private_source_verified':args.source},indent=2))

if __name__=='__main__':main()
