"""Exact approved NorSand identity in the actual uploaded SQLite export."""
import argparse,json,hashlib,sqlite3
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('database',type=Path);p.add_argument('output',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[6];ident='norsand-jefferies-1993-active-axial';definition_path='models/research/norsand/'+ident+'.json';raw=(root/definition_path).read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=='67ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c';model=json.loads(raw);review=json.loads((root/'catalogue/agent-reviews/norsand-1993-agent-v1.json').read_text());approval=next(x for x in json.loads((root/'catalogue/approved-models.json').read_text())['models'] if x['model_id']==ident and x['status']=='approved' and x['definition']['sha256']==h)
 c=sqlite3.connect('file:'+str(a.database.resolve())+'?mode=ro',uri=True)
 try:
  integrity=c.execute('pragma integrity_check').fetchone()[0];fk=c.execute('pragma foreign_key_check').fetchall();assert integrity=='ok' and not fk
  stored=c.execute('select definition_json from models where id=?',(ident,)).fetchone();assert stored and json.loads(stored[0])==model
  approvals=c.execute('select definition_path,definition_sha256,record_json from model_approvals where model_id=?',(ident,)).fetchall();assert any(path==definition_path and digest==h and json.loads(record)==approval for path,digest,record in approvals)
  reviews=c.execute('select sha256,record_json from agent_reviews where model_id=?',(ident,)).fetchall();assert any(digest=='9cfe9b7d58632c5dbc3099fb6debe40a8fdcea47ae66b7077a5e60bf8bebf6b7' and json.loads(record)==review for digest,record in reviews)
  sources=c.execute('select url,locator,role from sources where model_id=?',(ident,)).fetchall();assert any(url=='https://doi.org/10.1680/geot.1993.43.1.91' and 'fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9' in role for url,locator,role in sources)
 finally:c.close()
 out={'result':'PASS','scope':'Exact actual uploaded SQLite definition/approval/review/source and database integrity; live SHA comparison binds this same database','model':ident,'definition_sha256':h,'database_sha256':hashlib.sha256(a.database.read_bytes()).hexdigest(),'integrity':integrity,'foreign_key_errors':len(fk),'exact_definition':True,'exact_approval':True,'exact_agent_review':True,'sources':sources};a.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS exact uploaded database identity and integrity.')
if __name__=='__main__':main()
