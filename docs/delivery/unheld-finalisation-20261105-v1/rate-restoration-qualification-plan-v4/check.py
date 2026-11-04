from pathlib import Path
import ast,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parent;O=H.parent/'rate-restoration-qualification-plan-v3';checks=[]
def test(label,condition):
 assert condition,label
 checks.append(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in H.glob('*.py'):ast.parse(p.read_text());test('parse '+p.name,True)
for name in ['requests.json','external-pins.json']:test(name+' exact', (H/name).read_bytes()==(O/name).read_bytes())
s=(H/'extras.mjs').read_text();test('pair reads both new v4 output reports',all("join(plan.output,'extra-"+b+"/report.json')"in s for b in ['native','wasm']) and all("join(actual,'extra-"+b+"/report.json')"not in s for b in ['native','wasm']));s=s.replace("join(plan.output,'extra-native/report.json')","join(actual,'extra-native/report.json')").replace("join(plan.output,'extra-wasm/report.json')","join(actual,'extra-wasm/report.json')");s=s.replace("import{verifySupplementInputs}from'./response-contract.mjs';\n",'').replace('const[backend,actualArg,manifestSHA,reviewPath,reviewSHA]','const[backend,actualArg,manifestSHA]').replace('function guard(full=false){verifyReview();','function guard(full=false){').replace("const out=join(plan.output,'extra-'+backend)","const out=join(actual,'extra-'+backend)").replace('control-restoration-C-twelve-public-supplement-v4','control-restoration-C-twelve-public-supplement-v3').replace('verifySupplementInputs(result,row.specification);','assert.deepEqual(result.loading.controls_bits,row.specification.loading.controls_bits);assert.deepEqual(result.integration_settings,row.specification.integration_settings);')
a=s.index('function verifyReview()');b=s.index('guard(true);assert.equal',a);s=s[:a]+s[b:];test('exact reverse to v3 extras all other assertions and transport unchanged',s==(O/'extras.mjs').read_text())
pre=json.loads((H/'predecessor-pins.json').read_text());test('unique predecessor pins',len({p['path']for p in pre})==len(pre))
for p in pre:
 q=Path(p['path']);test('predecessor '+p['path'],q.stat().st_size==p['bytes']and sha(q)==p['sha256'])
plan=json.loads((H/'plan.json').read_text());test('only continuation phases',plan['phases']==['extra-native','extra-wasm','extra-pair']);test('no rebuilt claim',plan['fresh_build_required']is False and plan['compiled_observations']is False);test('new output',plan['actual']!=plan['output'])
# Exact original74 extension except explicit output/review guard wrappers.
s=(H/'recorded74-launch.py').read_text();old=(H.parent/'recorded74-actual-plan-v1/launch.py').read_text();a=s.index("spec=importlib.util.spec_from_file_location('continuation_v4'");b=s.index("previous=c.ACTUAL",a);s=s[:a]+s[b:];s=s.replace("'baseline-five-C-v4-'+phase+'-preflight-20261105.raw'","'baseline-five-C-'+phase+'-preflight-20261105.raw'");a=s.index('primary=None\ntry:result=c.observe_phase');b=s.index("if phase=='recorded74':\n assert 'Ran 74",a);s=s[:a]+'result=c.observe_phase(pre,phase,MANIFEST)\n'+s[b:];test('exact original74 reverse argv env modules assertions',s==old)
result=subprocess.run(['node',str(H/'check.mjs')],capture_output=True,text=True);assert result.returncode==0,result.stderr;node=json.loads(result.stdout);test('pure node response contract checks',node['passed']and node['engine_calls']==0)
print(json.dumps({'passed':True,'source_checks':len(checks),'node':node,'checks':checks},indent=2))
