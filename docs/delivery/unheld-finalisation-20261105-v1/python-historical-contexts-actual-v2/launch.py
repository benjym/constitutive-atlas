import importlib.util,json,hashlib
from pathlib import Path
p=Path(__file__).with_name('plan.json');q=json.loads(p.read_text());o=Path(q['observer']);assert hashlib.sha256(o.read_bytes()).hexdigest()==q['observer_sha256']
s=importlib.util.spec_from_file_location('observer',o);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=m.observe(q['argv'],q['cwd'],p.parent/'observer',env=q['env'],timeout=q['timeout']);raise SystemExit(r.returncode)
