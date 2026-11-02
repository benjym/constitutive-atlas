#!/usr/bin/env python3
"""Source-only composition from frozen git-show inputs. No index/worktree mutation."""
from pathlib import Path
import json,re,subprocess,hashlib,ast
P=Path(__file__).resolve().parent
refs=json.loads((P/'three-way-status.json').read_text())['refs']
def text(side,f):return (P/'inputs'/side/f).read_text()
def save(f,s):
 q=P/'proposed'/f;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
def three(b,a,c):
 if a==c:return a
 if a==b:return c
 if c==b:return a
 if all(isinstance(x,dict) for x in (b,a,c)):
  out={}
  for k in list(c)+[k for k in a if k not in c]:
   if k not in b:
    if k in a and k in c:assert a[k]==c[k],k
    out[k]=a[k] if k in a else c[k]
   else:
    assert k in a and k in c,'unsupported deletion'
    out[k]=three(b[k],a[k],c[k])
  return out
 if all(isinstance(x,list) for x in (b,a,c)) and all(isinstance(y,dict) and 'id' in y for x in (b,a,c) for y in x):
  bd={x['id']:x for x in b};ad={x['id']:x for x in a};cd={x['id']:x for x in c};merged=three(bd,ad,cd)
  return list(merged.values())
 raise AssertionError('unresolved semantic conflict')
# Both narrative changes are strict append-only; preserve each exact suffix.
for f in ['ROADMAP.md','docs/STATUS.md']:
 b=text('base',f);a=text('interface',f);c=text('published',f);assert a.startswith(b) and c.startswith(b);save(f,c+a[len(b):])
# Registry and catalogue: semantic three-way by persistent entry id.
for f in ['catalogue/approved-models.json','catalogue/manifest.json']:
 b,a,c=[json.loads(text(side,f)) for side in ['base','interface','published']];d=three(b,a,c)
 save(f,json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# Independent CLI additions: retain both argument declarations.
f='tools/build_web.py';s=(P/'automatic'/f).read_text();s=re.sub(r'^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n',lambda m:m[1]+m[2],s,flags=re.S|re.M);ast.parse(s);save(f,s)
# App: start published; splice only the interface import, own technical branch and controller.
f='web/app.js';b=text('base',f);a=text('interface',f);c=text('published',f)
importline="import {setupInterface2016Laboratory} from './interface2016-laboratory.mjs';\n";assert importline in a and importline not in c;c=importline+c
marker="}else if(entry.path_laboratory&&timedView?.supports(entry.id))"
start=a.index("}else if(entry.id==='hvwe2016-reconciled-fixed-local'");end=a.index(marker,start);branch=a[start:end]
assert c.count(marker)==1;c=c.replace(marker,branch+marker,1)
controller="setupInterface2016Laboratory({chart,cancelOrdinary:()=>cancel('')}),";router='createLaboratoryControllerRouter([';assert a.count(controller)==1 and c.count(router)==1;c=c.replace(router,router+controller,1);save(f,c)
# Profiles: preserve raw published entries, replace only the authorized family profile and append exact runnable entry.
f='web/model-profile-data.mjs';a=text('interface',f);c=text('published',f)
def entry(s,key):
 match=re.search(r'^  '+re.escape(json.dumps(key))+r': ',s,re.M);assert match
 _,n=json.JSONDecoder().raw_decode(s[match.end():]);return match.start(),match.end()+n
key='hypoplastic-interface-2016';aa,az=entry(a,key);ca,cz=entry(c,key);c=c[:ca]+a[aa:az]+c[cz:]
aa,az=entry(a,'hvwe2016-reconciled-fixed-local');last=c.rindex('\n};');c=c[:last]+',\n'+a[aa:az]+c[last:];save(f,c)
# Workflow auto-merge is already conflict-free and combines disjoint original steps.
f='.github/workflows/verify.yml';save(f,(P/'automatic'/f).read_text())
# Preserve exact branch/base shared-source context, whether or not current receipts need it.
archives=[]
for f in sorted(x['path'] for x in json.loads((P/'three-way-status.json').read_text())['overlap']):
 for side in ['base','interface','published']:
  source=P/'inputs'/side/f;b=source.read_bytes();sha=hashlib.sha256(b).hexdigest();target=P/'proposed/catalogue/source-snapshots'/sha/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
  archives.append({'original_path':f,'archived_path':str(target.relative_to(P/'proposed')),'sha256':sha,'resolved_commit':refs[side]})
(P/'archive-contexts.json').write_text(json.dumps(archives,indent=2)+'\n')
print('Eight shared files composed; exact original contexts retained under proposal/source-snapshots.')
if __name__=='__main__':pass
