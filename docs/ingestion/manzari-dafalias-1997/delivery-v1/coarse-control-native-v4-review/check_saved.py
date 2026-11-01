import contextlib,gzip,hashlib,io,json,math,runpy,struct,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parent;B=P/'coarse-control-native-v4';E=B/'evidence';R=P/'runtime-rebind-v5';T=P/'build-native-v4';C=P.parents[2]/'investigations/control-partition-derivative-v1/implementation-v1';root=P.parents[3]
load=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
for b in [B,T]:check(b.name+'/manifest',all(h(b/k)==v for k,v in load(b/'manifest.json').items()))
check('pre-observation inputs unchanged',all(h(root/k)==v for k,v in load(B/'freeze.json')['inputs'].items()))
s=load(C/'source-freeze.json');check('582 source files unchanged',len(s['source_files'])==582 and all(h(Path(s['source_directory'])/k)==v for k,v in s['source_files'].items()))
r=load(E/'report.json');receipt=load(B/'receipt.json');br=load(T/'build-receipt.json');bind=load(E/'runtime-binding.json');pol=load(R/'coarse-diagnostic-policy.json');plan=load(P/'execution-v3/requests.json');c=pol['case'];old=next(x for x in plan['cases']if x['id']==c['id'])
check('exact original complete planned case settings/model',c==old and pol['settings']==plan['settings'] and pol['model']==plan['model'] and pol['model_sha256']==plan['model_sha256'])
check('candidate exact hash',h(P/'manzari-dafalias-1997-constant-m-be-v1.json')==pol['model_sha256'])
check('actual artifact/raw/build identities',h(Path(br['artifact_path']))==br['artifact_sha256']==receipt['artifact_sha256']==bind['artifact_sha256'] and h(E/'report.json')==receipt['raw_report_sha256']==bind['report_sha256'] and h(T/'build-receipt.json')==bind['coordinator_build_receipt_sha256'])
check('actual generated catalogue/header matching saved and embedded',h(Path(br['catalogue_path']))==br['generated_catalogue_sha256'] and Path(br['catalogue_path']).read_bytes()==(T/'generated-models.json').read_bytes() and (Path(br['catalogue_path']).parent/'models.hpp').read_bytes()==(T/'generated-models.hpp').read_bytes())
bp=load(T/'build-process.json');cp=load(T/'configure-process.json');check('explicit Release serial target',bp['returncode']==cp['returncode']==0 and bp['command'][-4:]==['--target','atlas_solver','--parallel','1'] and '-DCMAKE_BUILD_TYPE=Release' in cp['command'])
desc=load(B/'describe-process.json');embedded=json.loads(desc['stdout']);check('actual saved describe exact generated16 models',desc['returncode']==0 and desc['command']==[br['artifact_path'],'--describe'] and embedded==load(T/'generated-models.json') and len(embedded['models'])==16)
with gzip.open(E/(c['id']+'.jsonl.gz'),'rt')as f:raw=[json.loads(x)for x in f]
check('single complete raw record',len(raw)==1)
x=raw[0];response=json.loads(x['raw_stdout']);points=r['cases'][c['id']]['points']
check('wire bits independently reconstruct all133 controls',[struct.pack('>d',x).hex()for x in c['controls']]==c['controls_bits'] and len(c['controls'])==133)
check('raw parsed fullresponse and saved points correspondence',response==x['response'] and points==[{'coordinate':v['control'],'state':v['state'],'strain':v['strain']}for v in response['points']])
check('operational completion full finite state/control/strain',response['ok'] is True and len(points)==133 and all(v['coordinate']==c['controls'][i] and len(v['state'])==14 and len(v['strain'])==6 and all(math.isfinite(z)for z in v['state']+v['strain'])for i,v in enumerate(points)))
retained=load(P/'retained-raw-v1/manifest.json')['files'];prior=next(v for v in retained if 'md-native-report-v3/'in v['original_path'] and v['original_path'].endswith('/'+c['id']+'.jsonl.gz'));priorfile=root/prior['retained_path'];check('prior failure raw durable hash',h(priorfile)==prior['sha256'])
with gzip.open(priorfile,'rt')as f:priorraw=[json.loads(v)for v in f]
check('exact prior failed request replay',priorraw[0]['request']==x['request'])
priorresponse=priorraw[0]['response'];check('prior19points failed now133complete',priorresponse['ok']is False and len(priorresponse['points'])==19)
with patch.object(sys,'argv',[str(R/'check_coarse.py'),str(E),'--output',str(D/'rechecked.json')]),patch.object(sys,'path',[str(R)]+sys.path),contextlib.redirect_stdout(io.StringIO()):
 try:runpy.run_path(str(R/'check_coarse.py'),run_name='__main__')
 except SystemExit as ex:check('frozen checker exit',ex.code==0)
j=load(D/'rechecked.json');check('frozen checker all results reproduced',j['passed'] and j['checks']==load(B/'checks.json')['checks'])
(D/'checks.json').write_text(json.dumps({'reviewer_compiled_calls':0,'decision':'accepted bounded operational completion only','checks':checks},indent=2)+'\n');print(len(checks),len(j['checks']))
