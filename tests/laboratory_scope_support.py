"""Synthetic total-elastic transport fixture, generated through normal validation.

This fixture is not an atlas scientific model or a public catalogue addition.
"""
import json
from pathlib import Path
from atlas.compiler import generate
from atlas.model import ROOT, load, migrate_formulation, validate


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
    # Exercise the same loader and semantic checks as all other records.
    validate(total)
    generate(destination/'generated',list(fixtures.glob('*.json')))
    return total
