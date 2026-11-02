"""Bounded receipt/JSON/Git metadata verification. No source/asset byte rescan."""
from pathlib import Path
import hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent;B=HERE.parent;P=B/'package-v6';REPO=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 freeze_path=P/'source-freeze.json';freezehash=sha(freeze_path);f=json.loads(freeze_path.read_text());policy=json.loads((B/'source-closure-v5/RESOURCE_POLICY.json').read_text());identity=json.loads((B/'source-closure-v5/full-tree-resource-identity.json').read_text());plan=json.loads((P/'plan.json').read_text())
 assert sha(P/'MANIFEST.json')=='c566be0e484973342ea3b52c15465fb52d80236f851d6f43c9a62dfb97e052bf'
 for n,h in json.loads((P/'MANIFEST.json').read_text())['files'].items():assert sha(P/n)==h
 for field,name in [('plan_sha256','plan.json'),('wrapper_sha256','run_package.py'),('freeze_script_sha256','freeze_inputs.py'),('process_helper_sha256','owned_process.py')]:assert f[field]==sha(P/name)
 assert f['status']=='frozen-source-only; no package execution'
 assert f['revision']==identity['revision']==policy['revision']=='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
 assert f['parents']==identity['parents']==policy['parents']==plan['parents'];assert f['cwd']==plan['cwd'];assert f['tree']==identity['tree']==policy['tree']
 assert f['resource_identity_sha256']==sha(B/'source-closure-v5/full-tree-resource-identity.json')==policy['metadata_identity_sha256']
 actual={}
 raw=subprocess.check_output(['git','ls-tree','-r','-l','-z',f['revision']],cwd=REPO)
 for row in raw.split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t');mode,kind,oid,size=meta.decode().split();assert kind=='blob';actual[name.decode()]={'mode':mode,'git_blob':oid,'bytes':int(size)}
 expected={r['path']:{k:r[k] for k in ['mode','git_blob','bytes']} for r in identity['entries']}
 assert actual==expected and set(f['source'])==set(expected) and len(expected)==40318
 for n,item in f['source'].items():
  assert set(item)=={'bytes','sha256','git_blob','mode','permissions'}
  assert {k:item[k] for k in ['mode','git_blob','bytes']}==expected[n]
  assert re.fullmatch('[a-f0-9]{64}',item['sha256']) and type(item['permissions']) is int
 assert sum(v['bytes'] for v in f['source'].values())==f['source_bytes']==policy['exact_logical_bytes']==3605081558
 changed=set()
 for parent in f['parents']:
  changed.update(n.decode() for n in subprocess.check_output(['git','diff-tree','-r','--no-commit-id','--name-only','-z',parent,f['revision']],cwd=REPO).split(b'\0') if n)
 assert f['branch_delta_paths']==sorted(changed);assert f['deleted_paths']==sorted(changed-set(expected))
 for n,item in f['copied_members'].items():
  if item['kind']=='file':assert {k:item[k] for k in ['bytes','sha256','git_blob']}=={k:f['source'][n][k] for k in ['bytes','sha256','git_blob']} and item['git_mode']==f['source'][n]['mode'] and item['mode']==f['source'][n]['permissions']
 dirs=[plan['argv'][i+1] for i,arg in enumerate(plan['argv']) if arg.startswith('--') and arg.endswith('-wasm-dir')]
 assert len(dirs)==14 and set(dirs)==set(f['asset_member_sets'])
 assets={str(Path(directory)/n):{'sha256':item['sha256'],'bytes':item['bytes']} for directory,members in f['asset_member_sets'].items() for n,item in members.items()}
 assert len(assets)==50 and all(f['qualified_assets_and_ignored_witness'][n]==item for n,item in assets.items())
 for n,item in assets.items():
  assert re.fullmatch('[a-f0-9]{64}',item['sha256']) and type(item['bytes']) is int and item['bytes']>=0
  try:relative=Path(n).relative_to(Path(f['cwd'])).as_posix()
  except ValueError:continue
  if relative in f['source']:assert item=={k:f['source'][relative][k] for k in ['sha256','bytes']}
 witness=str(Path(f['cwd'])/'.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json')
 assert f['qualified_assets_and_ignored_witness'][witness]=={'sha256':'ee7e4ad4b34c14843c6f7d0b2d66a936d8c8409fa1e2dc2c493949a9411589f9','bytes':146902}
 assert set(f['qualified_assets_and_ignored_witness'])==set(assets)|{witness} and len(f['qualified_assets_and_ignored_witness'])==51
 # Registry/index metadata only: no archive, curated trajectory or engine bytes read.
 root=Path(f['cwd']);grants=json.loads((root/'data/experiment_releases.json').read_text())['grants'];assert grants==[]
 curated=json.loads((root/'data/curated/index.json').read_text())['records']
 for item in curated:
  n=(Path('data/curated')/item['path']).as_posix();assert f['source'][n]['sha256']==item['sha256']
 alias=policy['case_alias_policy'][0]['paths'];assert f['source'][alias[0]]==f['source'][alias[1]]
 link=policy['known_symlink_policy'][0];entry=f['source'][link['path']];assert entry['mode']=='120000' and entry['bytes']==12 and entry['sha256']==hashlib.sha256(b'../else/deep').hexdigest()
 assert sha(freeze_path)==freezehash
 report={'status':'passed-bounded-actual-freeze-receipt-review','source_freeze_sha256':freezehash,'revision':f['revision'],'tree':f['tree'],'parents':f['parents'],'source_files':len(expected),'source_bytes':f['source_bytes'],'source_mode_blob_size_exact_git_equality':True,'copied_entries_consistent':len(f['copied_members']),'asset_directories':14,'asset_files':50,'ignored_witness_files':1,'total_asset_entries':51,'curated_index_records_bound_to_source_hashes':len(curated),'grant_archives':0,'script_plan_helper_pins_match':True,'link_alias_bindings_match':True,'branch_delta_and_deletions_match':True,'parent_actual_freeze_terminal':{'session':46121,'chunk':'dab3e9','exit_code':0},'review_does_not_repeat_actual_source_or_asset_byte_scan':True,'package_browser_material_compiler_remote_calls':0}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
