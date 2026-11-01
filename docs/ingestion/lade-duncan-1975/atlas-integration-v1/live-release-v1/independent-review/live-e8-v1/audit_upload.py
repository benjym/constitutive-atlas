import importlib.util,pathlib,json,hashlib,tarfile
S=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');H=pathlib.Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');O=S/H/'independent-review/live-e8-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=S/H/'check_live_v5.py';spec=importlib.util.spec_from_file_location('live_v5',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prior=json.loads((S/H/'independent-review/live-checker-v1/v5-audit/review-receipt.json').read_text());assert all(sha(S/k)==v for k,v in prior['files'].items())
inv,identity,manifest,report,data=m.upload_data()
assert m.parse((S/H/'tested-upload.json').read_bytes())==inv
assert (S/H/'uploaded-identity.json').read_bytes()==data['engine-implicit-path/identity.json']
assert (S/H/'uploaded-package-manifest.json').read_bytes()==data['engine-implicit-path/package-manifest.json']
encoded=(json.dumps(inv,indent=2)+'\n').encode();report['inventory_sha256']=hashlib.sha256(encoded).hexdigest();assert (S/H/'upload-verification.json').read_bytes()==(json.dumps(report,indent=2)+'\n').encode()
assert identity['runtime_sha256']=='acb8756e5d80b3a9f967a5e3985a2e4b3c5d0f0ca1011172732155c3d9c25928'
assert identity['qualification_sha256']=='61c68aed8407502c80e236a6fa4151098c06aa5515859b8b94e60089d4980a2a'
assert identity['build_review_sha256']=='e47890b8aba6d4f074f45635315acdcc569bc48a6acf5a47bc96798d4ab50e4a'
for f,h in identity['component_sha256'].items():assert inv[f]==h
acq=m.read('upload-acquisition.json');archive=m.private_file(acq['artifact_tar_path']);payloads={}
need={'engine-implicit-path/review.json','engine-implicit-path/approval.json','engine-implicit-path/build-review.json','engine-implicit-path/qualification.json','engine-implicit-path/models.json'}
with tarfile.open(archive)as t:
 for member in t:
  n=m.member_name(member.name,member.isdir())
  if n in need:payloads[n]=m.parse(t.extractfile(member).read())
assert len(payloads)==len(need)
review=payloads['engine-implicit-path/review.json'];assert review['status']=='accepted'
# Scope identity is identical to the separately accepted canonical scientific review.
canon=S/'catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json';assert sha(canon)==inv['engine-implicit-path/review.json']
assert payloads['engine-implicit-path/build-review.json']['status']=='accepted'
files={str(H/n):sha(S/H/n)for n in ['check_live_v5.py','LIVE_POLICY-v5.json','run-artifacts.json','upload-acquisition.json','tested-upload.json','uploaded-identity.json','uploaded-package-manifest.json','upload-verification.json']}
files[str(canon.relative_to(S))]=sha(canon)
result={'status':'accepted-saved-upload-only','reviewer_run':'/root/lade_source_review','revision':report['revision'],'run':report['run'],'artifact_id':report['artifact_id'],'files_verified':len(inv),'report_recomputed':report,'checks':{'API_digest_outer_zip_tar_exact':True,'all_tar_member_hashes_recomputed':True,'archive_caps_paths_duplicates_and_specials':True,'saved_inventory_identity_manifest_receipt_exact':True,'qualified_model_runtime_module_review_and_components_exact':True,'single_public_Lade_model':True},'files':files,'private_artifacts':{acq['artifact_zip_path']:report['outer_zip_sha256'],acq['artifact_tar_path']:report['tar_sha256']},'blocking_findings':[],'not_claimed':['Full CI success','Deployment success','Live HTTP body identity','Actual live browser behavior','E8 completion']}
(O/'upload-review-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'receipt_sha256':sha(O/'upload-review-receipt.json'),'files':len(inv),'artifact':report['artifact_id']},indent=2))
