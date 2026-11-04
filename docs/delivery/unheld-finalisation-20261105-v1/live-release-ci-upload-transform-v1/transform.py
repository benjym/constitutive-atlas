"""Pure source-qualified namespace/report transform. Never observes a real artifact on import."""
from pathlib import Path,PurePosixPath
from collections import Counter
import hashlib,json,re,tarfile,zipfile,ast
HERE=Path(__file__).resolve().parent
REPORT=re.compile(r'implicit-path-package-checks/build-[A-Za-z0-9_-]+/report\.json\Z')
SEMANTIC_REPORT='implicit-path-package-checks/@generated-check-report/report.json'
def hidden(name):return any(part.startswith('.')for part in PurePosixPath(name).parts)
def qualified_names(expected,actual):
 expected=list(expected);actual=list(actual)
 assert len(expected)==len(set(expected))and len(actual)==len(set(actual)),'Duplicate namespace'
 assert not any(hidden(n)for n in actual),'Uploader unexpectedly retained hidden paths'
 kept=[n for n in expected if not hidden(n)]
 old=[n for n in kept if REPORT.fullmatch(n)];new=[n for n in actual if REPORT.fullmatch(n)]
 assert len(old)==len(new)==1,'Exactly one generated package-check report required'
 normalize=lambda names:{SEMANTIC_REPORT if REPORT.fullmatch(n)else n for n in names}
 assert normalize(kept)==normalize(actual),'Meaningful uploaded namespace differs'
 return {'hidden_exclusions':[n for n in expected if hidden(n)],'expected_generated_report':old[0],'actual_generated_report':new[0],'expected_members':len(expected),'uploaded_members':len(actual),'normalized_members':len(kept)}
def validate_report(raw):
 expected=json.loads((HERE/'reference/original-implicit-path-report.json').read_text());actual=json.loads(raw)
 assert set(actual)==set(expected)=={'status','checks','scope'}and actual['status']==expected['status']=='passed'and actual['scope']==expected['scope']
 for report in [expected,actual]:
  assert isinstance(report['checks'],list)and all(set(row)=={'name','passed'}and isinstance(row['name'],str)and row['passed']is True for row in report['checks'])
 assert Counter(row['name']for row in actual['checks'])==Counter(row['name']for row in expected['checks']),'Complete original check coverage changed'
 policy=json.loads((HERE/'POLICY.json').read_text());pin=next(x for x in policy['inputs']if x['path'].endswith('/tools/test_implicit_path_package.py'))
 source=Path(pin['path']).read_bytes();assert hashlib.sha256(source).hexdigest()==pin['sha256']
 required={call.args[0].value for call in ast.walk(ast.parse(source))if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='require'and call.args and isinstance(call.args[0],ast.Constant)}
 assert required<={row['name']for row in actual['checks']}
 return {'status':'passed-original-report-gates','checks':len(actual['checks']),'source_literal_gate_names':sorted(required),'report_sha256':hashlib.sha256(raw).hexdigest(),'original_report_sha256':hashlib.sha256((HERE/'reference/original-implicit-path-report.json').read_bytes()).hexdigest()}
def verify_archive(archive,expected_names,capture_names):
 observed={};captured={}
 with zipfile.ZipFile(archive)as z:
  files=[i for i in z.infolist()if not i.is_dir()]
  assert len(files)==1 and files[0].filename=='artifact.tar','Expected sole artifact.tar'
  with z.open(files[0])as raw,tarfile.open(fileobj=raw,mode='r|*')as tar:
   for member in tar:
    rawname=member.name
    while rawname.startswith('./'):rawname=rawname[2:]
    if member.isdir():continue
    p=PurePosixPath(rawname)
    assert member.isfile()and not p.is_absolute()and '..'not in p.parts and str(p)==rawname and rawname not in observed,'Unsafe/duplicate tar member: '+member.name
    stream=tar.extractfile(member);assert stream is not None
    if rawname in capture_names or REPORT.fullmatch(rawname):
     assert member.size<=16*1024*1024,'Semantic JSON too large'
     data=stream.read();h=hashlib.sha256(data).hexdigest();size=len(data);captured[rawname]=data
    else:
     h=hashlib.sha256();size=0
     while chunk:=stream.read(1024*1024):h.update(chunk);size+=len(chunk)
     h=h.hexdigest()
    assert size==member.size
    observed[rawname]={'sha256':h,'bytes':size,'mode':oct(member.mode)}
 proof=qualified_names(expected_names,observed)
 assert set(capture_names)<=set(captured),'Required semantic JSON absent'
 proof['report']=validate_report(captured[proof['actual_generated_report']])
 verify_archive.last_proof=proof
 return observed,captured
