"""Offline consistency checks for the bounded public recorded-replay capture.

This supplements analytical/native tests; it does not establish constitutive
accuracy, stress continuity between endpoints, or independent scientific review.
"""
import hashlib
import json
import math
from atlas.recorded import (CONTROL_DEFAULTS, MATERIAL_DEFAULTS, recorded_wire)


def verify(rows):
    if len(rows)!=16:raise ValueError('incomplete recorded API capture')
    successful=failed=points=0
    catalogue=None
    for row in rows:
        spec,r=row['request'],row['response'];c,k=recorded_wire(spec)
        digest=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        if r.get('request_sha256')!=digest or r.get('specification')!=spec:raise ValueError('request provenance differs')
        if r.get('api_version')!='experimental-recorded-replay-0.1' or r.get('model')!=spec['model']:raise ValueError('wrong API/model')
        if r.get('controls_wire')!=c or r.get('knots_wire')!=k:raise ValueError('wire changed path')
        if catalogue is None:catalogue=r['catalogue_hash']
        if r['catalogue_hash']!=catalogue:raise ValueError('catalogue changed within capture')
        expected=MATERIAL_DEFAULTS|spec.get('integration_settings',{})
        if any(r['integration_settings'][key]!=v for key,v in expected.items()):raise ValueError('material settings changed')
        control=CONTROL_DEFAULTS|spec.get('control_settings',{})
        if r['control_settings']!=control:raise ValueError('control settings changed')
        if r['initial_strain']!=spec['path']['initial_strain']:raise ValueError('strain origin changed')
        for field in ('initial','parameters'):
            if field in spec and r[field]!=spec[field]:raise ValueError('explicit initial/parameters changed')
        pts=r['points'];knots=spec['path']['knots'];points+=len(pts)
        if r['ok']:
            successful+=1
            if len(pts)!=len(knots) or r['failed_knot']!=-1:raise ValueError('incomplete success')
        else:
            failed+=1
            if r['failed_knot']>=0 and r['failed_knot']!=len(pts):raise ValueError('failure index/prefix mismatch')
        if pts:
            if r['state']!=pts[-1]['state'] or r['strain']!=pts[-1]['strain']:raise ValueError('rollback/final state mismatch')
            if pts[0]['state']!=r['initial'] or pts[0]['strain']!=r['initial_strain']:raise ValueError('implicit preparation')
        elif r['state']!=r['initial'] or r['strain']!=r['initial_strain']:raise ValueError('invalid request changed parent')
        # Every retained specimen uses stress scale p_ref=100 kPa (and no
        # initial component exceeds it), independently pinned in this capture.
        if r['parameters'][0]!=100000 or max(map(abs,r['initial'][:6]))>100000:raise ValueError('outside verifier stress-scale scope')
        for i,(pt,knot) in enumerate(zip(pts,knots)):
            if pt['coordinate']!=knot['coordinate']:raise ValueError('record order changed')
            if not all(math.isfinite(x) for x in pt['state']+pt['strain']):raise ValueError('nonfinite accepted state')
            if len(pt['state'])!=len(r['initial']) or len(pt['strain'])!=6:raise ValueError('state shape changed')
            error=0
            for j,ctrl in enumerate(spec['path']['controls']):
                scale=max(map(abs,ctrl['coefficients']));values=pt['state'][:6] if ctrl['kind']=='stress' else pt['strain']
                residual=sum(a/scale*b for a,b in zip(ctrl['coefficients'],values))-knot['targets'][j]/scale
                error=max(error,abs(residual)/(100000 if ctrl['kind']=='stress' else 1))
            if error>control['control_tolerance']+1e-14:raise ValueError('endpoint target violated')
            if i and knots[i]['targets']==knots[i-1]['targets']:
                if pt['state']!=pts[i-1]['state'] or pt['strain']!=pts[i-1]['strain'] or pt['diagnostics']['substeps']!=0:raise ValueError('duplicate observation mutated history')
    if (successful,failed)!=(13,3):raise ValueError('missing success/failure branches')
    return dict(ok=True,cases=len(rows),successful=successful,failed=failed,accepted_points=points,
                scope='Public native endpoint/provenance consistency; analytical oracles are separate tests.')
