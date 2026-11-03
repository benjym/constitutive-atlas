"""Read-only lawful source acquisition; response originals remain private."""
from pathlib import Path
import urllib.request,urllib.error,json,hashlib,concurrent.futures,datetime
ROOT=Path(__file__).resolve().parents[4];PRIVATE=ROOT/'.local/private-sources/s-clay1/delivery-v2';PRIVATE.mkdir(parents=True,exist_ok=True)
URLS={
'publisher-pdf':'https://cdnsciencepub.com/doi/pdf/10.1139/t02-119',
'publisher-full':'https://cdnsciencepub.com/doi/full/10.1139/t02-119',
'publisher-epdf':'https://cdnsciencepub.com/doi/epdf/10.1139/t02-119',
'legacy-pdf':'https://www.nrcresearchpress.com/doi/pdf/10.1139/t02-119',
'openalex':'https://api.openalex.org/works/https://doi.org/10.1139/t02-119',
'semantic-scholar':'https://api.semanticscholar.org/graph/v1/paper/DOI:10.1139/t02-119?fields=title,openAccessPdf,url',
'chalmers':'https://research.chalmers.se/en/publication/173097',
'strathclyde':'https://strathprints.strath.ac.uk/3809/',
'author-slides':'https://www.mycrisp.com/cugm2003/m-karstunen.pdf'}
def get(pair):
 name,url=pair;r={'name':name,'url':url,'accessed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ConstitutiveAtlas source research'}),timeout=25) as f:b=f.read();r.update(status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
 except urllib.error.HTTPError as e:b=e.read();r.update(status=e.code,error=str(e))
 except Exception as e:r['error']=str(e);return r
 suffix='.pdf' if b.startswith(b'%PDF') else '.response';p=PRIVATE/(name+suffix);p.write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),private_path=str(p.relative_to(ROOT)),is_pdf=b.startswith(b'%PDF'));return r
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:rows=list(ex.map(get,URLS.items()))
 (Path(__file__).parent/'acquisition-v2.json').write_text(json.dumps({'original_doi':'10.1139/t02-119','responses':rows},indent=2)+'\n')
 print(json.dumps([{k:v for k,v in r.items() if k in ['name','status','error','is_pdf']} for r in rows],indent=2))
