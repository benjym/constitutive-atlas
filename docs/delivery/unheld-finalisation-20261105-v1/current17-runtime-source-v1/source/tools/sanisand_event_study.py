"""Bounded Python-only decision fixtures; no constitutive trajectory integration."""
import argparse, copy, gzip, hashlib, json, math
from pathlib import Path
from atlas.dsl import I,Sym,ValidationError,dev,dot,trace
from atlas.model import ROOT,defaults,load,prepare_increment
from tools.sanisand_elastic_entry import elastic_point,first_yield
from tools.inspect_sanisand_limit import load_fragment,evaluate_fragment
from tools.verify_sanisand_fixed_memory import unpack
MODEL='models/research/sanisand-2004-parent-reset-be.json'
RAW='catalogue/investigations/sanisand-parent-reset-v1/trajectories.json.gz'
def clean(x):
    if isinstance(x,Sym):return list(x.v)
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x
def digest(x):return hashlib.sha256(json.dumps(clean(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def norm(x):return math.sqrt(sum(v*v for v in x))
def guard(state,inc):return sum((a-b)*v for a,b,v in zip(state['alpha'],state['alpha_in'],dev(Sym(tuple(inc))).v))
def limit_input(distance,sign=1):
    n=[.4,-.1,-.3,.7,-.2,.1];l=norm(n);n=[v/l for v in n]
    # alpha=0 avoids cancellation of tiny anchor distances.
    radius=math.sqrt(2/3)*.01
    return dict(sigma=Sym(tuple(1e5*((1 if i<3 else 0)+radius*v) for i,v in enumerate(n))),
                alpha=Sym((0.,)*6),alpha_in=Sym(tuple(-distance*v for v in n)),
                z=Sym(tuple(-.4*v for v in n)),e=.7,
                d_epsilon=Sym(tuple(sign*(1e-4*v+(1e-5 if i<3 else 0)) for i,v in enumerate(n))))
def generate():
    model=load(ROOT/MODEL);params=defaults(model)
    files=[MODEL,RAW,'tools/sanisand_elastic_entry.py','tools/inspect_sanisand_limit.py',
      'tools/inspect_sanisand_original.py','atlas/dsl.py','atlas/model.py','atlas/structure.py','atlas/compiler.py',
      'schemas/model.schema.json','tools/verify_sanisand_fixed_memory.py',
      'catalogue/source-audits/sanisand-2004-hardening-limit.json',
      'catalogue/source-audits/sanisand-2004-original-equations.json',
      'catalogue/source-audits/original-papers-2026-10-31.json']
    hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
    result=dict(scope='Project-authored Python decision fixtures, not canonical event rules, full trajectory or scientific validation',
      conventions='Compression positive, zero spin, six-component Mandel tensors; stress Pa; strain dimensionless',
      model=MODEL,parameters=params,parameter_sha256=digest(params),files_sha256=hashes,
      source_locations=dict(elasticity='Dafalias-Manzari 2004 Eq3 p623',yield_surface='Eqs13-17 pp627-628',
        hardening_reset='Eq24 and following paragraph p631',fabric='Eqs26-27 p631',
        opensees_anchor='commit 8a0273db3e2f5a14c05924a179c1e439500c852c ManzariDafalias.cpp L858-893'),
      limitations=['Elastic entry assumes fixed alpha and full valid elastic predictor; no plastic continuation.',
        'Hardening helper is an existing project algebraic on-cone derivation, not independent external validation.',
        'Parent selection comparison freezes physical state: no trajectories or partition error are inferred.',
        'No canonical reset selection; 1986 loading-process source review remains open.'])
    sigma=I*1e5;alpha=Sym((0.,)*6);e=.7
    entry=[]
    elastic=dict(G0=params['G0'],nu=params['nu'],p_at=params['p_at'])
    for name,strain in [('constant-volume',Sym((.0001,-.00005,-.00005,.0002,-.0001,.00005))),
                        ('mixed-volume',Sym((.001,.0003,-.0001,.0004,-.0002,.0001)))]:
        inputs=dict(sigma=sigma,e=e,alpha=alpha,strain=strain,m=params['m'],G0=params['G0'],nu=params['nu'],p_at=params['p_at'])
        ev=first_yield(sigma,e,alpha,strain,m=params['m'],G0=params['G0'],nu=params['nu'],p_at=params['p_at'])
        split=ev['lower']['fraction']/2
        mid,em=elastic_point(sigma,e,strain,split,**elastic)
        rest=first_yield(mid,em,alpha,strain*(1-split),m=params['m'],**elastic)
        record=dict(name=name,inputs=inputs,input_sha256=digest(inputs),event=ev,
                    elastic_partition_fraction=split,partition_state=dict(sigma=mid,e=em),
                    recomposed_upper_fraction=split+(1-split)*rest['upper']['fraction'])
        if name=='constant-volume':
            G=params['G0']*params['p_at']*(2.97-e)**2/(1+e)*math.sqrt(1e5/params['p_at'])
            record['analytic_fraction']=math.sqrt(2/3)*params['m']*1e5/(2*G*norm(strain.v))
        entry.append(record)
    result['elastic_entry']=entry
    rows=json.loads(gzip.decompress((ROOT/RAW).read_bytes()))
    peak=next(r for r in rows if (r['path'],r['steps'],r['leg'],r['step'])==(0,16,0,15))
    parent=unpack(model,peak['state']);p=sum(parent['sigma'][:3])/3
    delta=[parent['sigma'][i]/p-(1 if i<3 else 0)-parent['alpha'][i] for i in range(6)]
    normal=[v/norm(delta) for v in delta];memory=[a-b for a,b in zip(parent['alpha'],parent['alpha_in'])]
    forward=peak['increment'];reverse=[-v for v in forward]
    directions=dict(forward=forward,reverse=reverse,zero=[0.]*6,transverse=[0.,0.,0.,1e-5,0.,0.],
                    oblique_reverse=[v+(1e-5 if i==3 else 0) for i,v in enumerate(reverse)])
    selection=[]
    for name,inc in directions.items():
        before=copy.deepcopy(parent);prepared=prepare_increment(model,parent,inc)
        assert before==parent
        selection.append(dict(name=name,increment=inc,guard=guard(parent,inc),
            reset=prepared['alpha_in']!=parent['alpha_in'],prepared=prepared,
            preserved_fabric=prepared['fabric']==parent['fabric'],input_sha256=digest(dict(parent=parent,increment=inc))))
    whole=[a+2*b for a,b in zip(reverse,forward)]
    result['reversal_selection']=dict(retained_row=dict(path=0,steps=16,leg=0,step=15),parent=parent,
      parent_sha256=digest(parent),source_local_cone_guard=sum(a*b for a,b in zip(memory,normal)),
      normal=normal,selection=selection,
      partition_selection=dict(definition='Selection only at the same frozen physical peak; independent calls, not sequential constitutive updates.',
        components=[reverse,[2*v for v in forward]],sum_increment=whole,
        unsplit_guard=guard(parent,whole),split_first_guard=guard(parent,reverse),
        unsplit_anchor=prepare_increment(model,parent,whole)['alpha_in'],
        split_first_anchor=prepare_increment(model,parent,reverse)['alpha_in']))
    fragment=load_fragment(ROOT);limit_rows=[]
    result['hardening_scalar_defaults']={k:v['default'] for k,v in fragment['inputs'].items() if v['shape']!='sym' and 'default' in v}
    result['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for sign in [1,-1]:
        zero=evaluate_fragment(fragment,**limit_input(0,sign))
        for distance in [0.,1e-3,1e-5,1e-7,1e-9,1e-12]:
            inputs=limit_input(distance,sign);out=evaluate_fragment(fragment,**inputs)
            b=[v-w for v,w in zip(out['alpha_b'].v,inputs['alpha'].v)]
            N=[v-(dot(out['n'],out['r'])/3 if i<3 else 0) for i,v in enumerate(out['n'].v)]
            elastic=[2*out['G']*v+(out['K']*out['volumetric_increment'] if i<3 else 0) for i,v in enumerate(out['de'].v)]
            A=sum(v*w for v,w in zip(N,elastic));expected=[v*max(A,0)/(out['p']*sum(v*w for v,w in zip(b,out['n'].v))) for v in b]
            limit_rows.append(dict(sign=sign,distance=distance,inputs=inputs,input_sha256=digest(inputs),output=out,
              zero_limit_alpha=expected,alpha_error_to_zero=norm([v-w for v,w in zip(out['backstress_increment'].v,zero['backstress_increment'].v)]),
              yield_consistency_defect=sum(v*w for v,w in zip(N,out['stress_increment'].v))-out['p']*dot(out['n'],out['backstress_increment'])))
    result['hardening_limit']=limit_rows
    rejected=[]
    for name,inputs in [('negative-distance',limit_input(-.01)),('nonpositive-Hbar-zero',dict(limit_input(0),M=.01,c=1.,lambda_c=0.,e0=.7))]:
        try:evaluate_fragment(fragment,**inputs)
        except ValidationError as exc:rejected.append(dict(name=name,inputs=inputs,input_sha256=digest(inputs),error=str(exc)))
        else:raise AssertionError('expected domain rejection')
    result['rejections']=rejected
    return clean(result)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='Explicit destination JSON file')
    args=parser.parse_args()
    data=generate()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('Wrote',args.output)

if __name__=='__main__':main()
