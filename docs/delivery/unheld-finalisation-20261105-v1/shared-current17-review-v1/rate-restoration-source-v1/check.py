from pathlib import Path
import hashlib,json,re
N=Path('docs/delivery/unheld-finalisation-20261105-v1')
P=N/'current17-igs97-regression-diagnosis-v1'
Q=N/'shared-current17-review-v1/rate-restoration-source-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
m=P/'manifest.json'
ck('exact frozen manifest',sha(m.read_bytes())=='900c333afd34eda284c6300d3951ce890d2b8b9f52c96c4c4416eb9cf97253c2')
for path,pin in json.loads(m.read_text())['files'].items():
 f=P/path
 ck('member '+path,f.is_file() and not f.is_symlink() and len(f.read_bytes())==pin['bytes'] and sha(f.read_bytes())==pin['sha256'])
policy=json.loads((P/'GATES.json').read_text())
for k,pin in policy['inputs'].items():
 b=Path(pin['path']).read_bytes();ck('independent input '+k,len(b)==pin['bytes'] and sha(b)==pin['sha256'])
current=(P/'originals/current_solver.hpp').read_text();old=(P/'originals/old_solver.hpp').read_text()
B=P/'original-rate-profile-v1'
b=(B/'proposed/cpp/include/atlas/solver.hpp').read_text();before=(B/'current-block.txt').read_text();after=(B/'replacement-block.txt').read_text()
ck('single exact changed block',current.count(before)==1 and b.count(after)==1)
ck('whole file forward exact',current.replace(before,after)==b)
ck('whole file reverse exact',b.replace(after,before)==current)
ck('candidate correct hash',sha(b.encode())=='0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc')
rate=after.split('if(models()[model].rate){\n',1)[1].split('            }else{',1)[0]
rate='\n'.join(x[4:] for x in rate.splitlines())+'\n'
rate=rate.replace('return false;derivative=','return false;double derivative=')
ck('entire rate arithmetic original byte fragment',rate in old)
nonrate=after.split('            }else{\n',1)[1].rsplit('            }\n',1)[0]
nonrate='\n'.join(x[4:] for x in nonrate.splitlines())+'\n'
nonrate=nonrate.replace('return false;derivative=slope.value;','return false;const double derivative=slope.value;')
ck('entire nonrate body exact640',nonrate==before)
# Collapse each dispatch choice and compare the complete controlled_step function.
def control(s):return s[s.index('inline bool controlled_step('):s.index('// Research range is an explicit caller choice')]
ck('rate full controlledstep exact702',control(b.replace(after,rate))==control(old))
ck('nonrate full controlledstep exact640',control(b.replace(after,before))==control(current))
ck('generic dispatch without model IDs',after.count('models()[model].rate')==1 and not any(x in after.lower() for x in ('igs97','manzari','1997','hypoplastic')))
ck('partition helper and integration untouched',b[:b.index('inline bool controlled_step(')]==current[:current.index('inline bool controlled_step(')])
ck('remaining validation/defaults/history untouched',b[b.index('// Research range is an explicit caller choice'):]==current[current.index('// Research range is an explicit caller choice'):])
# Execute only the author's pure source/algebra checker, redirecting its output.
author=(P/'check_source.py').read_text().replace('P=Path(__file__).resolve().parent',f'P=Path({str(P)!r})').replace("(P/'source-checks.json').write_text", "(Path("+repr(str(Q))+ ")/'author-source-checks.json').write_text")
exec(compile(author,str(P/'check_source.py'),'exec'),{'__file__':str(Q/'check.py')})
(Q/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'compiled_calls':0},indent=2)+'\n')
print(json.dumps({'independent_checks':len(checks),'passed':True}))
