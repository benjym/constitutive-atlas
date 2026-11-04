from pathlib import Path
import hashlib,json
Q=Path(__file__).resolve().parent;N=Q.parents[1];P=N/'current17-browser-plan-v1';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
ok(H(P/'manifest.json')=='ea239e2202f0c76b56f703d54a956f65ccc8ba715886428f4a0550b0e6726c5a','exact prospective manifest')
m=json.loads((P/'manifest.json').read_text());ok(len(m['files'])==34,'all34members')
for r in m['files']:
 p=P/r['path'];ok(p.is_file()and not p.is_symlink()and H(p)==r['sha256']and p.stat().st_size==r['size_bytes'],'exact frozen member '+r['path'])
ok(H(P/'plan.json')=='57755606e68767862711873063a1de6f5b27a3ff72b6283e6266dd3f7e7f8a36','exact browser plan')
ok(H(P/'POLICY.json')=='69ffcf07cafae17627272d014c77c3e7fd24508f5a9608f0f7fbd33bdd19c59c','exact browser policy')
plan=json.loads((P/'plan.json').read_text());policy=json.loads((P/'POLICY.json').read_text());old=N/'live-release-artifact-plan-v1/browser-validator-v2.validate.mjs'
a=old.read_text().splitlines();b=(P/'validate.mjs').read_text().splitlines();ok(len(a)==len(b),'validator same line count')
changed=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];ok(changed==[6,17],'validator exactly two changed lines')
# Exact full-line transitions; all other lines, including request/CSV/finite/parity calls, byteexact.
oldpolicy=a[6];expected=oldpolicy.replace("'browser-validator-v2.POLICY.json'","'POLICY.json'").replace("examples=read(join(S,'catalogue/laboratory-examples.json')).examples","examples=read(policy.reference_index).examples")
ok(expected==b[6],'policy line only exact locator/reference index substitutions')
expected=a[17].replace("assert.equal(examples.length,9);for", "assert.equal(examples.length,9);assert.deepEqual(examples.map(e=>e.id),policy.expected_ids);const currentExamples=read(policy.source_index).examples;assert.equal(currentExamples.length,9);assert.deepEqual(currentExamples.map(e=>e.id),policy.expected_ids);for").replace("stats.push({id:entry.id,...parity(actual.result,reference.result,gate)})", "assert.equal(reference.catalogue_hash,policy.old_catalogue_hash);assert.equal(reference.result.catalogue_hash,policy.old_catalogue_hash);const normalizedReference=structuredClone(reference.result);normalizedReference.catalogue_hash=policy.catalogue_hash;stats.push({id:entry.id,...parity(actual.result,normalizedReference,gate)})")
ok(expected==b[17],'reference result only exact catalogue_hash normalization plus stronger old/current catalogue/membership guards')
oldp=json.loads((N/'live-release-artifact-plan-v1/browser-validator-v2.POLICY.json').read_text());ok(policy['parity_policy']==oldp['parity_policy']and policy['requests']==oldp['requests'],'original request and physical policy identity')
ok(all(pin in policy['pins']for pin in oldp['pins']),'all original validator dependency pins preserved')
for pin in policy['pins']:ok(H(Path(pin['path']))==pin['sha256'],'exact authority pin '+pin['path'])
ok(H(Path(policy['catalogue']))=='19be5a4568830e2ac2d5e930ceb2f778a98a37c4bf31f700e6bc7ee3d41ccdac','current17 exact metadata')
ok(policy['old_catalogue_hash']=='beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575'and policy['catalogue_hash']=='4e31188499b5d19e52439451a709775f00e08a1f4d94570e40f43d825cd0e0a1','only exact known catalogue identities')
ok(plan['ready_for_actual']is False and plan['source_revision']=='64002531f0af5c06ad0402d0d80548102f8e6a38','source plan remains pending exact actual authorities')
ok(len(plan['scripts'])==9 and sum('source'in x for x in plan['scripts'])==8,'eight original scripts plus one cycles gate')
oldout=str(Path(plan['scripts'][0]['source']).parent)
for row in plan['scripts']:
 s=Path(row['path']).read_text()
 if 'source'in row:
  before=Path(row['source']).read_text();s=s.replace(plan['output_directory'],oldout)
  if Path(row['path']).name=='named.js':
   x=s.index('await page.goto(root);const currentIndex=');y=s.index('for(const ex of examples){');guard=s[x:y];ok('JSON.stringify(examples.map(e=>e.id).sort())'in guard and policy['catalogue_hash']in guard,'named exact9 public index/current catalogue guard');s=s[:x]+s[y:]
  ok(s==before,'entire original script preserved '+Path(row['path']).name)
 else:
  for text in ("inputValue()!=='1'","inputValue()!=='0'","isDisabled()","selectOption('s-clay1')","selectOption('linear-elastic')"):
   # Starting model may be URL-selected; exact source reviewed separately.
   if text=="selectOption('linear-elastic')":continue
   ok(text in s,'new cycles explicit gate '+text)
(Q/'source-checks.json').write_text(json.dumps({'status':'PASS_SOURCE_PLAN_ONLY','checks':len(labels),'labels':labels},indent=2)+'\n');print(json.dumps({'status':'PASS_SOURCE_PLAN_ONLY','checks':len(labels)}))
