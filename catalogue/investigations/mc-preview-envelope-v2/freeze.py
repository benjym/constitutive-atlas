from pathlib import Path
import hashlib,json,datetime
s=Path(__file__).resolve().parent
assert not(s/'manifest.json').exists()and not(s/'assessment.json').exists()
assert json.loads((s/'preflight-results.json').read_text())['passed']is True
assert(s/'envelope-audit/README.md').is_file()
pins={str(p.relative_to(s)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(s.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
(s/'manifest.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n')
(s/'prospective-freeze.json').write_text(json.dumps({'identity':'mc-preview-envelope-correction-freeze-v2','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(pins),'manifest_sha256':hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest(),'numeric_policy_changed':False,'new_candidate_calls':0,'saved_observations_assessed_with_corrected_envelope_at_freeze':0,'prior_observations':'v1 collected; original assessment TypeError retained; runtime envelope already observed. This correction is not a claim of a new pre-collection freeze.'},indent=2)+'\n')
print('frozen',len(pins))
