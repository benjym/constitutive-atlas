"""Opaque controlled-hydro collection and independently referenced assessment.

Raw journals are retained before assessment. A numerical failure is an outcome,
never an instruction to change the frozen protocol or discard a journal.
"""
import argparse
import copy
import json
import math
from pathlib import Path

from tools import clay2014_controlled_reference as reference
from tools import clay2014_path_study as transport

ROOT = reference.ROOT
BASE = 'catalogue/investigations/clay2014-controlled-resolution-v1/'
PROTOCOL = BASE+'protocol-reference.json'
FREEZE = BASE+'collection-freeze.json'
VERSION = 'clay2014-controlled-resolution-observation-v1'
ARTIFACTS = {
    'build/atlas_clay2014_solver': '9468a693877a794c6786f55e42ebeb1384f6913fd52656e00f1d79ed9c67740f',
    'build-wasm/clay2014-paths.js': '0100cc8d8682cef4bda38291361a3bd9bbfd0aaa1ac77de80955ebea42eac92f',
    'build-wasm/clay2014-paths.wasm': '51d95914a56d33302c3d2a32e950079aa713f7d07a9fc1506970d4bcc63dd588',
}
require = reference.require
read = reference.read
sha = reference.sha


def frozen_inputs():
    freeze = read(ROOT/FREEZE)
    for name,pin in freeze['files'].items():
        require(sha(ROOT/name)==pin, 'collection source/reference freeze changed: '+name)
    protocol = read(ROOT/PROTOCOL)
    reference.verify(protocol)
    return protocol,freeze


def request(protocol, point, parent):
    data=protocol['input']
    return {'model': data['model'], 'parameters': data['parameters'].copy(),
            'initial': parent.copy(), 'strain': point['increment'].copy(),
            'settings': protocol['policy']['settings'].copy()}


def verify_artifacts(backend):
    held = {p:pin for p,pin in ARTIFACTS.items() if (p.startswith('build-wasm/') if backend=='wasm' else p.startswith('build/'))}
    for name,pin in held.items():
        require(sha(ROOT/name)==pin, 'receipted executable artifact changed: '+name)
    return held


def collect_native(output):
    protocol,_=frozen_inputs()
    artifacts=verify_artifacts('native')
    output=Path(output);raw=output.with_suffix('.transport.jsonl')
    require(not output.exists() and not raw.exists(), 'fresh observation/journal required')
    output.parent.mkdir(parents=True,exist_ok=True);raw.write_text('')
    receipt={'version':VERSION,'backend':'native','protocol_sha256':sha(ROOT/PROTOCOL),
             'collection_freeze_sha256':sha(ROOT/FREEZE),'artifacts':artifacts,
             'completed':False,'calls':0}
    def save():output.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    save();session=transport.NativeSession(ROOT/'build/atlas_clay2014_solver',raw)
    try:
        session.call({'mode':'describe'})
        for group in protocol['groups']:
            parent=protocol['input']['initial'].copy()
            for point in group['points']:
                response=session.call(request(protocol,point,parent))
                receipt['calls']+=1;save()
                require(type(response)is dict and response.get('ok')is True
                        and transport.vector(response.get('state'),7), 'successful finite chaining response required')
                parent=response['state'].copy()
        receipt['completed']=True
    finally:
        code,stderr,trailing=session.close()
        receipt.update(exit_status=code,stderr=stderr,trailing_stdout=trailing,transport_sha256=sha(raw))
        save()
    verify_artifacts('native')
    require(code==0 and not trailing, 'native termination/transport failure retained')
    return receipt


