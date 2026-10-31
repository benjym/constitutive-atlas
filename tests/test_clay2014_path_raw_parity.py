"""Independent complete-295-row two-companion check; no compiled execution."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from tools import clay2014_path_study as s

AUTHOR_TEST=Path(s.ROOT)/'tests'/'test_clay2014_path_study.py'
if not AUTHOR_TEST.exists():
 # Preinstallation overlay only; installed runs always use the repository test.
 AUTHOR_TEST=Path(s.__file__).resolve().parents[1]/'tests'/'test_clay2014_path_study.py'
spec=importlib.util.spec_from_file_location('clay_author_fixture',AUTHOR_TEST)
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)

class IndependentRawParity(unittest.TestCase):
 def test_both_companions_audited_even_after_digest_rebinding(self):
  ref,cases,points=s.checked_reference();model=s.load(s.MODEL_PATH)
  native=fixtures.synthetic(ref,cases,points,model)
  wasm=copy.deepcopy(native);wasm.update(backend='wasm',wasm_loader_sha256='1'*64,wasm_binary_sha256='2'*64);wasm.pop('native_sha256')
  def rows(report):
   calls=[{'request':{'mode':'describe'},'response':report['runtime_descriptor']}]+[c for g in report['records']for c in g['calls']]+[c for p in report['failure_probes']for c in(p,p['recovery'])]
   out=[]
   for i,c in enumerate(calls):
    if report['backend']=='native':out.append(dict(backend='native',mode='persistent_stream',request_line=s.stream_line(c['request']),request=c['request'],stdout=json.dumps(c['response'])))
    else:out.append(dict(backend='wasm',name='atlas_describe'if i==0 else'atlas_integrate_with_settings',types=[]if i==0 else['string']*5,args=[]if i==0 else[c['request']['model']]+[s.csv(c['request'][k])for k in('parameters','initial','strain','settings')],request=c['request'],raw=json.dumps(c['response'])))
   return out
  with tempfile.TemporaryDirectory()as d:
   d=Path(d);np=d/'native.json';nr=d/'native.transport.jsonl';wr=d/'wasm.transport.jsonl';nrows=rows(native);wrows=rows(wasm)
   def save():
    nr.write_text(''.join(json.dumps(v)+'\n'for v in nrows));wr.write_text(''.join(json.dumps(v)+'\n'for v in wrows))
    native['transport_sha256']=s.sha(nr);wasm['transport_sha256']=s.sha(wr);np.write_text(json.dumps(native));wasm.update(native_report_sha256=s.sha(np),native_transport_sha256=s.sha(nr))
   save();self.assertEqual(s.parity(wasm,native,np,wr,nr),0.)
   # Correct hashes are rebound deliberately. The parser/semantic identity must
   # still reject corruption in either raw companion, not merely hash mismatch.
   for backend,field in [('native','stdout'),('wasm','raw')]:
    target=nrows if backend=='native'else wrows;old=target[17][field];bad=json.loads(old);bad['state'][0]+=1;target[17][field]=json.dumps(bad);save()
    with self.assertRaisesRegex(ValueError,'raw parsed response binding'):s.parity(wasm,native,np,wr,nr)
    target[17][field]=old;save()
   # A valid in-memory native report must not be accepted alongside an unrelated
   # file merely because the Wasm receipt is rebound to that file's hash.
   np.write_text(json.dumps({'unrelated':True}));wasm['native_report_sha256']=s.sha(np)
   with self.assertRaisesRegex(ValueError,'native.*(report|file|receipt|bytes)|parsed native'):
    s.parity(wasm,native,np,wr,nr)

if __name__=='__main__':unittest.main()
