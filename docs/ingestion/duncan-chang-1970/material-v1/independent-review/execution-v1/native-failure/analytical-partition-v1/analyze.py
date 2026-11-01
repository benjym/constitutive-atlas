"""Independent source roots on actual binary64 alternate-partition loads; no engine."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import json, runpy, hashlib, math
B=Path(__file__).resolve().parents[4]; E=B/'execution-v1'
R=runpy.run_path(str(B/'reference.py')); q=R['q']
def run(precision=100):
 requests=json.loads((E/'requests.json').read_text()); observed=json.loads((E/'native-results.json').read_text()); rows=[]
 with localcontext() as ctx:
  ctx.prec=precision
  for path,raw in zip(requests['paths'],observed['paths']):
   if not path['id'].startswith('loose-max-crossing-'): continue
   idx,call=next((i,c) for i,c in enumerate(raw['calls']) if not json.loads(c['stdout'])['ok'])
   initial=list(map(float,call['args'][2].split(','))); parent=list(map(float,call['args'][3].split(','))); p=path['parameters']; prior=json.loads(call['stdout'])['diagnostics']['substeps']
   nu=q(p['nu']); pa=q(p['pa']); n=q(p['n']); rf=q(p['Rf']); alpha=2*R['sin'](q(p['phi']))/(1-R['sin'](q(p['phi'])))
   assert p['c_cohesion']==0 and initial[1]==initial[2] and parent[1]==parent[2] and all(x==0 for x in parent[3:])
   U=q(p['Kur'])*pa; A=q(p['K'])*pa
   def bisect(f,lo,hi):
    fl=f(lo); fh=f(hi)
    if fl==0:return lo
    if fh==0:return hi
    if fl*fh>0:return None
    for _ in range(240):
     mid=(lo+hi)/2
     if f(mid)>0:hi=mid
     else:lo=mid
    return (lo+hi)/2
   def root(z,de):
    tr=sum(map(q,de[:3])); shape=[q(de[i])/(1+nu)+nu*tr/((1+nu)*(1-2*nu)) for i in range(3)]
    k=shape[0]-shape[1]; br=shape[1]; old=z[0]-z[1]; h=z[6]; c=z[1]
    assert k>0 and k*c-old*br>0
    def conf(m):return c+m*br/2
    def sat(m):return (old+m*k/2)/(alpha*conf(m))
    def unload(m):return m-U*(conf(m)/pa)**n
    def primary(m):return m-A*(conf(m)/pa)**n*(1-rf*sat(m))**2
    boundary=(h-old)/k; strength=2*(alpha*c-old)/(k-alpha*br)
    # Roots on the open unloading branch and closed primary history branch.
    candidates=[]
    if boundary>0:
     m=bisect(unload,D(0),boundary)
     if m is not None and old+m*k<h:candidates.append((m,'unloading'))
    lo=max(D(0),boundary)
    if strength>lo:
     m=bisect(primary,lo,strength)
     if m is not None and old+m*k>=h and sat(m)<1:candidates.append((m,'primary'))
    m=q(p['E_failure'])
    if old+m*k>=h and sat(m)>=1:candidates.append((m,'postfailure'))
    assert len(candidates)<=1
    if not candidates:return None
    m,branch=candidates[0]; out=[z[i]+m*shape[i] for i in range(3)]+[D(0)]*3+[D(0)]
    out[6]=max(h,out[0]-out[1])
    err=abs(unload(m) if branch=='unloading' else primary(m) if branch=='primary' else m-q(p['E_failure']))
    assert conf(m)>0 and out[6]>=out[0]-out[1]
    return out,branch,m,err
   variants=[]
   for encoded in [False,True]:
    leaves=[]; rejected=[]; maxdepth=0
    def recurse(z,de,depth,fraction):
     nonlocal maxdepth
     maxdepth=max(depth,maxdepth); found=root(z,de)
     if found is not None:
      out,branch,m,err=found
      if encoded:
       out=[q(float(x)) for x in out]
       # Conservative binary encoding of the maximum history, same exact
       # diagonal principal difference; no stress projection.
       exact=max(z[6],out[0]-out[1]); hf=float(exact)
       if q(hf)<exact:hf=math.nextafter(hf,math.inf)
       out[6]=q(hf)
      source_branch=R['quantities'](out,z,p)[2]
      assert source_branch==('unload_reload' if branch=='unloading' else branch)
      residual=max(map(abs,R['residual'](out,z,de,p)))
      assert residual/q(p['p_ref'])<D('2e-10')
      leaves.append({'source_residual_max_over_p_ref':str(residual/q(p['p_ref'])),'depth':depth,'fraction':str(fraction),'branch':branch,'de':[x.hex() for x in de],'modulus':str(m),'modulus_equation_error':str(err),'D':str(out[0]-out[1]),'h':str(out[6])})
      return out
     rejected.append(depth)
     if depth>=14:return None
     left=[x*.5 for x in de]; first=recurse(z,left,depth+1,fraction/2)
     if first is None:return None
     return recurse(first,left,depth+1,fraction/2)
    left=[x/3.0 for x in parent]; right=[x-y for x,y in zip(parent,left)]
    defect=[q(a)+q(b)-q(c) for a,b,c in zip(left,right,parent)]
    assert all(a+b==c for a,b,c in zip(left,right,parent))
    first=recurse(list(map(q,initial)),left,1,D(1)/3)
    final=None if first is None else recurse(first,right,1,D(2)/3)
    variants.append({'continuation':'binary64 stress with history rounded upward' if encoded else '100-digit continuous source stress/history','success':final is not None,'accepted_leaf_count':len(leaves),'discarded_original_substeps':prior,'global_attempted_accepted_steps':prior+len(leaves),'within_20000_budget':prior+len(leaves)<=20000,'max_depth_visited':maxdepth,'no_root_node_depths':rejected,'actual_root_partition_defect':list(map(str,defect)),'nominal_fraction_sum':str(sum(D(x['fraction']) for x in leaves)),'final_state':None if final is None else list(map(str,final)),'leaves':leaves})
   rows.append({'id':path['id'],'failed_call_index':idx,'variants':variants})
 inputs=[E/'requests.json',E/'native-results.json',B/'reference.py',Path('docs/reviews/bounded-partition-retry-v1/CONTRACT.md')]
 return {'identity':'independent-analytical-third-partition-v1','compiled_calls':0,'decimal_precision':precision,'rows':rows,'bindings':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs}}
if __name__=='__main__':print(json.dumps(run(),indent=2))
