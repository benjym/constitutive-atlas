"""Freeze a prospective BE-schedule revision; reads source/old evidence, never executes a model."""
import argparse,datetime,hashlib,json,pathlib
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[3];V1=BASE.parent/'execution-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--revision',default='v1');a=ap.parse_args();dest=BASE/('freeze-'+a.revision+'.json');assert not dest.exists(),'Never overwrite a prior freeze'
 old=json.loads((V1/'cases.json').read_text())['cases'];new=json.loads((BASE/'cases.json').read_text())['cases'];assert len(old)==len(new)==136
 assert [c['id'] for c in old]==[c['id'] for c in new];rows=[]
 for x,y in zip(old,new):
  if x['kind']=='schedule':
   for k in ['specification','argv','args','types','call','references']:assert x[k]==y[k],(x['id'],k)
   kind='unchanged existing schedule'
  else:
   s=y['specification'];args=x['args'];parse=lambda v:[float(t) for t in v.split(',')] if v else []
   assert s['parameters']==parse(args[1]) and s['initial']==parse(args[2]) and s['initial_strain_rate']==parse(args[3]) and s['start_time']==args[4]
   assert abs(sum(g['duration'] for g in s['segments'])-args[5])<=1e-15
   for seg in s['segments']:assert [ctrl['value'] for ctrl in seg['controls']]==parse(args[3])
   if x['ok']:
    assert y['references'][-1]['state']==x['expected'] and y['references'][-1]['stress']==x['expected_stress']
   kind='direct-to-BE single segment' if not x.get('late') else 'same hold; output prefix introduces visible late committed sample'
  rows.append({'id':x['id'],'mapping':kind})
 for n in ['oracle.py','parity.py','expected-catalogue.json','reference-convergence.json']:assert (BASE/n).read_bytes()==(V1/n).read_bytes(),n
 lineage={'passed':True,'cases':136,'mapping':rows,'original_case_sha256':sha(V1/'cases.json'),'new_case_sha256':sha(BASE/'cases.json'),'unchanged_original_equations':True,'original_physical_budgets_preserved':True,'compiled_calls':0}
 (BASE/'lineage-check.json').write_text(json.dumps(lineage,indent=2)+'\n')
 source_files=set((ROOT/'atlas').glob('*.py'))|set((ROOT/'cpp').rglob('*.hpp'))|set((ROOT/'cpp').rglob('*.cpp'))|set((ROOT/'cmake/bingham').rglob('*'))
 source_files={p for p in source_files if p.is_file()}
 source_files|={ROOT/'CMakeLists.txt',ROOT/'schemas/model-v0.3.schema.json',ROOT/'schemas/run-v0.2.schema.json',ROOT/'docs/FORMULATION_CONTRACT.md',ROOT/'models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json',BASE.parent/'source-v1/candidate.json',BASE.parent/'source-v1/source-receipts.json',BASE.parent/'source-v1/analytical-references.json'}
 sources={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(source_files)}
 assert sources['models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json']=='6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850'
 prior_names=['freeze-v4.json','cases.json','study.py','oracle.py','parity.py','native-attempt1.json','native-attempt1-saved-diagnostics.json','native-attempt1-component-diagnostics.json','native-artifacts-attempt1.json','native-build-attempt1.json']
 prior={str((V1/n).relative_to(ROOT)):sha(V1/n) for n in prior_names if (V1/n).exists()}
 provenance={'identity':'bingham-be-schedule-source-bindings-v2','source_files':sources,'prior_v1_evidence':prior,'copied_helpers':{n:{'v1_sha256':sha(V1/n),'v2_sha256':sha(BASE/n)} for n in ['oracle.py','parity.py','expected-catalogue.json','reference-convergence.json']},'disclosure':'v1 compiled observations and failure diagnosis precede this study; this freeze precedes only new v2 requests; no v1 bytes or gates rewritten'}
 (BASE/'source-bindings.json').write_text(json.dumps(provenance,indent=2)+'\n')
 own={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(BASE.iterdir()) if p.is_file() and not p.name.startswith('freeze-')}
 record={'identity':'bingham-be-schedule-execution-v2-'+a.revision,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_new_v2_compiled_calls':True,'prior_bingham_compiled_observations_exist':True,'qualified_interface_proposed':'atlas_run_schedule BE only; atlas_integrate_time midpoint excluded','cases':136,'repeats_per_case':2,'files':own,'source_bindings_sha256':sha(BASE/'source-bindings.json'),'prior_evidence':prior}
 dest.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'freeze':str(dest),'sha256':sha(dest),'own_files':len(own),'source_files':len(sources)},indent=2))
if __name__=='__main__':main()
