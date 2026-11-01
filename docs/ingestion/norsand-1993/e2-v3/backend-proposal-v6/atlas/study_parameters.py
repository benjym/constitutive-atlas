"""Complete study parameter accounting, separate from constitutive admission."""
import math
import re
from urllib.parse import urlsplit
from .study_allocation import require


def number(value, label):
    require(type(value) in (int,float), label + ': finite number required, excluding bool')
    try: valid=math.isfinite(value)
    except OverflowError: valid=False
    require(valid, label + ': finite number required')
    return value


def validate_parameter_policy(policy, definitions, *, allocation_sha256, definition_sha256):
    keys={'schema_version','kind','id','phase','allocation_sha256','models','limitations'}
    require(isinstance(policy,dict) and set(policy)==keys, 'unsupported parameter-policy fields')
    require(policy['schema_version']=='0.1' and policy['kind']=='study-parameter-policy'
            and policy['phase']=='historical_development', 'unsupported parameter-policy scope')
    require(isinstance(policy['id'],str) and re.fullmatch(r'[a-z][a-z0-9-]*',policy['id']) is not None, 'invalid parameter-policy ID')
    require(isinstance(policy['allocation_sha256'],str) and re.fullmatch(r'[a-f0-9]{64}',policy['allocation_sha256']) is not None
            and policy['allocation_sha256']==allocation_sha256, 'whole-test allocation identity mismatch')
    require(isinstance(policy['limitations'],list) and bool(policy['limitations']) and all(isinstance(x,str) and bool(x) for x in policy['limitations']), 'explicit parameter-policy limitations required')
    require(isinstance(policy['models'],list) and bool(policy['models']), 'model parameter policies required')
    reports=[];seen=set()
    for record in policy['models']:
        require(isinstance(record,dict) and set(record)=={'id','definition_sha256','parameters'}, 'exact model identity and parameter map required')
        mid=record['id']
        require(isinstance(mid,str) and re.fullmatch(r'[a-z][a-z0-9-]*',mid) is not None, 'invalid model ID')
        require(mid not in seen, 'duplicate model parameter policy: '+mid);seen.add(mid)
        require(mid in definitions and mid in definition_sha256, 'missing model definition: '+mid)
        require(record['definition_sha256']==definition_sha256[mid], 'model definition identity mismatch: '+mid)
        definition=definitions[mid]
        require(isinstance(definition,dict) and definition.get('id')==mid and isinstance(definition.get('parameters'),dict), 'model definition parameter inventory missing: '+mid)
        parameters=record['parameters'];declared=definition['parameters']
        require(isinstance(parameters,dict) and bool(parameters) and set(parameters)==set(declared), 'parameter coverage must be exact: '+mid)
        for name,p in parameters.items():
            label=mid+'.'+name
            require(isinstance(p,dict), label+': parameter object required')
            role=p.get('role');require(role in ('fitted','fixed'), label+': explicit fitted/fixed role required')
            common={'role','category','value','unit','provenance'}
            require(set(p)==common|({'bounds','transform'} if role=='fitted' else set()), label+': wrong fields for parameter role')
            require(p['category'] in ('material','numerical_scale','specialization'), label+': unsupported category')
            require(p['unit']==declared[name]['unit'], label+': unit mismatch; no implicit conversion')
            value=number(p['value'],label)
            lower=number(declared[name]['min'],label+' definition min');upper=number(declared[name]['max'],label+' definition max')
            require(lower<=value<=upper, label+': value outside declared model range')
            if role=='fitted':
                bounds=p['bounds'];require(isinstance(bounds,list) and len(bounds)==2, label+': two fit bounds required')
                lo,hi=(number(x,label+' bound') for x in bounds)
                require(lower<=lo<hi<=upper and lo<=value<=hi, label+': invalid fit bounds or seed')
                require(p['transform'] in ('linear','log'), label+': unsupported search transform')
                require(p['transform']!='log' or lo>0, label+': log search requires positive bounds')
            source=p['provenance']
            require(isinstance(source,dict) and {'kind','locator'}<=set(source) and set(source)<={'kind','locator','url'}, label+': provenance required')
            require(source['kind'] in ('definition_default','literature','analyst_choice') and isinstance(source['locator'],str) and bool(source['locator']), label+': explicit provenance kind/locator required')
            if source['kind']=='literature' or 'url' in source:
                require(isinstance(source.get('url'),str), label+': provenance URL required')
                url=urlsplit(source['url']);require(url.scheme in ('http','https') and bool(url.netloc), label+': persistent HTTP source URL required')
            if source['kind']=='definition_default':
                require(value==number(declared[name]['default'],label+' definition default'), label+': value is not the declared default')
        fitted=[n for n,p in parameters.items() if p['role']=='fitted']
        reports.append({'id':mid,'definition_sha256':record['definition_sha256'],
            'fitted_parameters':fitted,'fitted_parameter_count':len(fitted),
            'fixed_material_parameters':[n for n,p in parameters.items() if p['role']=='fixed' and p['category']=='material'],
            'fixed_literature_material_parameters':[n for n,p in parameters.items() if p['role']=='fixed' and p['category']=='material' and p['provenance']['kind']=='literature'],
            'literature_seeded_fitted_parameters':[n for n,p in parameters.items() if p['role']=='fitted' and p['provenance']['kind']=='literature'],
            'numerical_scales':[n for n,p in parameters.items() if p['category']=='numerical_scale'],
            'specializations':[n for n,p in parameters.items() if p['category']=='specialization']})
    require(set(definitions)==seen and set(definition_sha256)==seen, 'extra or missing definition inventory')
    return {'kind':'study-parameter-accounting-check','id':policy['id'],'passed':True,
            'allocation_sha256':allocation_sha256,'models':reports,'scientific_admission':False,
            'limitations':policy['limitations']}
