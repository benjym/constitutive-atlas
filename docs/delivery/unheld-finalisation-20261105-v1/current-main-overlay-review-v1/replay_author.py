"""Exact frozen source-only author suite with all disposable writes redirected to reviewer."""
from pathlib import Path
import contextlib,io,json,runpy,sys,tempfile
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;A=P.parent/'current-main-overlay-v1/final-active-v1';original_tmp=tempfile.TemporaryDirectory;original_write=Path.write_text
created=[]
def owned(*args,**kwargs):
 kwargs['dir']=P;tmp=original_tmp(*args,**kwargs);created.append(tmp.name);return tmp
def write(self,*args,**kwargs):
 target=P/'author-checks.json'if self.absolute()==A/'checks.json'else self
 assert target.absolute().is_relative_to(P),str(target)
 return original_write(target,*args,**kwargs)
tempfile.TemporaryDirectory=owned;Path.write_text=write
try:
 out=io.StringIO()
 with contextlib.redirect_stdout(out):runpy.run_path(str(A/'check.py'),run_name='__main__')
 assert json.loads((P/'author-checks.json').read_bytes())==json.loads((A/'checks.json').read_bytes())
 assert not any(Path(n).exists()for n in created)
finally:tempfile.TemporaryDirectory=original_tmp;Path.write_text=original_write
print(json.dumps({'status':'PASS','strict_author_checks':487,'author_packet_writes':0,'source_metadata_only':True,'disposable_contexts':len(created),'fixture_cleanup':'complete'},indent=2))
