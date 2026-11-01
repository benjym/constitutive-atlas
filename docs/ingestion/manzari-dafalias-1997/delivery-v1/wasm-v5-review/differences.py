"""Descriptive differences only; frozen parity gates make acceptance decisions."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,math
D=Path(__file__).resolve().parent
T=Path('/private/tmp/atlas-control-partition-v1')
a=json.loads((T/'md-native-v5/report.json').read_text());b=json.loads((T/'md-wasm-v5/report.json').read_text())
state=[0.]*14;strain=[0.]*6;points=0;different=0
for name,ca in a['cases'].items():
    cb=b['cases'][name];assert len(ca['points'])==len(cb['points'])
    for pa,pb in zip(ca['points'],cb['points']):
        assert pa['coordinate']==pb['coordinate'];points+=1
        for field,length,target in [('state',14,state),('strain',6,strain)]:
            assert len(pa[field])==len(pb[field])==length
            for j,(x,y)in enumerate(zip(pa[field],pb[field])):
                assert math.isfinite(x)and math.isfinite(y)
                different+=x!=y;target[j]=max(target[j],abs(x-y))
max_ad=max(abs(x-y)for ra,rb in zip(a['special']['linearize']['state_tangent'],b['special']['linearize']['state_tangent'])for x,y in zip(ra,rb))
(D/'differences.json').write_text(json.dumps({'scope':'Descriptive point/tangent differences only; no new acceptance tolerance or qualification claim.','case_count':len(a['cases']),'point_pairs':points,'nonidentical_state_or_strain_scalar_pairs':different,'maximum_absolute_state_differences_by_index':state,'maximum_absolute_strain_differences_by_index':strain,'maximum_absolute_AD_tangent_difference':max_ad,'compiled_calls':0},indent=2)+'\n')
print(json.dumps({'point_pairs':points,'max_stress_difference_Pa':max(state[:6]),'max_AD_difference':max_ad}))
