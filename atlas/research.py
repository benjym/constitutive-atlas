"""Auditable bibliographic discovery. Search output is a screening queue."""
import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import urllib.parse
import urllib.request
from .model import ROOT, all_models
from .structure import check
from .dsl import ValidationError


def validate_publications(graph):
    """Check identity and provenance, without certifying scientific relations."""
    schema = json.loads((ROOT / 'schemas/publications.schema.json').read_text())
    check(graph, schema)
    ids = set()
    model_ids = {m['id'] for m in json.loads((ROOT / 'catalogue/manifest.json').read_text())['models']}
    for node in graph['publications']:
        doi = node['doi']
        if doi != doi.strip().lower() or node['id'] != 'doi:' + doi or node['url'] != 'https://doi.org/' + doi:
            raise ValidationError('publication identity must use a normalized DOI and matching URL')
        if node['id'] in ids:
            raise ValidationError('duplicate publication identity')
        ids.add(node['id'])
        if len(node['model_ids']) != len(set(node['model_ids'])) or not set(node['model_ids']) <= model_ids:
            raise ValidationError('unknown or duplicate formulation binding')
    relations = set()
    for edge in graph['relations']:
        key = (edge['source'], edge['target'], edge['relation'])
        if edge['source'] not in ids or edge['target'] not in ids or edge['source'] == edge['target']:
            raise ValidationError('relation endpoints must be distinct known publications')
        if key in relations:
            raise ValidationError('duplicate publication relation')
        relations.add(key)
    for record in graph['publications'] + graph['relations']:
        for evidence in record['evidence']:
            if ('path' in evidence) != ('sha256' in evidence):
                raise ValidationError('local evidence needs both a path and checksum')
            if 'path' in evidence:
                path = (ROOT / evidence['path']).resolve()
                if not path.is_relative_to(ROOT.resolve()):
                    raise ValidationError('evidence path escapes repository')
                if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']:
                    raise ValidationError('publication evidence checksum mismatch')
    return graph


def load_publications():
    return validate_publications(json.loads((ROOT / 'catalogue/publications.json').read_text()))


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
    publications = load_publications()
    dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
    connection=sqlite3.connect(dest)
    try:
        connection.execute('PRAGMA foreign_keys=ON')
        with connection:
            connection.executescript('''CREATE TABLE IF NOT EXISTS models(id TEXT PRIMARY KEY,name TEXT NOT NULL,family TEXT NOT NULL,status TEXT NOT NULL,executable INTEGER NOT NULL,definition_json TEXT);
            CREATE TABLE IF NOT EXISTS sources(model_id TEXT NOT NULL,url TEXT NOT NULL,locator TEXT NOT NULL,role TEXT NOT NULL,FOREIGN KEY(model_id) REFERENCES models(id));
            CREATE TABLE IF NOT EXISTS publications(id TEXT PRIMARY KEY,doi TEXT NOT NULL UNIQUE,title TEXT NOT NULL,url TEXT NOT NULL,record_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS publication_relations(source TEXT NOT NULL REFERENCES publications(id),target TEXT NOT NULL REFERENCES publications(id),relation TEXT NOT NULL,record_json TEXT NOT NULL,PRIMARY KEY(source,target,relation));
            CREATE TABLE IF NOT EXISTS publication_models(publication_id TEXT NOT NULL REFERENCES publications(id),model_id TEXT NOT NULL REFERENCES models(id),PRIMARY KEY(publication_id,model_id));''')
            connection.execute('DELETE FROM publication_models')
            connection.execute('DELETE FROM publication_relations')
            connection.execute('DELETE FROM publications')
            connection.execute('DELETE FROM sources');connection.execute('DELETE FROM models')
            for entry in manifest['models']:
                m=models.get(entry['id']);connection.execute('INSERT INTO models VALUES(?,?,?,?,?,?)',(entry['id'],entry['name'],entry['family'],m['status'] if m else 'candidate',int(bool(m)),json.dumps(m) if m else None))
                sources = list((m or {}).get('sources', []))
                if entry.get('discovery_url'):
                    sources.append(dict(url=entry['discovery_url'], locator='Bibliographic review pending', role='Discovery reference'))
                sources += entry.get('research_sources', []) + entry.get('catalogue_sources', [])
                for s in sources:
                    connection.execute('INSERT INTO sources VALUES(?,?,?,?)', (entry['id'], s['url'], s['locator'], s['role']))
            for node in publications['publications']:
                connection.execute('INSERT INTO publications VALUES(?,?,?,?,?)',
                    (node['id'], node['doi'], node['title'], node['url'], json.dumps(node)))
                for model_id in node['model_ids']:
                    connection.execute('INSERT INTO publication_models VALUES(?,?)', (node['id'], model_id))
            for edge in publications['relations']:
                connection.execute('INSERT INTO publication_relations VALUES(?,?,?,?)',
                    (edge['source'], edge['target'], edge['relation'], json.dumps(edge)))
    finally:connection.close()
    return dest
