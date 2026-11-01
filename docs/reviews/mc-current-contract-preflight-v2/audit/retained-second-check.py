import hashlib, importlib.util, json, pathlib
P=pathlib.Path(__file__).resolve().parent
load=lambda f:json.loads((P/f).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('strict_reader',P/'strict_observation_json.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
checks={}
for kind in ['duplicate','overflow']:
 try: module.loads((P/f'witness-{kind}.json').read_text())
 except ValueError as e: checks['strict_rejects_'+kind]=str(e)
 else: raise AssertionError(kind)
assert (P/'replay-results.json').read_bytes()==(P/'snapshot/current/consumer-results.json').read_bytes();checks['parent_collector_byte_exact_replay']=True
cat=load('snapshot/current/catalogue.json');assert len(cat['models'])==12
assert cat['sha256']==hashlib.sha256(json.dumps(cat['models'],sort_keys=True,separators=(',',':')).encode()).hexdigest();checks['catalogue_hash_recomputed']=cat['sha256'];checks['model_ids']=[m['id'] for m in cat['models']]
a=load('snapshot/current/mc-draft.json');b=load('snapshot/current/prior-mc.json');delta=sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k));assert delta==['description','name','status'];checks['candidate_changed_fields']=delta
contracts=load('snapshot/current/contracts.json');bits=sum(len(x['specification']['loading']['controls_bits']) for x in contracts);assert len(contracts)==14 and bits==834;checks['paths_controls_deltas']=[14,bits,bits-14]
ref=load('snapshot/mc-browser-loading-paths-v1/reference-p360.json'); frames=load('snapshot/current/source-ideal.json')['frames']; refs={x['id']:x for x in ref['paths']}; count=0
for f in frames:
 rp=refs[f['id']]['points']; pts=f['result']['points'];assert len(rp)==len(pts)
 for r,p in zip(rp,pts):
  assert p['state']==list(map(float,r['state'])) and p['strain']==list(map(float,r['strain']))
  assert p['control']==float(r['control']) and p['p']==float(r['mean_stress']) and p['q_signed']==float(r['q']) and p['q']==abs(float(r['q']))
  assert p['u']==(float(r['pore_pressure']) if f['result']['protocol'] in (2,3) else None)
  assert [p[k] for k in ['iterations','substeps','rejected','error']]==[0,0,0,0]
  count+=1
checks['rounded_reference_frame_points_checked']=count
assert sha(P/'snapshot/mc-browser-loading-paths-v1/source-input.json')==ref['source_input_sha256'];checks['reference_source_input_sha256']=ref['source_input_sha256']
root=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');pins=load('snapshot/current/source-pins.json')['sources'];mismatch=[]
for f,h in pins.items():
 if not(root/f).is_file() or sha(root/f)!=h:mismatch.append(f)
checks['source_pins_checked']=len(pins);checks['current_root_source_pin_mismatches']=mismatch
assert not mismatch
(P/'independent-python-results.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
