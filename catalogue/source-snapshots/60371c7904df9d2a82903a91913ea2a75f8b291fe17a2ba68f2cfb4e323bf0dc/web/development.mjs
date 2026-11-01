const scenarios=['file_initial','original_table_disputed_e0'];
const packages=['pressure3','density3'];
const finite=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
export function validateSummary(data){
  if(data?.kind!=='kfs-development-summary'||data.schema_version!=='0.1'||data.status!=='provisional'||data.scientific_admission!==false)throw Error('Unsupported development evidence');
  if(!Array.isArray(data.scenarios)||data.scenarios.length!==2||!scenarios.every(id=>data.scenarios.filter(s=>s.id===id&&typeof s.label==='string'&&typeof s.description==='string').length===1))throw Error('Incomplete initialization scenarios');
  if(!Array.isArray(data.scores)||data.scores.length!==4||!scenarios.every(s=>packages.every(p=>data.scores.filter(r=>r.scenario===s&&r.package===p&&finite(r.root_scaled_mse)).length===1)))throw Error('Incomplete or invalid package scores');
  const r=data.refinement;
  if(!r||typeof r.passed!=='boolean'||!finite(r.maximum_fraction)||!finite(r.limit_fraction)||r.limit_fraction<=0||JSON.stringify(r.levels)!=='[0.0002,0.0001,0.00005]'||!Array.isArray(r.shifts)||r.shifts.length!==12)throw Error('Incomplete refinement evidence');
  for(const p of packages)for(const test of ['KFS-TMD12','KFS-TMD14'])for(const step of r.levels){
    if(r.shifts.filter(x=>x.package===p&&x.test===test&&x.maximum_increment===step&&finite(x.q)&&finite(x.volume)).length!==1)throw Error('Invalid refinement coverage');
  }
  if(!Array.isArray(data.limitations)||!data.limitations.length||!data.limitations.every(x=>typeof x==='string'))throw Error('Missing limitations');
  if(!Array.isArray(data.sources)||!data.sources.length||!data.sources.every(s=>{try{return typeof s.title==='string'&&new URL(s.url).protocol==='https:';}catch{return false;}}))throw Error('Unsafe or missing evidence links');
  if(!/^[a-f0-9]{64}$/.test(data.definition_sha256))throw Error('Missing archived model identity');
  return data;
}
export function scenarioView(data,id){
  validateSummary(data);
  if(!scenarios.includes(id))throw Error('Unknown initialization scenario');
  const rows=packages.map(p=>{
    const score=data.scores.find(r=>r.package===p&&r.scenario===id).root_scaled_mse;
    const baseline=data.scores.find(r=>r.package===p&&r.scenario==='file_initial').root_scaled_mse;
    return {package:p,score,relativeChange:baseline?score/baseline-1:null};
  });
  return {description:data.scenarios.find(s=>s.id===id).description,rows,contrast:rows[1].score-rows[0].score};
}
export async function mount(doc,fetcher=fetch){
  const status=doc.getElementById('development-status');
  try{
    const response=await fetcher('./development.json');if(!response.ok)throw Error('Evidence download failed');
    const data=validateSummary(await response.json()),select=doc.getElementById('scenario');
    const element=(tag,text)=>{const node=doc.createElement(tag);node.textContent=text;return node;};
    select.replaceChildren(...data.scenarios.map(s=>{const option=element('option',s.label);option.value=s.id;return option;}));
    function update(){
      const view=scenarioView(data,select.value);
      doc.getElementById('scenario-description').textContent=view.description;
      doc.getElementById('scores').replaceChildren(...view.rows.map(row=>{
        const tr=doc.createElement('tr'),label=element('th',row.package);label.scope='row';
        tr.append(label,element('td',row.score.toFixed(6)),element('td',row.relativeChange===null?'Undefined':(100*row.relativeChange).toFixed(3)+'%'));return tr;
      }));
      doc.getElementById('contrast').textContent='Density3 minus pressure3: '+view.contrast.toFixed(6)+'. Negative values favor density3 for this conditional development objective.';
    }
    select.addEventListener('change',update);select.disabled=false;update();
    doc.getElementById('refinement-summary').textContent=(data.refinement.passed?'The frozen refinement gate passes. ':'The frozen refinement gate fails. ')+
      'Largest adjacent change: '+(100*data.refinement.maximum_fraction).toFixed(3)+'% of the matching initialization shift; declared limit '+(100*data.refinement.limit_fraction).toFixed(1)+'%.';
    doc.getElementById('refinement-rows').replaceChildren(...data.refinement.shifts.map(r=>{
      const tr=doc.createElement('tr');for(const value of [r.package+' / '+r.test,r.maximum_increment.toFixed(5),r.q.toFixed(6),r.volume.toFixed(6)])tr.append(element('td',value));return tr;
    }));
    doc.getElementById('limitations').replaceChildren(...data.limitations.map(x=>element('li',x)));
    doc.getElementById('sources').replaceChildren(...data.sources.map(s=>{const li=doc.createElement('li'),link=element('a',s.title);link.href=s.url;li.append(link);return li;}));
    doc.getElementById('model-identity').textContent='Archived definition SHA-256: '+data.definition_sha256;
    status.textContent='Provisional development evidence loaded. Independent scientific review is pending.';
  }catch(error){status.textContent='Development evidence unavailable: '+error.message;status.setAttribute('role','alert');}
}
if(typeof document!=='undefined')mount(document);
