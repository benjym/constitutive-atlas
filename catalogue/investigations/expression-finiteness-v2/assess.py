"""Assess retained observations, not a rebuild or constitutive reference."""
from pathlib import Path
import hashlib,json
STUDY=Path(__file__).resolve().parent

def assess(study=STUDY):
    study=Path(study)
    for name,pin in json.loads((study/'manifest.json').read_text()).items():
        if hashlib.sha256((study/name).read_bytes()).hexdigest()!=pin:
            raise ValueError('frozen input changed: '+name)
    expected=json.loads((study/'expected.json').read_text())
    rows={}
    for backend in ('native','wasm'):
        receipt=json.loads((study/backend/'receipt.json').read_text())
        if [x['exit_code']for x in receipt['commands']] != [0,0,0]:
            raise ValueError('incomplete execution: '+backend)
        rows[backend]=json.loads((study/backend/'observe.stdout.txt').read_text())
    # Canonical JSON equality preserves bool versus numeric distinctions and
    # checks every ordered row, identifier, key and status, including extras.
    canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
    matches={backend:canonical(actual)==canonical(expected)for backend,actual in rows.items()}
    parity=canonical(rows['native'])==canonical(rows['wasm'])
    return {'rows_per_backend':len(expected),'matches':matches,'parity':parity,
            'pass':all(matches.values())and parity,'compiled_rebuild':False,
            'scope':'executed expression acceptance; no model-context or solver proof'}

if __name__=='__main__':print(json.dumps(assess(),indent=2))
