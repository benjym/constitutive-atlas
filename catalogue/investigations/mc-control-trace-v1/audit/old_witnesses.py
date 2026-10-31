from pathlib import Path
import importlib.util,sys,runpy,copy,json
P=Path(__file__).resolve().parent;F=P/'frozen';sys.path.insert(0,str(F));spec=importlib.util.spec_from_file_location('assess',F/'assess.py');m=importlib.util.module_from_spec(spec);sys.modules['assess']=m;spec.loader.exec_module(m)
n=runpy.run_path(str(F/'preflight.py'));doc=json.loads(json.dumps(n['doc']));req=n['req'];pts=doc['streams'][0]['baseline']['points'];out={}
for name,parent in [('none',None),('empty_failed_parent',{'ok':False,'points':[]}),('truncated_parent',{'ok':True,'points':pts[:-1]}),('failed_full_parent',{'ok':False,'points':pts})]:
 try:r=m.assess(doc,req,parent);out[name]={'accepted':True,'identity_checked':r['streams'][0]['original_artifact_identity_checked']}
 except Exception as e:out[name]={'accepted':False,'reason':str(e)}
(P/'old-parent-witnesses.json').write_text(json.dumps({'identity':'mc-control-trace-original-parent-gap-witnesses-v1','candidate_calls':0,'outcomes':out},indent=2)+'\n')
(P/'synthetic-old-doc.json').write_text(json.dumps(doc,indent=2)+'\n');print(out)
