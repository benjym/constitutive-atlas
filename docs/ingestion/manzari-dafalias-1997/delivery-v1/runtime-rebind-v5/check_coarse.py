"""Operational regression for one exact old133point request; no source-pass claim."""
from pathlib import Path
import argparse,gzip,json,math
from preflight import D,P,sha
from check_binding import verify

def main():
 p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output);assert not out.exists(),'preserve evidence';folder=Path(a.folder);checks=[]
 def add(n,v):checks.append({'name':n,'passed':bool(v)})
 try:binding=verify(folder,'coarse');add('strict-source-build-artifact-binding',binding['passed'])
 except Exception as e:binding={'error':str(e)};add('strict-source-build-artifact-binding',False)
 policy=json.loads((D/'coarse-diagnostic-policy.json').read_text());c=policy['case'];report=json.loads((folder/'report.json').read_text());case=report.get('cases',{}).get(c['id'],{});points=case.get('points',[])
 add('operational-success',case.get('ok')is True);add('exact133points',len(points)==133);add('original-control-bit-wire',case.get('response_metadata',{}).get('loading',{}).get('controls_bits')==c['controls_bits'])
 def finite(v,n):return isinstance(v,list)and len(v)==n and all(type(x)in(int,float)and math.isfinite(x)for x in v)
 for i,point in enumerate(points):
  add('coordinate/'+str(i),i<len(c['controls'])and point.get('coordinate')==c['controls'][i]);add('full-finite-state/'+str(i),finite(point.get('state'),14));add('full-finite-strain/'+str(i),finite(point.get('strain'),6))
 add('initial-state',bool(points)and points[0].get('state')==c['initial']);add('initial-zero-strain',bool(points)and points[0].get('strain')==[0.]*6)
 with gzip.open(folder/(c['id']+'.jsonl.gz'),'rt')as f:raw=[json.loads(line)for line in f]
 expected={'mode':'run-controls','model':policy['model'],'parameters':c['parameters'],'initial':c['initial'],'settings':policy['settings'],'protocol':c['protocol'],'controls_bits':c['controls_bits']}
 add('exact-old-request',len(raw)==1 and raw[0].get('request')==expected)
 if len(raw)==1:
  x=raw[0];response=json.loads(x.get('raw_stdout','{}'));add('raw-saved-response',response==x.get('response'));add('no-harness-error',x.get('returncode')==0 and response.get('ok')is True and 'harness_error'not in response);add('all-raw-points-retained',points==[{'coordinate':v['control'],'state':v['state'],'strain':v['strain']}for v in response.get('points',[])])
 r={'identity':policy['identity'],'passed':all(x['passed']for x in checks),'scope':policy['scope'],'failures':sum(not x['passed']for x in checks),'policy_sha256':sha(D/'coarse-diagnostic-policy.json'),'report_sha256':sha(folder/'report.json'),'binding':binding,'checks':checks};out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'failures':r['failures']}));raise SystemExit(0 if r['passed']else 1)
if __name__=='__main__':main()
