"""Explicitly loaded dedicated native ABI. Importing this module executes no binary."""
import ctypes as C,json,hashlib
from dataclasses import asdict
from copy import deepcopy
from pathlib import Path
from .controlled_time import (PROFILE,Context,Result,Settings,identity,control_fields,components,unpack,initialize,context_from_dict,stage_controls,finite)
class NativeEngine:
    def __init__(self,module,catalogue,model):
        self.trace=[]
        self.artifact_identity={'module_sha256':hashlib.sha256(Path(module).read_bytes()).hexdigest(),'catalogue_file_sha256':hashlib.sha256(Path(catalogue).read_bytes()).hexdigest()}
        self.model=model;self.catalogue=json.loads(Path(catalogue).read_text())
        if self.catalogue.get('profile')!=PROFILE:raise ValueError('controlled-time catalogue required')
        matches=[(i,m) for i,m in enumerate(self.catalogue['models']) if m['id']==model['id']]
        if len(matches)!=1 or matches[0][1]['model_sha256']!=identity(model):raise ValueError('native model/catalogue identity mismatch')
        self.index,self.descriptor=matches[0]
        payload={k:v for k,v in self.catalogue.items() if k!='catalogue_sha256'}
        expected=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        if self.catalogue.get('catalogue_sha256')!=expected:raise ValueError('catalogue semantic hash mismatch')
        self.lib=C.CDLL(str(Path(module).resolve()))
        self.lib.controlled_time_model_hash.argtypes=[C.c_int];self.lib.controlled_time_model_hash.restype=C.c_char_p
        self.lib.controlled_time_catalogue_hash.argtypes=[];self.lib.controlled_time_catalogue_hash.restype=C.c_char_p
        self.lib.controlled_time_catalogue_file_hash.argtypes=[];self.lib.controlled_time_catalogue_file_hash.restype=C.c_char_p
        if self.lib.controlled_time_catalogue_file_hash()!=hashlib.sha256(Path(catalogue).read_bytes()).hexdigest().encode():raise ValueError('compiled catalogue file identity mismatch')
        if self.lib.controlled_time_model_hash(self.index)!=identity(model).encode() or self.lib.controlled_time_catalogue_hash()!=expected.encode():raise ValueError('compiled model/catalogue identity mismatch')
        D=C.POINTER(C.c_double);I=C.c_int;F=C.c_double
        self.lib.controlled_time_size.argtypes=[I,I];self.lib.controlled_time_size.restype=I
        self.lib.controlled_time_evaluate.argtypes=[I,D,I,D,I,F,D,I,D,I,I,D,I,D,I,D,I];self.lib.controlled_time_evaluate.restype=I
        self.lib.controlled_time_advance.argtypes=[I,D,I,D,I,F,F,D,I,D,I,D,I,D,I,D,I,D,I,D,I,D,I,D,I,D,I,D,I];self.lib.controlled_time_advance.restype=I
        self.fields=control_fields(model);self.shapes=[sum(6 if f['shape']=='sym' else 1 for f in model['state']),len(model['parameters']),sum(6 if f['shape']=='sym' else 1 for f in self.fields),sum(6 if f['shape']=='sym' else 1 for f in model.get('observables',[])),6,4]
        if [self.lib.controlled_time_size(self.index,i) for i in range(6)]!=self.shapes:raise ValueError('native ABI catalogue shape mismatch')
    @staticmethod
    def array(v):return (C.c_double*len(v))(*v)
    def evaluate(self,context,initial=False):
        context_from_dict(self.model,asdict(context));ns,np,nc,no,_,_=self.shapes
        state=self.array(components(context.state,self.model['state']));p=self.array([context.parameters[n] for n in self.model['parameters']]);v=self.array(components(context.controls,self.fields));cr=self.array(components(context.control_rates,self.fields))
        rr=self.array([-1234567.]*ns);oo=self.array([-1234567.]*no);ss=self.array([-1234567.]*ns)
        status=self.lib.controlled_time_evaluate(self.index,state,ns,p,np,context.time,v,nc,cr,nc,int(initial),rr,ns,oo,no,ss,ns)
        self.trace.append(dict(kind='evaluate',inputs=asdict(context),initial=initial,status=status,raw_rates=list(rr),raw_observables=list(oo),raw_scales=list(ss),artifact_identity=self.artifact_identity))
        if status!=1:raise ValueError('native controlled-time evaluation rejected')
        return unpack(list(rr),self.model['state']),unpack(list(oo),self.model.get('observables',[])),list(ss)
    def advance(self,model,parent,duration,controls_start,controls_end,settings=Settings()):
        if identity(model)!=identity(self.model):raise ValueError('wrong native model')
        context_from_dict(model,asdict(parent));settings.check()
        if controls_start!=parent.controls:raise ValueError('start controls differ from committed values')
        if not finite(duration) or duration<=0 or not finite(parent.time+duration) or not parent.time+duration>parent.time:raise ValueError('positive representable physical duration required')
        endvalues,endrates=stage_controls(model,controls_start,controls_end,duration,1)
        _,left,_=self.evaluate(parent);rightctx=Context(deepcopy(parent.state),parent.time,deepcopy(parent.controls),endrates,deepcopy(parent.parameters),parent.model_sha256)
        _,right,_=self.evaluate(rightctx)
        ns,np,nc,no,_,_=self.shapes
        arrays=[self.array(components(parent.state,model['state'])),self.array([parent.parameters[n] for n in model['parameters']]),self.array(components(parent.controls,self.fields)),self.array(components(parent.control_rates,self.fields)),self.array(components(controls_start,self.fields)),self.array(components(controls_end,self.fields)),self.array(list(asdict(settings).values()))]
        z,p,v,cr,start,end,ss=arrays;outputs=[self.array([-1234567.]*n) for n in [ns,1,nc,nc,no,4]];out,clock,outv,outr,oo,diag=outputs
        before=[list(a) for a in arrays]
        status=self.lib.controlled_time_advance(self.index,z,ns,p,np,parent.time,duration,v,nc,cr,nc,start,nc,end,nc,ss,6,out,ns,clock,1,outv,nc,outr,nc,oo,no,diag,4)
        self.trace.append(dict(kind='advance',inputs=asdict(parent),duration=duration,controls_start=deepcopy(controls_start),controls_end=deepcopy(controls_end),settings=asdict(settings),status=status,raw_state=list(out),raw_time=list(clock),raw_controls=list(outv),raw_rates=list(outr),raw_observables=list(oo),raw_diagnostics=list(diag),input_arrays_before=before,input_arrays_after=[list(a) for a in arrays],artifact_identity=self.artifact_identity))
        if [list(a) for a in arrays]!=before:raise ValueError('native ABI changed input')
        if status!=1:
            if any(any(x!=-1234567. for x in a) for a in outputs):raise ValueError('failed native call changed output')
            raise ValueError('native controlled-time advance rejected; context preserved')
        if clock[0]!=parent.time+duration or list(outv)!=components(endvalues,self.fields) or list(outr)!=components(endrates,self.fields):raise ValueError('native clock/control context mismatch')
        ctx=Context(unpack(list(out),model['state']),clock[0],unpack(list(outv),self.fields),unpack(list(outr),self.fields),deepcopy(parent.parameters),parent.model_sha256)
        context_from_dict(model,asdict(ctx))
        return Result(ctx,unpack(list(oo),model.get('observables',[])),left,right,dict(zip(['trials','accepted_half_steps','rejected_trials','final_error'],list(diag))))
