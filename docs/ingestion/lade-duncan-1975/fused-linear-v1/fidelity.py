"""Strict parsed numerical identity, including JSON integer-form signed zero."""
import json,math
class IntegerToken(str):pass
def floating(token):
 value=float(token)
 if not math.isfinite(value):raise ValueError('nonfinite floating token')
 return value
def constant(token):raise ValueError('nonfinite constant '+token)
def parse_response(data):return json.loads(data,parse_int=IntegerToken,parse_float=floating,parse_constant=constant)
def normalized(x):
 if isinstance(x,dict):return {k:normalized(v) for k,v in x.items()}
 if isinstance(x,list):return [normalized(v) for v in x]
 if isinstance(x,IntegerToken):return ('integer',str(x))
 if isinstance(x,float):return ('binary64',x.hex())
 if isinstance(x,bool):return ('bool',x)
 return x
def same_response(a,b):
 if not isinstance(a,dict) or not isinstance(b,dict):return False
 return normalized({k:v for k,v in a.items() if k!='elapsed_ms'})==normalized({k:v for k,v in b.items() if k!='elapsed_ms'})
