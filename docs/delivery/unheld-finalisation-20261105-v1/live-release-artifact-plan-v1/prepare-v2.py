from pathlib import Path
import json,hashlib
P=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/live-release-artifact-plan-v1')
http='''def verify_http(base_url,members,names,output,report):
 """Retain request start, response headers, complete/partial hashes and failure before raising."""
 def save():
  (output/'report.json').write_text(json.dumps(report,indent=2)+'\\n')
 report['status']='running-production-http';report['http']=[];save()
 for name in sorted(names):
  url=base_url.rstrip('/')+'/'+name
  row={'path':name,'requested_url':url,'url':url,'status':None,'sha256':hashlib.sha256(b'').hexdigest(),'bytes':0,'headers':{},'observation_status':'request-started'}
  report['http'].append(row);save();h=hashlib.sha256()
  try:
   request=urllib.request.Request(url,headers={'Cache-Control':'no-cache','Accept-Encoding':'identity','User-Agent':'Constitutive-Atlas-release-audit'})
   with urllib.request.urlopen(request,timeout=120)as response:
    row.update(url=response.url,status=response.status,headers=dict(response.headers.items()),observation_status='headers-returned');save()
    while chunk:=response.read(1024*1024):h.update(chunk);row['bytes']+=len(chunk)
   row.update(sha256=h.hexdigest(),observation_status='body-returned');save()
   assert row['status']==200 and row['sha256']==members[name]['sha256']and row['bytes']==members[name]['bytes'],name
   row['observation_status']='matched';save()
  except BaseException as error:
   row.update(sha256=h.hexdigest(),observation_status='failed',error={'type':type(error).__name__,'message':str(error)})
   if getattr(error,'headers',None)is not None:row['headers']=dict(error.headers.items())
   if getattr(error,'code',None)is not None:row['status']=error.code
   report['status']='failed-production-http';save();raise
 report['status']='passed-artifact-and-selected-production-http';save()
 return report['http']

'''
s=(P/'verify.py').read_text();s=s.replace('def main():',http+'def main():');start=s.index(' # Compare selected real production bytes');end=s.index("if __name__=='__main__':main()")
s=s[:start]+''' report={'status':'artifact-verified-http-pending','revision':args.revision,'pages_run_id':run['id'],'artifact_id':artifact['id'],'api_artifact_digest':artifact['digest'],'download_zip_sha256':zipsha,'download_zip_bytes':zipsize,'deployment_id':deployment['id'],'members':len(members),'tar_bytes':sum(x['bytes']for x in members.values()),'revision_stamps':stamps,'http':[],'scope':'No browser or compiled execution; all source/CI evidence review remains separate.'}
 (args.output/'members.json').write_text(json.dumps(members,indent=2)+'\\n')
 verify_http(args.base_url,members,set(contract['http_paths'])|set(stamps),args.output,report)
 print(json.dumps(report,indent=2))
'''+s[end:]
(P/'verify-v2.py').write_text(s)
s=(P/'browser-validator-v1.validate.mjs').read_text().replace("import{parity,withoutElapsed}","import{laboratoryDocumentCSV}from'../nine-example-refresh-plan-v1/context/web/laboratory-document.mjs';\nimport{parity,withoutElapsed}").replace("browser-validator-v1.POLICY.json","browser-validator-v2.POLICY.json")
start=s.index(" const csv=fs.readFileSync");end=s.index('\n}',start)
s=s[:start]+''' const csvText=fs.readFileSync(join(D,id+'-default.csv'),'utf8'),csv=csvText.trim().split(/\\r?\\n/).map(x=>x.split(',')),header=csv.shift();assert.deepEqual(header,['axial_strain_1','radial_strain_1','volumetric_strain_1','effective_mean_stress_Pa','effective_signed_deviatoric_stress_Pa','pore_pressure_change_Pa','stress_scope','pore_pressure_availability','iterations','substeps']);assert.equal(csv.length,101);
 for(const row of csv){assert.equal(row.length,header.length);for(const index of[0,1,2,3,4,8,9])assert.ok(row[index].trim()!==''&&Number.isFinite(Number(row[index])),header[index]);assert.equal(row[5],'');assert.equal(row[6],'effective');assert.equal(row[7],'unavailable');checks++;}
 assert.equal(csvText.replace(/\\r\\n/g,'\\n').trimEnd(),laboratoryDocumentCSV(defaultDoc.specification,defaultDoc.result,read(policy.catalogue)).trimEnd(),'Every CSV field must equal original exporter output');checks++;
'''+s[end:]
(P/'browser-validator-v2.validate.mjs').write_text(s)
policy=json.loads((P/'browser-validator-v1.POLICY.json').read_text());policy['identity']='baseline-five-prospective-production-browser-download-policy-v2';policy['correction']='R1 exact original CSV exporter for every field plus all declared meaningful numeric columns finite; original gates unchanged.';catalogue=P.parent/'nine-example-refresh-plan-v1/manufactured-catalogue-fixture.json';helper=P.parent/'nine-example-refresh-plan-v1/context/web/laboratory-document.mjs';policy['catalogue']=str(catalogue)
for f in [catalogue,helper]:policy['pins'].append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'browser-validator-v2.POLICY.json').write_text(json.dumps(policy,indent=2)+'\n')
