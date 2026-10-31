"""Synthetic assessment and corruption probes only. No compiled candidate execution."""
from pathlib import Path
import argparse,copy,json,gzip
from assess import Study,ideal_rows

def run(root,out):
 s=Study(root);ideal=ideal_rows(s);report=s.assess(ideal)
 assert report['passed'],report['failures'][:5]
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 (out/'synthetic-ideal.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 indices={r['id']:i for i,r in enumerate(s.requests)}
 def find(predicate):return next(i for i,r in enumerate(s.requests)if predicate(r))
 dense=find(lambda r:r['expected_ok']and r['case']=='dense-sign1-p0'and r['operation']=='projector_max'and r['kind']=='jet')
 selected=find(lambda r:r['id'].startswith('lazy/selected/')and r['kind']=='jet')
 lazy=find(lambda r:r['id'].startswith('lazy/unselected/')and r['kind']=='jet')
 sticky=find(lambda r:r['id'].startswith('sticky/')and r['kind']=='jet')
 solver=find(lambda r:r.get('solver')and not r['expected_ok'])
 hist=find(lambda r:r.get('history')and r['expected_ok'])
 histfail=find(lambda r:r.get('history')and not r['expected_ok'])
 valueonly=find(lambda r:r['expected_ok']and r.get('operation')=='max_value'and r['kind']=='jet')
 initial=find(lambda r:r['id'].startswith('initial/on/')and r['kind']=='jet')
 reset=find(lambda r:r['id'].startswith('reset/inactive/')and r['kind']=='jet')
 scale=find(lambda r:r['id'].startswith('scale/')and r['expected_ok'])
 cases=[]
 def probe(name,mutate):
  rows=copy.deepcopy(ideal);mutate(rows);result=s.assess(rows)
  assert not result['passed'],name
  cases.append({'name':name,'rejected':True,'failures':result['failures'][:4],'failure_count':len(result['failures'])})
 probe('column37',lambda x:x[dense]['output'][0]['derivatives'].__setitem__(37,1e100))
 probe('mandel-shear-direction',lambda x:x[dense]['output'][3]['derivatives'].__setitem__(3,1e100))
 probe('mandel-shear',lambda x:x[dense]['output'][3].__setitem__('value',1e100))
 probe('request-missing',lambda x:x.pop(10))
 probe('request-duplicate',lambda x:x.__setitem__(10,copy.deepcopy(x[9])))
 probe('last-request-truncated',lambda x:x.pop())
 probe('selected-repeat-false-success',lambda x:x[selected].__setitem__('ok',True))
 probe('lazy-unselected-false-failure',lambda x:x[lazy].__setitem__('ok',False))
 probe('sticky-predicate-cleared',lambda x:x[sticky].__setitem__('ok',True))
 probe('solver-partial-reset-committed',lambda x:x[solver]['output'][7].__setitem__('value',1.))
 probe('history-event-loss',lambda x:x[hist]['history'].__setitem__('events',[0]))
 probe('history-tentative-state-leak',lambda x:x[histfail]['history']['values'].__setitem__(0,18.))
 def stale(x):
  x[solver]['solver']['recovery_state']=[7.,2.,-3.,0.,0.,0.,.7,0.]
  x[solver]['solver']['fresh_state']=[7.,2.,-3.,0.,0.,0.,.7,0.]
 probe('stale-equal-recovery-with-bools-true',stale)
 probe('value-only-column37-leak',lambda x:x[valueonly]['output'][0]['derivatives'].__setitem__(37,1.))
 probe('derivative-array-truncated',lambda x:x[dense]['output'][0]['derivatives'].pop())
 probe('derivative-nonfinite',lambda x:x[dense]['output'][0]['derivatives'].__setitem__(0,float('nan')))
 probe('output-nonfinite',lambda x:x[dense]['output'][0].__setitem__('value',float('inf')))
 probe('input-mutation',lambda x:x[selected].__setitem__('input_unchanged',False))
 probe('wrong-slot',lambda x:x[dense].__setitem__('slot',999))
 probe('wrong-kind',lambda x:x[dense].__setitem__('kind','double'))
 probe('bool-slot-is-not-int',lambda x:x[0].__setitem__('slot',False))
 probe('nonbool-status',lambda x:x[dense].__setitem__('ok',1))
 probe('initial-check-skipped',lambda x:x[initial].__setitem__('ok',True))
 probe('inactive-reset-derivative-lost',lambda x:x[reset]['output'][0]['derivatives'].__setitem__(0,999.))
 probe('scale-value-wrong',lambda x:x[scale]['output'][0].__setitem__('value',999.))
 probe('solver-rejection-diagnostic-missing',lambda x:x[solver]['solver'].__setitem__('rejected',0))
 probe('solver-prepare-witness-missing',lambda x:x[solver]['solver'].__setitem__('tentative_reset_observed',False))
 probe('history-generation-wrong-type',lambda x:x[hist]['history'].__setitem__('generation',8.))
 probe('double-has-unexpected-derivatives',lambda x:x[0]['output'][0].__setitem__('derivatives',[0.]*38))
 result={'identity':'spectral-context-assessor-corruption-probes-v1','synthetic_only':True,'compiled_observations':0,'ideal_frame_passed':report['passed'],'probes':cases,'probe_count':len(cases),'passed':all(x['rejected']for x in cases)}
 (out/'corruption-probes.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 with gzip.GzipFile(filename=str(out/'synthetic-ideal-rows.json.gz'),mode='wb',mtime=0)as f:f.write(json.dumps(ideal,separators=(',',':'),allow_nan=False).encode())
 print(json.dumps({'ideal_passed':report['passed'],'probes_rejected':len(cases),'compiled_observations':0}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('out');a=p.parse_args();run(a.root,a.out)
