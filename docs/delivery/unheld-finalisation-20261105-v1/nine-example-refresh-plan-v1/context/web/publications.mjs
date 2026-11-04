const $=id=>document.getElementById(id);
const versionNames={'version-of-record':'Journal version',preprint:'Preprint',correction:'Correction'};
const relationNames={'is-preprint-of':['Preprint of','Journal version of'],corrects:['Corrects','Corrected by'],'builds-on':['Builds on','Followed by'],discusses:['Discusses','Discussed by']};
let graph,models=new Map();
function el(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function external(url,text){
  const link=el('a',text),parsed=new URL(url);
  if(!['https:','http:'].includes(parsed.protocol))throw Error('Unsupported publication URL.');
  link.href=parsed.href;link.target='_blank';link.rel='noopener noreferrer';return link;
}
function fragment(id){return 'publication-'+encodeURIComponent(id);}
function permalink(node,text=node.title){const link=el('a',text);link.href='./publications.html#'+fragment(node.id);return link;}
function sources(container,evidence){
  for(const source of evidence){const row=el('p');row.append(external(source.url,source.locator+' ↗'));container.append(row);}
}
function render(){
  const query=$('publication-search').value.trim().toLowerCase(),version=$('publication-version').value,model=$('publication-model').value;
  const nodes=new Map(graph.publications.map(node=>[node.id,node])),grid=$('publication-grid');grid.replaceChildren();
  const selected=graph.publications.filter(node=>(version==='all'||node.version_role===version)&&(model==='all'||node.model_ids.includes(model))&&
    (node.title+' '+node.authors.join(' ')+' '+node.doi+' '+node.publication_date_parts.join('-')).toLowerCase().includes(query));
  for(const node of selected){
    const card=el('article',undefined,'catalogue-card publication-card');card.id=fragment(node.id);card.tabIndex=-1;
    card.append(el('span',versionNames[node.version_role]||node.version_role,'badge'),el('h2',node.title),el('p',node.authors.join('; ')+' · '+node.publication_date_parts.join('-')));
    const doi=el('p');doi.append(external(node.url,'DOI: '+node.doi+' ↗'));card.append(doi);
    card.append(permalink(node,'Link to this publication'));
    card.append(el('p','Independent source review pending.','publication-review'));
    for(const modelId of node.model_ids){
      const row=el('p','Linked formulation: ');row.append(el('strong',models.get(modelId)||modelId));card.append(row);
    }
    const edges=graph.relations.filter(edge=>edge.source===node.id||edge.target===node.id);
    const corrections=edges.filter(edge=>edge.relation==='corrects'&&edge.target===node.id);
    if(corrections.length){
      const notice=el('div',undefined,'publication-correction');notice.append(el('h3','Correction notice'));
      for(const edge of corrections){const p=el('p');p.append(permalink(nodes.get(edge.source)));notice.append(p,el('p',edge.summary));}
      card.append(notice);
    }
    if(edges.length){
      const list=el('ul',undefined,'publication-relations');
      for(const edge of edges){
        const outgoing=edge.source===node.id,other=nodes.get(outgoing?edge.target:edge.source),item=el('li');
        item.append(el('strong',relationNames[edge.relation][outgoing?0:1]+': '),permalink(other),el('p',edge.summary));
        const detail=el('details');detail.append(el('summary','Relation evidence · review pending'));sources(detail,edge.evidence);item.append(detail);list.append(item);
      }
      card.append(el('h3','Related publications'),list);
    }
    const detail=el('details');detail.append(el('summary','Record evidence & open questions'));sources(detail,node.evidence);
    for(const question of node.unresolved)detail.append(el('p',question));card.append(detail);grid.append(card);
  }
  $('publication-count').textContent=`${selected.length} of ${graph.publications.length} publications shown · ${graph.relations.length} sourced relations in the full collection`;
  if(!selected.length)grid.append(el('p','No matching publications. Reset filters to show the collection.'));
}
function readFilters(){
  const params=new URLSearchParams(location.search);
  $('publication-search').value=params.get('q')||'';
  for(const [id,key] of [['publication-version','version'],['publication-model','model']]){
    const value=params.get(key)||'all',select=$(id);
    if(!Array.from(select.options).some(option=>option.value===value))select.add(new Option('Unknown filter: '+value,value));
    select.value=value;
  }
}
function applyFilters(){
  const url=new URL(location.href);
  for(const [id,key] of [['publication-search','q'],['publication-version','version'],['publication-model','model']]){
    const value=$(id).value;if(value&&value!=='all')url.searchParams.set(key,value);else url.searchParams.delete(key);
  }
  history.replaceState(null,'',url);render();
}
function revealAnchor(){
  if(!location.hash)return;
  const id=location.hash.slice(1),node=graph.publications.find(node=>fragment(node.id)===id);
  if(!node)return;
  if(!document.getElementById(id)){
    $('publication-search').value='';$('publication-version').value=$('publication-model').value='all';applyFilters();
  }
  const target=document.getElementById(id);target.focus({preventScroll:true});target.scrollIntoView({block:'start'});
}
try{
  const [response,manifest]=await Promise.all([fetch('./publications.json'),fetch('./catalogue.json')]);
  if(!response.ok||!manifest.ok)throw Error('Publication assets unavailable.');
  graph=await response.json();const catalogue=await manifest.json();
  if(graph.kind!=='publication-lineage'||graph.schema_version!=='0.1'||!Array.isArray(graph.publications)||!Array.isArray(graph.relations))throw Error('Unsupported publication records.');
  models=new Map(catalogue.models.map(model=>[model.id,model.name]));
  const linked=new Set(graph.publications.flatMap(node=>node.model_ids));
  for(const id of [...linked].sort())$('publication-model').add(new Option(models.get(id)||id,id));
  $('publication-scope').textContent=graph.scope+' Independent review pending. Updated '+graph.updated_on+'.';
  readFilters();render();revealAnchor();
  $('publication-filters').onsubmit=event=>{event.preventDefault();applyFilters();};
  $('publication-search').oninput=$('publication-version').onchange=$('publication-model').onchange=applyFilters;
  $('publication-reset').onclick=()=>{$('publication-search').value='';$('publication-version').value=$('publication-model').value='all';history.replaceState(null,'',location.pathname);render();};
  window.addEventListener('hashchange',revealAnchor);
  window.addEventListener('popstate',()=>{readFilters();render();revealAnchor();});
}catch(error){
  $('publication-error').hidden=false;$('publication-count').textContent='Publication browsing unavailable.';
  $('publication-scope').textContent='Source review status could not be loaded.';$('publication-grid').replaceChildren();
  for(const control of $('publication-filters').elements)control.disabled=true;
}
