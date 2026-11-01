"""Hand-derived geometric witnesses; no Atlas/author/compiled code imports."""
from copy import deepcopy
import json
from math import sqrt
from reference import prepare, trial, validate, PROFILE


def main():
    checks = []
    def require(name, condition):
        if not condition:
            raise RuntimeError(name)
        checks.append(name)
    def advance(s,x):
        return trial(s,[a-b for a,b in zip(x,s['x'])])
    def at(s,k,center,radius):
        return s['contours'][k] == {'center':center,'radius':radius}
    s0 = prepare()
    s1,e = advance(s0,[8.,0.,0.])
    require('primary fixed-center monotonic growth',e=='grow-active' and at(s1,0,[0.,0.,0.],8.))
    s2,e = advance(s1,[4.,0.,0.])
    require('first reversal midpoint and radius',e=='create' and at(s2,1,[6.,0.,0.],2.) and s2['anchor']==[8.,0.,0.])
    s3,e = advance(s2,[6.,0.,0.])
    require('second nested reversal',e=='create' and at(s3,2,[5.,0.,0.],1.) and s3['anchor']==[4.,0.,0.])
    s4,e = advance(s3,[5.,0.,0.])
    require('four-contour depth',e=='create' and at(s4,3,[5.5,0.,0.],.5) and len(s4['contours'])==4)
    s5,e = advance(s4,[5.25,0.,0.])
    require('fifth inward event retains four contours',e=='depth-saturated' and s5['contours']==s4['contours'] and s5['gamma']==.25)
    s6,e = advance(s5,[6.,0.,0.])
    require('outer equality erases innermost contour',e=='erase-inner' and len(s6['contours'])==3 and s6['anchor']==[4.,0.,0.])
    s7,e = advance(s6,[8.,0.,0.])
    require('outermost priority restores primary contour',e=='erase-inner' and len(s7['contours'])==1 and s7['anchor']==[0.,0.,0.])
    held,e=trial(s7,[0.,0.,0.])
    require('hold at exact outer boundary is no-op',held==s7 and e=='hold')
    tiny,e=trial(s2,[1e-13,-1e-13,1e-13])
    require('source-rounded subthreshold increment is no-op',tiny==s2 and e=='hold')
    threshold,e=trial(s0,[1e-12,0.,0.])
    require('threshold equality is retained',threshold['x'][0]==1e-12 and e=='grow-active')
    a,e=advance(s2,[2.,0.,0.])
    require('nested active contour midpoint growth',at(a,1,[5.,0.,0.],3.) and a['anchor']==[8.,0.,0.] and e=='grow-active')
    a,_=advance(s0,[2.,4.,4.]); b,e=advance(a,[1.,2.,2.])
    require('three-dimensional half-chord geometry',e=='create' and at(b,1,[1.5,3.,3.],1.5) and b['gamma']==1.5)
    # Norm uses all three components; no planar/one-dimensional assumption.
    a,e=advance(s0,[1.,2.,3.])
    require('non-rational three-dimensional distance',a['gamma']==sqrt(14.))
    before=deepcopy(s2)
    proposal,_=trial(s2,[1.,0.,0.])
    require('trial leaves committed state unchanged',s2==before)
    proposal['contours'][0]['radius']=999.
    require('trial does not alias nested committed memory',s2==before)
    outer_a,_=trial(s2,[1.,0.,0.]); outer_b,_=trial(s2,[1.,0.,0.])
    require('outer-pass replay from parent is idempotent',outer_a==outer_b and s2==before)
    invalid=[float('nan'),0.,0.]
    rejected=False
    try: trial(s2,invalid)
    except ValueError: rejected=True
    require('nonfinite rejection preserves parent',rejected and s2==before)
    # A later plane fails: no partial transaction is returned or published.
    committed=[deepcopy(s1),deepcopy(s2)]
    frozen=deepcopy(committed); outputs=[]
    try:
        outputs=[trial(p,d)[0] for p,d in zip(committed,[[1.,0.,0.],invalid])]
    except ValueError: outputs=[]
    require('failed multi-plane proposal publishes nothing',outputs==[] and committed==frozen)
    restarted=json.loads(json.dumps(s4,allow_nan=False));validate(restarted)
    require('restart preserves nested full-state continuation',trial(restarted,[.25,0.,0.])==trial(s4,[.25,0.,0.]))
    # Explicit contrast to the source iStep<=1 creation gate, not equivalence.
    first,_=trial(s1,[-4.,0.,0.],creation_permitted=True)
    later,_=trial(s1,[-4.,0.,0.],creation_permitted=False)
    require('literal host-step gate changes identical geometric path',len(first['contours'])==2 and len(later['contours'])==1)
    # Do not assert phase invariance from a loop whose labels are unused.
    # The corrected profile has no phase input; the counterexample above is
    # the discriminating behavioral check against the literal source gate.
    # Recovery's external failure policy is deliberately not solved by this packet.
    no_create,e=trial(s1,[-4.,0.,0.],creation_permitted=False)
    require('explicit inhibited creation retains active memory',len(no_create['contours'])==1 and e=='inside-active')
    require('old snapshots untouched after full fixture sequence',s0==prepare() and s2==before)
    malformed=prepare(); malformed['x']=[1e308,0.,0.]
    rejected=False
    try: validate(malformed)
    except ValueError: rejected=True
    require('reviewer overflow restart counterexample rejected',rejected)
    huge=prepare();huge['x']=[1e308,0.,0.];huge['gamma']=1e308
    huge['contours'][0]['radius']=1e308
    validate(huge)
    require('large consistent finite restart retains stable distance',trial(huge,[0.,0.,0.])[0]==huge)
    frozen_huge=deepcopy(huge);rejected=False
    try: trial(huge,[1e308,0.,0.])
    except ValueError: rejected=True
    require('overflowing finite increment rejects without mutation',rejected and huge==frozen_huge)
    outside=prepare();outside['x']=[8.,0.,0.];outside['gamma']=8.
    rejected=False
    try: validate(outside)
    except ValueError: rejected=True
    require('restart endpoint outside stored radius rejected',rejected)
    corrupt=deepcopy(s2);corrupt['contours'][0]['radius']=1.
    rejected=False
    try: validate(corrupt)
    except ValueError: rejected=True
    require('restart endpoint outside inactive outer radius rejected',rejected)
    return {'status':'PASS','profile':PROFILE,'checks':checks,'count':len(checks),
            'scope':'geometry/transaction contract, not a material solver or Masing qualification',
            'retained_source_counterexample':{'same_path':[0,8,4], 'source_step_1_contours':2,'source_step_10_contours':1}}


if __name__=='__main__':
    print(json.dumps(main(),indent=2,allow_nan=False))
