"""Auditable bibliographic discovery. Search output is a screening queue."""
import datetime
import json
from pathlib import Path
import sqlite3
import urllib.parse
import urllib.request
from .model import ROOT, all_models


def discover(query,output,rows=50,cursor='*'):
    if not 1<=rows<=1000:raise ValueError('rows must be between 1 and 1000')
    url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':query,'rows':rows,'cursor':cursor})
    request=urllib.request.Request(url,headers={'User-Agent':'ConstitutiveAtlas/0.1 (bibliographic research)'})
    with urllib.request.urlopen(request,timeout=45) as response:raw=json.load(response)
    record={'schema_version':'0.1','kind':'discovery-batch','query':query,'url':url,
            'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response':raw,'status':'unscreened'}
    dest=Path(output)
    # Discovery batches are evidence; never overwrite an earlier search.
    with dest.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    return record


def export_database(path):
    models={m['id']:m for m in all_models()};manifest=json.loads((ROOT/'catalogue/manifest.json').read_text())
    dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
    connection=sqlite3.connect(dest)
    try:
        with connection:
            connection.executescript('''CREATE TABLE IF NOT EXISTS models(id TEXT PRIMARY KEY,name TEXT NOT NULL,family TEXT NOT NULL,status TEXT NOT NULL,executable INTEGER NOT NULL,definition_json TEXT);
            CREATE TABLE IF NOT EXISTS sources(model_id TEXT NOT NULL,url TEXT NOT NULL,locator TEXT NOT NULL,role TEXT NOT NULL,FOREIGN KEY(model_id) REFERENCES models(id));''')
            connection.execute('DELETE FROM sources');connection.execute('DELETE FROM models')
            for entry in manifest['models']:
                m=models.get(entry['id']);connection.execute('INSERT INTO models VALUES(?,?,?,?,?,?)',(entry['id'],entry['name'],entry['family'],m['status'] if m else 'candidate',int(bool(m)),json.dumps(m) if m else None))
                sources = list((m or {}).get('sources', []))
                if entry.get('discovery_url'):
                    sources.append(dict(url=entry['discovery_url'], locator='Bibliographic review pending', role='Discovery reference'))
                sources += entry.get('research_sources', []) + entry.get('catalogue_sources', [])
                for s in sources:
                    connection.execute('INSERT INTO sources VALUES(?,?,?,?)', (entry['id'], s['url'], s['locator'], s['role']))
    finally:connection.close()
    return dest
