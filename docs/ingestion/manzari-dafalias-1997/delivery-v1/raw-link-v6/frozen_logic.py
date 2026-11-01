"""Load only frozen Python orchestration; no original Backend is constructed here."""
from pathlib import Path
import ast,hashlib,importlib.util,json,math,textwrap
D=Path(__file__).resolve().parent;P=D.parent

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def frozen():
 for name,digest in json.loads((D/'inputs.json').read_text()).items():assert sha(P/name)==digest,'frozen input drift: '+name

def load(relative):
 spec=importlib.util.spec_from_file_location('frozen_'+relative.replace('/','_').replace('.','_'),P/relative)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def ordinary_case(case,response,relative='ordinary-regression-v7/run.py'):
 # Exact contiguous original decision code, from points extraction to append.
 source=(P/relative).read_text();start=source.index('            points = response.get(');end=source.index("            (out/'report.json').write_text",start)
 body=textwrap.dedent(source[start:end]);last="report['cases'].append("
 line=next(line for line in body.splitlines()if line.startswith(last));assert line.endswith(')')
 body=body.replace(line,'return '+line[len(last):-1]);namespace={'math':math}
 exec('def evaluate(c,response):\n'+textwrap.indent(body,'    '),namespace)
 return namespace['evaluate'](case,response)

def ordinary_hook_source():
 source=(P/'ordinary-regression-v7/run.py').read_text();needle='    backend = module.Backend(args, out)'
 assert source.count(needle)==1
 return source.replace(needle,'    module.Backend = audited_factory(module.Backend)\n'+needle)