def audit(receipt, raw_path):
    protocol,_=frozen_inputs()
    require(type(receipt)is dict and receipt.get('version')==VERSION,'observation identity')
    backend=receipt.get('backend');require(backend in ('native','wasm'),'backend identity')
    require(receipt.get('protocol_sha256')==sha(ROOT/PROTOCOL)
            and receipt.get('collection_freeze_sha256')==sha(ROOT/FREEZE),'prospective freeze binding')
    expected_artifacts={p:pin for p,pin in ARTIFACTS.items() if (p.startswith('build-wasm/') if backend=='wasm' else p.startswith('build/'))}
    require(receipt.get('artifacts')==expected_artifacts,'exact historical build-artifact identity')
    require(receipt.get('completed')is True and type(receipt.get('calls'))is int
            and receipt['calls']==315,'complete observation')
    require(type(receipt.get('exit_status'))is int and receipt['exit_status']==0
            and receipt.get('trailing_stdout')=='','successful transport termination')
    require(type(receipt.get('stderr'))is str,'stderr receipt')
    require(sha(raw_path)==receipt.get('transport_sha256'),'raw journal hash')
    rows=[json.loads(line,parse_constant=lambda _:require(False,'nonfinite raw JSON'))
          for line in Path(raw_path).read_text().splitlines()]
    require(len(rows)==316,'descriptor plus complete315-call journal')
    model=transport.load(ROOT/reference.MODEL)
    def parse(row, wanted, descriptor=False):
        require(type(row)is dict and row.get('backend')==backend,'raw backend')
        require(transport.same(row.get('request'),wanted),'raw control/actual-parent chain')
        if backend=='native':
            require(row.get('mode')=='persistent_stream' and row.get('request_line')==transport.stream_line(wanted),'native stream request')
            raw=row.get('stdout')
        else:
            require(row.get('name')==('atlas_describe' if descriptor else 'atlas_integrate_with_settings'),'Wasm ABI name')
            require(row.get('types')==([] if descriptor else ['string']*5),'Wasm ABI types')
            args=row.get('args')
            if descriptor:require(args==[],'descriptor arguments')
            else:
                require(type(args)is list and len(args)==5 and args[0]==wanted['model'],'Wasm ABI arguments')
                for text,key in zip(args[1:],('parameters','initial','strain','settings')):
                    require(type(text)is str and [float(x) for x in text.split(',')]==wanted[key],'Wasm CSV control')
            raw=row.get('raw')
        require(type(raw)is str,'opaque raw response string')
        return json.loads(raw,parse_constant=lambda _:require(False,'nonfinite response'))
    descriptor=parse(rows[0],{'mode':'describe'},True)
    require(transport.same(descriptor.get('models'),[model]) and descriptor.get('sha256')==transport.digest([model]),'runtime declarative model identity')
    index=1;groups=[];failures=[];maximum={'stress':0.,'e':0.}
    def gate(ok,label):
        if not ok:failures.append(label)
    for group in protocol['groups']:
        parent=protocol['input']['initial'].copy();points=[]
        for point in group['points']:
            wanted=request(protocol,point,parent);response=parse(rows[index],wanted);index+=1
            transport.check_response(response,wanted,model)
            state=response['state'];d=response['diagnostics']
            gate(transport.same(d['increment_fractions'],protocol['policy']['required_fractions'])
                 and d['rejected']==0, f"factor{group['factor']}/call{len(points)+1}: controlled mesh")
            delta=[a-b for a,b in zip(state,point['target'])]
            error={'stress':math.hypot(*delta[:6]),'e':abs(delta[6])}
            gate(error['stress']<=protocol['policy']['caller_stress_relative_bound']*protocol['stress_scale_Pa'],f"factor{group['factor']}/call{len(points)+1}: stress accuracy")
            gate(error['e']<=protocol['policy']['caller_void_absolute_bound'],f"factor{group['factor']}/call{len(points)+1}: void accuracy")
            for k in maximum:maximum[k]=max(maximum[k],error[k])
            points.append({'segment':point['segment'],'physical_endpoint':point['physical_endpoint'],
                           'errors':error,'signed_pressure_error_Pa':delta[0],
                           'signed_void_error':delta[6],'reference_uncertainty':point['reference_uncertainty'],
                           'state':state,'actual_parent':wanted['initial'],
                           'fractions':d['increment_fractions']})
            parent=state.copy()
        groups.append({'factor':group['factor'],'points':points})
    comparisons=[]
    for low,high in zip(groups,groups[1:]):
        a=[p for p in low['points'] if p['physical_endpoint']]
        b=[p for p in high['points'] if p['physical_endpoint']]
        require(len(a)==len(b)==3,'physical endpoints')
        for x,y in zip(a,b):
            for channel in maximum:
                floor=protocol['policy']['stress_floor_relative']*protocol['stress_scale_Pa'] if channel=='stress' else protocol['policy']['void_floor_absolute']
                uncertainty=max(x['reference_uncertainty'][channel],y['reference_uncertainty'][channel])
                bound=protocol['policy']['endpoint_successor_error_factor']*x['errors'][channel]+2*(floor+uncertainty)
                passed=y['errors'][channel]<=bound
                label=f"factors{low['factor']}/{high['factor']}/segment{x['segment']}: {channel} contraction"
                gate(passed,label)
                comparisons.append({'label':label,'passed':passed,'predecessor_error':x['errors'][channel],
                                    'successor_error':y['errors'][channel],'bound':bound})
    return {'version':'clay2014-controlled-resolution-assessment-v1','backend':backend,
            'outcome':'passed' if not failures else 'failed','failures':failures,
            'protocol_sha256':sha(ROOT/PROTOCOL),'collection_freeze_sha256':sha(ROOT/FREEZE),
            'transport_sha256':sha(raw_path),'groups':groups,'endpoint_comparisons':comparisons,
            'maximum_caller_error':maximum,'claims':copy.deepcopy(protocol['policy']['claims'])}


def parity(native,wasm):
    require(native['backend']=='native' and wasm['backend']=='wasm','parity backend order')
    require(native['protocol_sha256']==wasm['protocol_sha256']==sha(ROOT/PROTOCOL),'parity protocol')
    require(len(native['groups'])==len(wasm['groups'])==4,'parity groups')
    scale=read(ROOT/PROTOCOL)['stress_scale_Pa'];maximum=0.
    for a,b in zip(native['groups'],wasm['groups']):
        require(a['factor']==b['factor'] and len(a['points'])==len(b['points']),'aligned parity matrix')
        for x,y in zip(a['points'],b['points']):
            for key in ('state','actual_parent'):
                maximum=max(maximum,math.hypot(*(u-v for u,v in zip(x[key][:6],y[key][:6])))/scale,abs(x[key][6]-y[key][6]))
    return {'maximum_state_and_parent_scaled_difference':maximum,
            'passed':maximum<=reference.POLICY['parity_scaled_bound'],
            'both_numerical_assessments_passed':native['outcome']==wasm['outcome']=='passed'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--collect-native',action='store_true');p.add_argument('--receipt',type=Path)
    p.add_argument('--transport',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();require(not a.output.exists(),'fresh output required')
    if a.collect_native:
        require(a.receipt is None and a.transport is None,'collection has no replay inputs')
        collect_native(a.output)
    else:
        require(a.receipt is not None and a.transport is not None,'explicit receipt and raw companion required')
        result=audit(read(a.receipt),a.transport)
        a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(result['outcome'])
