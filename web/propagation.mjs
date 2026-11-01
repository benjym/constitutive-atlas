const ids=['file_initial','original_table_disputed_e0'];
const channels=['q','volumetric_strain'];
const finite=x=>typeof x==='number'&&Number.isFinite(x)&&x>=0;
const label=id=>id==='file_initial'?'File':'Original-table alternative';
const channelLabel=id=>id==='q'?'Stress q':'Volume strain';
const replayQuantities={stress_pa:'Stress components [Pa]',q_pa:'Deviator stress q [Pa]',void_ratio:'Void ratio',strain:'Strain components',volumetric_strain:'Volume strain',q_scaled_rms:'Scaled q RMS',volumetric_strain_scaled_rms:'Scaled volume RMS'};
export function validateCurrentReplay(r){
  if(r?.kind!=='current-kfs-replay-summary'||r.status!=='provisional'||r.scientific_admission!==false||r.test!=='KFS-TMD7'||r.observations!==44||r.segments!==43||r.current_processes!==44||r.maximum_axial_strain!==.02||r.maximum_increment!==.0002)throw Error('Unsupported current replay scope');
  if(!Array.isArray(r.rows)||r.rows.length!==7||!Object.keys(replayQuantities).every(k=>r.rows.filter(x=>x.quantity===k&&finite(x.maximum_difference)&&finite(x.limit)&&x.limit>0&&x.passed===(x.maximum_difference<=x.limit)).length===1)||r.passed!==r.rows.every(x=>x.passed))throw Error('Inconsistent current replay gates');
  for(const engine of ['archived','current']){const d=r.diagnostics?.[engine];if(!d||d.caller_increments!==125||!Number.isInteger(d.substeps)||d.substeps<0||!Number.isInteger(d.rejected)||d.rejected<0)throw Error('Missing current replay diagnostics');}
  if(!Array.isArray(r.experimental_errors)||r.experimental_errors.length!==2||!channels.every(c=>r.experimental_errors.filter(x=>x.channel===c&&finite(x.rmse)).length===1))throw Error('Missing current replay measurement errors');
  if(!/^[a-f0-9]{40}$/.test(r.source_commit)||!['artifact_sha256','current_definition_sha256','archived_definition_sha256'].every(k=>/^[a-f0-9]{64}$/.test(r[k])))throw Error('Missing current replay identity');
  if(!Array.isArray(r.limitations)||!r.limitations.length||!r.limitations.every(x=>typeof x==='string'))throw Error('Missing current replay limits');
  if(!Array.isArray(r.sources)||r.sources.length!==2||!r.sources.every(s=>{try{return typeof s.title==='string'&&new URL(s.url).protocol==='https:';}catch{return false;}}))throw Error('Unsafe current replay sources');
  return r;
}
export function validatePropagation(data){
  if(data?.kind!=='kfs-propagation-summary'||data.schema_version!=='0.1'||data.status!=='provisional'||data.scientific_admission!==false||data.evaluation_tests!==6||!/^[a-f0-9]{64}$/.test(data.definition_sha256))throw Error('Unsupported propagation evidence');
  if(!Array.isArray(data.panels)||data.panels.length!==4||!ids.every(c=>ids.every(e=>data.panels.filter(r=>r.calibration_scenario===c&&r.evaluation_scenario===e&&finite(r.root_scaled_mse)).length===1)))throw Error('Incomplete factorial scores');
  if(!Array.isArray(data.selections)||data.selections.length!==2||!ids.every(id=>data.selections.filter(s=>s.scenario===id&&Number.isInteger(s.seed)&&finite(s.alpha)).length===1)||data.calibration?.selection!=='calibration_only'||data.calibration.starts_per_scenario!==3||data.calibration.candidate_budget_per_start!==96||data.calibration.all_budget_limited!==true)throw Error('Missing calibration-only selection or budgets');
  for(const r of [data.original_refinement,data.nested]){
    if(!r||!Number.isInteger(r.case_channel_checks)||!Number.isInteger(r.separation_passes)||!Number.isInteger(r.nonincrease_failures)||r.separation_passes<0||r.separation_passes>r.case_channel_checks||!Array.isArray(r.failed)||r.failed.length!==r.nonincrease_failures||!finite(r.maximum_fraction)||!finite(r.limit_fraction)||r.limit_fraction<=0||typeof r.numerical_passed!=='boolean'||r.numerical_passed!==(r.nonincrease_failures===0&&r.separation_passes===r.case_channel_checks))throw Error('Inconsistent refinement outcome');
  }
  const o=data.original_refinement,n=data.nested;
  if(o.case_channel_checks!==32||o.passed!==o.numerical_passed||n.case_channel_checks!==8||typeof n.rejection_free!=='boolean'||n.passed!==(n.numerical_passed&&n.rejection_free)||!Number.isInteger(n.caller_points)||n.caller_points<=0||!finite(n.ratio_min)||!finite(n.ratio_max)||n.ratio_min>n.ratio_max)throw Error('Conflated refinement outcomes');
  if(!Array.isArray(n.rows)||n.rows.length!==8||!ids.every(c=>['KFS-TMD7','KFS-TMD9'].every(t=>channels.every(ch=>n.rows.filter(r=>r.calibration_scenario===c&&r.test===t&&r.channel===ch&&finite(r.first_change)&&finite(r.second_change)).length===1))))throw Error('Incomplete nested coverage');
  if(!Array.isArray(data.limitations)||!data.limitations.length||!data.limitations.every(x=>typeof x==='string'))throw Error('Missing propagation limits');
  if(!Array.isArray(data.sources)||!data.sources.length||!data.sources.every(s=>{try{return typeof s.title==='string'&&new URL(s.url).protocol==='https:';}catch{return false;}}))throw Error('Unsafe propagation sources');
  validateCurrentReplay(data.current_replay);
  return data;
}
export function propagationView(data,calibration,evaluation){
  validatePropagation(data);
  if(!ids.includes(calibration)||!ids.includes(evaluation))throw Error('Unknown propagation scenario');
  const score=data.panels.find(r=>r.calibration_scenario===calibration&&r.evaluation_scenario===evaluation).root_scaled_mse;
  const baseline=data.panels.find(r=>r.calibration_scenario===ids[0]&&r.evaluation_scenario===ids[0]).root_scaled_mse;
  const selection=data.selections.find(r=>r.scenario===calibration);
  return {score,relativeChange:baseline?score/baseline-1:null,seed:selection.seed,alpha:selection.alpha};
}
export async function mountPropagation(doc,fetcher=fetch){
  const status=doc.getElementById('propagation-status');
  try{
    const response=await fetcher('./development.json');if(!response.ok)throw Error('Evidence download failed');
    const data=validatePropagation((await response.json()).propagation);
    const element=(tag,text)=>{const node=doc.createElement(tag);node.textContent=text;return node;};
    const cal=doc.getElementById('calibration-scenario'),evaluation=doc.getElementById('evaluation-scenario');
    for(const select of [cal,evaluation]){
      select.replaceChildren(...ids.map(id=>{const option=element('option',label(id));option.value=id;return option;}));
      select.disabled=false;
    }
    function update(){
      const view=propagationView(data,cal.value,evaluation.value);
      doc.getElementById('propagation-selection').textContent='Selected error: '+view.score.toFixed(6)+
        ' ('+(view.relativeChange===null?'undefined change':(100*view.relativeChange).toFixed(3)+'% from file/file')+'). Calibration-selected seed '+view.seed+', alpha '+view.alpha.toFixed(6)+'.';
      doc.getElementById('propagation-panels').replaceChildren(...data.panels.map(row=>{
        const tr=element('tr','');tr.setAttribute('aria-current',String(row.calibration_scenario===cal.value&&row.evaluation_scenario===evaluation.value));
        tr.append(element('td',label(row.calibration_scenario)),element('td',label(row.evaluation_scenario)),element('td',row.root_scaled_mse.toFixed(6)));return tr;
      }));
    }
    cal.addEventListener('change',update);evaluation.addEventListener('change',update);update();
    const original=data.original_refinement,nested=data.nested;
    doc.getElementById('propagation-original').textContent='Original sequence: '+(original.passed?'PASS':'FAIL')+'. '+original.nonincrease_failures+
      ' of '+original.case_channel_checks+' case/channel checks fail nonincrease. All '+original.separation_passes+' meet separation; largest change '+(100*original.maximum_fraction).toFixed(3)+'% of the calibration-response shift (limit '+(100*original.limit_fraction).toFixed(1)+'%).';
    doc.getElementById('propagation-failures').replaceChildren(...original.failed.map(r=>{
      const tr=element('tr','');for(const value of [r.test+' / '+label(r.calibration_scenario),channelLabel(r.channel),r.first_change.toExponential(3),r.second_change.toExponential(3)])tr.append(element('td',value));return tr;
    }));
    doc.getElementById('propagation-nested').textContent='Separate nested caller regime: '+(nested.passed?'PASS':'FAIL')+'. '+nested.caller_points+
      ' caller points; rejection-free diagnostic '+(nested.rejection_free?'passes':'fails')+'. Largest change '+(100*nested.maximum_fraction).toFixed(4)+
      '% of the calibration-response shift. Later/earlier ratios '+nested.ratio_min.toFixed(3)+'–'+nested.ratio_max.toFixed(3)+'.';
    doc.getElementById('nested-rows').replaceChildren(...nested.rows.map(r=>{
      const tr=element('tr','');for(const value of [r.test+' / '+label(r.calibration_scenario),channelLabel(r.channel),r.first_change.toExponential(3),r.second_change.toExponential(3)])tr.append(element('td',value));return tr;
    }));
    doc.getElementById('propagation-limits').replaceChildren(...data.limitations.map(x=>element('li',x)));
    doc.getElementById('propagation-sources').replaceChildren(...data.sources.map(s=>{const li=element('li',''),a=element('a',s.title);a.href=s.url;li.append(a);return li;}));
    const replay=data.current_replay;
    doc.getElementById('current-replay-status').textContent='Current native / archived compatibility: '+(replay.passed?'PASS':'FAIL')+'. '+replay.observations+' observations, '+replay.segments+' loading segments, '+replay.rows.filter(r=>r.passed).length+' of 7 gates pass.';
    doc.getElementById('current-replay-rows').replaceChildren(...replay.rows.map(r=>{
      const tr=element('tr','');for(const value of [replayQuantities[r.quantity],r.maximum_difference.toExponential(3),r.limit.toExponential(1),r.passed?'PASS':'FAIL'])tr.append(element('td',value));return tr;
    }));
    const diagnosticText=engine=>{const d=replay.diagnostics[engine];return engine+': '+d.caller_increments+' caller increments, '+d.substeps+' substeps, '+d.rejected+' rejections';};
    doc.getElementById('current-replay-diagnostics').textContent=diagnosticText('archived')+'; '+diagnosticText('current')+'.';
    const errors=Object.fromEntries(replay.experimental_errors.map(r=>[r.channel,r.rmse]));
    doc.getElementById('current-replay-errors').textContent='Agreement between engines does not remove experimental error. Current prediction RMSE: q '+(errors.q/1000).toFixed(3)+' kPa; volume strain '+errors.volumetric_strain.toFixed(6)+'. These descriptive errors remain effectively unchanged.';
    doc.getElementById('current-replay-identity').textContent='Native source commit: '+replay.source_commit+'. Executable SHA-256: '+replay.artifact_sha256+'.';
    doc.getElementById('current-replay-limits').replaceChildren(...replay.limitations.map(x=>element('li',x)));
    doc.getElementById('current-replay-sources').replaceChildren(...replay.sources.map(s=>{const li=element('li',''),a=element('a',s.title);a.href=s.url;li.append(a);return li;}));
    status.textContent='Four saved sensitivity panels loaded. Both selections used calibration only: three starts per scenario, 96 candidates per start; all exhausted the budget. Model admission remains pending; see the separate reporting review.';
  }catch(error){const replayStatus=doc.getElementById('current-replay-status');if(replayStatus){replayStatus.textContent='Current replay evidence unavailable.';replayStatus.setAttribute('role','alert');}status.textContent='Propagation evidence unavailable: '+error.message;status.setAttribute('role','alert');}
}
if(typeof document!=='undefined')mountPropagation(document);
