"""Saved metadata/access checks only; no network, PDF parsing, author code or binaries."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');P=ROOT/'docs/ingestion/terracotta-2024/journal-acquisition-v2'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if (Path(__file__).parent/'inputs.json').exists():
 for p,h in load(Path(__file__).parent/'inputs.json').items():assert sha(ROOT/p)==h,p
r=load(P/'receipt.json');assert len(r['files'])==9
for name,h in r['files'].items():assert sha(P/name)==h,name
xml=(P/'publisher-api.xml').read_bytes();assert len(xml)==2001
root=ET.fromstring(xml);local=lambda tag:tag.split('}')[-1]
assert local(root.tag)=='full-text-retrieval-response' and [local(e.tag) for e in root]==['coredata']
fields={local(e.tag):(e.text or '').strip() for e in root[0] if local(e.tag)!='link'}
doi='10.1016/j.jmps.2024.105789';licence='http://creativecommons.org/licenses/by/4.0/'
assert fields['doi']==doi and fields['identifier']=='doi:'+doi
assert fields['title']=='A simple hydrodynamic model for clay'
assert fields['publicationName']=='Journal of the Mechanics and Physics of Solids'
for k,v in {'openaccess':'1','openaccessArticle':'true','openaccessType':'Full','openaccessUserLicense':licence}.items():assert fields[k]==v
assert not any(local(e.tag).lower() in ['body','originaltext','math','equation','article'] for e in root.iter())
access=load(P/'publisher-access.json');assert access['status']==200 and access['bytes']==len(xml) and access['content_type'].startswith('text/xml')
c=load(P/'crossref.json')['message'];assert c['DOI']==doi and c['title']==[fields['title']]
assert [(a['given'],a['family']) for a in c['author']]==[('Max','Wiebicke'),('Itai','Einav')]
assert c['volume']=='192' and c['article-number']=='105789'
vor=[x for x in c['license'] if x['content-version']=='vor'];tdm=[x for x in c['license'] if x['content-version']=='tdm']
assert len(vor)==1 and vor[0]['URL']==licence and vor[0]['start']['date-parts']==[[2024,7,18]]
assert len(tdm)==2 and {x['URL'] for x in tdm}=={'https://www.elsevier.com/tdm/userlicense/1.0/','https://www.elsevier.com/legal/tdmrep-license'}
assert all(x['start']['date-parts']==[[2024,11,1]] for x in tdm)
assert len(c['link'])==2 and all(x['content-version']=='vor' and x['intended-application']=='text-mining' for x in c['link'])
o=load(P/'openalex.json');assert o['doi']=='https://doi.org/'+doi and o['title']==fields['title']
locations=o['locations'];assert len(locations)==2 and {x['doi'] for x in locations}=={'https://doi.org/'+doi,'https://doi.org/10.2139/ssrn.4699137'}
assert all(x['pdf_url'] is None for x in locations)
published=next(x for x in locations if x['doi'].endswith(doi));ssrn=next(x for x in locations if 'ssrn' in x['doi'])
assert published['version']=='publishedVersion' and published['license']=='cc-by'
assert ssrn['version']=='acceptedVersion' and ssrn['license'] is None
assert o['open_access']['any_repository_has_fulltext'] is True
assert o['primary_location']['pdf_url'] is None and o['best_oa_location']['pdf_url'] is None
repo=load(P/'author-tree.json');assert repo['sha']==r['author_commit']=='a4039d0124d8ff61e766f5201f44ddc163c4cff5' and repo['truncated'] is False
assert len(repo['tree'])==9 and not any(Path(x['path']).suffix.lower() in {'.pdf','.tex'} for x in repo['tree'])
full=load(P/'full-access.json');assert len(full)==2
assert 'view=FULL' in full[0]['url'] and full[0]['error']=='HTTP Error 401: Unauthorized'
assert '/pdfft?' in full[1]['url'] and full[1]['error']=='HTTP Error 403: Forbidden'
pdf=load(P/'pdf-access.json');assert 'application/pdf' in pdf['url'] and pdf['error']=='HTTP Error 406: Not Acceptable'
failed=load(P/'metadata-access.json');assert len(failed)==3 and all('error' in x and 'status' not in x for x in failed)
network=load(P/'metadata-access-network.json');assert [x['name'] for x in network]==['openalex','crossref','author-tree']
for item,name in zip(network,['openalex.json','crossref.json','author-tree.json']):assert item['status']==200 and item['bytes']==(P/name).stat().st_size
assert r['results']=={'public_metadata':True,'publisher_default_xml_status':200,'publisher_default_xml_bytes':2001,'full_view_status':401,'pdf_endpoint_status':403,'api_pdf_status':406,'author_tree_pdf_or_tex_count':0,'downloads_filename_inventory_pdf_count':20}
print('PASS: nine exact raw hashes;2001-byte metadata-only XML; exact journal identity/openaccess/CC BY4 fields.')
print('PASS: Crossref vor2024-07-18 CC BY4 distinguished from two tdm2024-11-01 licenses; text-mining links do not prove acquired body.')
print('PASS: OpenAlex journal+SSRN/nullPDF; SSRN acceptedVersion/license null; pinned complete9-entry tree has no PDF/TeX.')
print('PASS: saved initial DNS failures, later200 metadata and401FULL/403pdfft/406API-PDF access records retained; no source pages acquired.')
print('LIMITS:20 Downloads is a nonrecursive filename-only count; no fresh text/archive scan, E1/equation/domain/parameter/third-party-data-rights or scientific approval.')
