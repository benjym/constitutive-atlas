"""Restricted synthetic total-elastic lowering for native transport tests only.

Production validate() deliberately remains effective-only. Never package these
fixtures as atlas models or use this test adapter as an ingestion path.
"""
import copy
import json
from pathlib import Path
from unittest.mock import patch
from atlas.compiler import generate
from atlas.model import ROOT, load, migrate_formulation, validate
from atlas.structure import check


def synthetic_total():
    model=migrate_formulation(load(ROOT/'models/linear-elastic.json'))
    model['id']='scope-synthetic-total-elastic'
    model['name']='Synthetic total elastic transport fixture'
    model['description']='Synthetic scope/serialization test only; not an atlas material addition.'
    model['formulation']['stress']['scope']='total'
    return model


def generate_transport_fixture(destination):
    destination=Path(destination);fixtures=destination/'fixtures';fixtures.mkdir(parents=True)
    for path in sorted((ROOT/'models').glob('*.json')):(fixtures/path.name).write_bytes(path.read_bytes())
    total=synthetic_total();special=fixtures/'scope-synthetic-total-elastic.json'
    special.write_text(json.dumps(total,indent=2)+'\n')
    schema=json.loads((ROOT/'schemas/model-v0.3.schema.json').read_text())
    def restricted_load(path):
        if Path(path)!=special:return load(path)
        candidate=json.loads(special.read_text());check(candidate,schema)
        assert candidate==total,'test fixture changed beyond its explicit scope'
        twin=copy.deepcopy(candidate);twin['formulation']['stress']['scope']='effective'
        validate(twin) # all mechanics/symbol/dimension/persistence checks unchanged
        return candidate
    with patch('atlas.compiler.load',side_effect=restricted_load):
        generate(destination/'generated',list(fixtures.glob('*.json')))
    return total
