"""Transport/freeze/corruption checks supplementary to unchanged numerical assessors."""
from pathlib import Path
import copy
import hashlib
import json
import math
import struct

ROOT=Path(__file__).resolve().parent

def validate(d):
    if [c['id'] for c in d['cases']]!=['compression','extension','isotropic']:raise ValueError('case identities')
    for c in d['cases']:
        if c['points']!=c['rk4_refinements'][-1]['points']:raise ValueError('fine alias differs')
        if c['transition_targets']!=c['rk4_refinements'][-1]['transition_targets']:raise ValueError('target alias differs')
        for run in c['rk4_refinements']+[c['midpoint']]:
            if len(run['points'])!=22:raise ValueError('missing observations')
            for q in run['points']:
                for key in ('time','elastic_pressure','elastic_q','pressure','signed_q'):
                    if type(q[key]) not in (float,int) or not math.isfinite(q[key]):raise ValueError('nonfinite or mistyped scalar')
                for key,n in [('state',4),('strain',6),('rate',6)]:
                    if len(q[key])!=n or not all(type(x) in (float,int) and math.isfinite(x) for x in q[key]):raise ValueError('bad vector')
    for group in ('parameters','rates'):
        if group=='parameters':rows=list(d['input_binary64'][group].values())
        else:rows=[r for rates in d['input_binary64'][group].values() for r in rates]
        for r in rows:
            if float.fromhex(r['hex'])!=r['value'] or struct.pack('>d',r['value']).hex()!=r['ieee754_big_endian']:raise ValueError('binary input mismatch')
    return True

def main():
    checks={}
    for folder in (ROOT,ROOT/'refinement-v2'):
        d=json.loads((folder/'references.json').read_text())
        checks[folder.name+':transport']=validate(d)
        freeze=json.loads((folder/'source-freeze.json').read_text())
        checks[folder.name+':freeze']=all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==r['sha256'] for n,r in freeze['files'].items())
    good=json.loads((ROOT/'refinement-v2/references.json').read_text())
    for name,mutate in [
      ('changed fine alias',lambda d:d['cases'][0]['points'][5]['state'].__setitem__(0,999.)),
      ('missing observation',lambda d:d['cases'][0]['midpoint']['points'].pop()),
      ('nonfinite scalar',lambda d:d['cases'][0]['midpoint']['points'][2].__setitem__('pressure',float('nan'))),
      ('boolean scalar',lambda d:d['cases'][0]['midpoint']['points'][2].__setitem__('pressure',True)),
      ('bad binary64',lambda d:d['input_binary64']['parameters']['K'].__setitem__('hex','0x1.0p+0')),
    ]:
        candidate=copy.deepcopy(good);mutate(candidate)
        try:validate(candidate)
        except ValueError:checks['reject:'+name]=True
        else:checks['reject:'+name]=False
    old=json.loads((ROOT/'policy.json').read_text());new=json.loads((ROOT/'refinement-v2/policy.json').read_text())
    checks['only identity and resolutions changed']=all(old[k]==new[k] for k in old if k not in ('identity','rk4_steps_per_second','midpoint_steps_per_second'))
    result={'identity':'terracotta-preparation-hold-transport-audit-v1','checks':checks,'status':'pass' if all(checks.values()) else 'fail'}
    (ROOT/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    if result['status']!='pass':raise SystemExit(1)

if __name__=='__main__':main()
