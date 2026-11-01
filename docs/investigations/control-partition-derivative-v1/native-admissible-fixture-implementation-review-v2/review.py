"""Independent identity-correction review; no compiler/backend/process calls."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,difflib
D=Path(__file__).resolve().parent;C=D.parent
A=C/'native-admissible-fixture-implementation-v2';OLD=C/'native-admissible-fixture-implementation-v1';R1=C/'native-admissible-fixture-implementation-review-v1';PLAN=C/'native-ci-dispatch-plan-v2';PR=C/'native-ci-dispatch-plan-v2-review'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(n,v):checks.append({'id':n,'passed':bool(v)});assert v,n
expected={A:'9390abd41a29a54930a0eef9277fda0ad5b7992be3c17786f2e2aaec3f8b3ad3',OLD:'a80f24bfd03f0d8717fc492449f77fb431de0e5812d7ffe94580c1071211cf3f',R1:'0a657dadd7d4d2c09f2e522101dc367b9771136b164d4d417669b9f40125faae',PLAN:'27325aae9a3f5f0d2ea7c4b7cc30ff6ccf80cd5ac454f14bbc234e14bfeb8710',PR:'5e304443eab3bb8dd4cb909256e854f3b2ca2a4dcbab736c9dc729050c56d237'}
for folder,h in expected.items():
 ck('manifest/'+folder.name,sha(folder/'manifest.json')==h)
 receipt=load(folder/'manifest.json');files=receipt.get('files',receipt)
 ck('all exact files/'+folder.name,all(sha(folder/n)==v for n,v in files.items()))
 ck('cache-free/'+folder.name,not list(folder.rglob('*.pyc'))and not list(folder.rglob('__pycache__')))
f=load(A/'source-freeze.json');f1=load(OLD/'source-freeze.json');S=Path(f['source_directory']);S1=Path(f1['source_directory'])
ck('new source freeze identity',sha(A/'source-freeze.json')=='a3793d07d8c23691f273aa760eb697914f2de08b75934f071c97d8d16f9ee73e')
for folder,receipt in [(S,f),(S1,f1)]:
 ck('exact582 inventory/'+str(folder),len(receipt['source_files'])==582 and sorted(receipt['source_files'])==sorted(str(p.relative_to(folder))for p in folder.rglob('*')if p.is_file()))
 ck('all582 bytes/'+str(folder),all(sha(folder/n)==v for n,v in receipt['source_files'].items()))
 ck('no source symlinks/'+str(folder),not any(p.is_symlink()for p in folder.rglob('*')))
ck('same path inventory',f['source_files'].keys()==f1['source_files'].keys())
ck('only tests/test_solver.cpp changed',[n for n in f['source_files']if f['source_files'][n]!=f1['source_files'][n]]==['tests/test_solver.cpp'])
ck('exact new public/isolated cpp',sha(A/'test_solver.cpp')==sha(S/'tests/test_solver.cpp')=='4439b0b9fb1ddf347e0496b047c4df3a12c3844b434c448796c18852daa8e5a6')
old=(OLD/'test_solver.cpp').read_text();new=(A/'test_solver.cpp').read_text()
before_print='std::cout<<(explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")'
after_print='std::cout<<(md_admissible?"Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5":explicit_fixtures?"Explicit valid-domain/GIS-depth20 fixtures":"Strict original default fixtures")'
before_error='"MD numerical fixture requires exact v5 pairing"';after_error='"MD1997 numerical fixture requires explicit-gis20-occ-restart-duncan-v5"'
for name,before,after in [('stdout',before_print,after_print),('pairing error',before_error,after_error)]:
 ck('exact once substitution/'+name,old.count(before)==new.count(after)==1 and after not in old)
ck('independent forward two substitutions only',old.replace(before_print,after_print).replace(before_error,after_error)==new)
ck('independent exact reverse restores v1',new.replace(after_print,before_print).replace(after_error,before_error)==old)
ops=[op for op in difflib.SequenceMatcher(None,old.splitlines(True),new.splitlines(True),autojunk=False).get_opcodes()if op[0]!='equal']
ck('exact two replacement lines',len(ops)==2 and all(t=='replace'and j-i==l-k==1 for t,i,j,k,l in ops))
contracts=load(PLAN/'process-contracts.json')
positive='Source-admissible MD1997 numerical fixtures; inherited explicit-gis20-occ-restart-duncan-v5'
ck('new label exact accepted contract',contracts['proposed_new_positive_stdout']==positive+'; models=16\n'and '"'+positive+'"'in after_print)
for row in contracts['cases']:
 if row['id']in ['missing-native','incompatible-native']:ck('pairing error exact accepted contract/'+row['id'],row['stderr']==after_error.strip('"')+'\n')
for name,label in [('legacy explicit','Explicit valid-domain/GIS-depth20 fixtures'),('legacy default','Strict original default fixtures')]:
 ck('both original labels byte exact/'+name,old.count('"'+label+'"')==new.count('"'+label+'"')==1)
# C++ conditional operator associates right-to-left: false md_admissible returns
# the identical old explicit/default expression; selector guards are unchanged.
ck('new label guarded only by md_admissible',after_print in new and after_print.replace('md_admissible?"'+positive+'":','')==before_print)
ck('pairing condition unchanged','require(profile&&std::string(profile)=="explicit-gis20-occ-restart-duncan-v5",'+after_error+');'in new)
ck('all selector guards before stdout',all(new.index(t)<new.index('std::cout<<')for t in ['unknown native fixture profile','unknown numerical fixture profile','MD numerical fixture requires exactly one MD model',after_error]))
ck('all numerical/helper code byte identical',old[old.index('// Source-only fixture diagnostics:'):old.index('int main()')]==new[new.index('// Source-only fixture diagnostics:'):new.index('int main()')]and old[old.index('// Independently finite-difference'):]==new[new.index('// Independently finite-difference'):])
ck('v1 blocker retained',load(R1/'manifest.json')['decision']=='BLOCKED'and load(R1/'checks.json')['blocking_findings']==['B1'])
ck('prior214 independent source assertions retained',load(R1/'checks.json')['checks_passed']==214 and all(x['passed']for x in load(R1/'checks.json')['checks']))
probes=load(R1/'probe-receipts.json')['receipts']
ck('all108 prior independent probes bound and valid',len(probes)==108 and all(x['domain']and x['smooth']for x in probes))
# No author verification script is executed; two-line equivalence carries the
# previous independent numerical-source assessment, not a compiled outcome.
result={'identity':'independent-native-fixture-identity-v2-review','reviewer':'/root/md1997_source','author':'coordinator /root; numerical-v1 /root/md1997_reference','decision':'ACCEPTED for prospective fixture implementation source only','blocking_findings':[],'resolved_findings':['B1'],'source_checks':len(checks),'checks':checks,'prior_full_numerical_source_review_manifest_sha256':expected[R1],'all_numerical_bytes_unchanged_after_reverse':True,'builds':0,'compiler_calls':0,'compiled_calls':0,'numerical_success_observed':False,'CI_implementation_accepted':False}
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
(D/'inputs.json').write_text(json.dumps({str(p/'manifest.json'):h for p,h in expected.items()},indent=2)+'\n')
print(json.dumps({'decision':result['decision'],'source_checks':len(checks),'resolved':['B1'],'compiled_calls':0}))
