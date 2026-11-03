from pathlib import Path
p=Path('web/ensemble-view.mjs');s=p.read_text();s=s.replace("import {createEnsemblePlot}","import {loadEnsembleCatalogue,fetchEnsembleTest,filterTests,replayGap} from './ensemble-experiments.mjs';\nimport {createEnsemblePlot}")
a=s.index('async function loadExperiment(){');b=s.index('function workerExecutor',a);s=s[:a]+s[b:]
a=s.index(' const [record,catalogue]=');b=s.index(' modelIds=',a);s=s[:a]+''' const [entries,catalogue]=await Promise.all([loadEnsembleCatalogue(),fetch('./models.json').then(r=>{if(!r.ok)throw Error('Model catalogue unavailable.');return r.json();})]);
 let entry=entries.find(e=>e.id==='OPARA-TXCD-100')||entries[0];
 if(!entry)throw Error('No tests available.');
 let record=await fetchEnsembleTest(entry),testGap='',loading=false,testSequence=0;
 if(entry.replay)validateExperiment(record);else testGap=replayGap(record)||'No verified replay loading asset is available for this record.';
''' +s[b:]
a=s.index(" const experiment=node('section'");b=s.index(" const exclusions=",a)
s=s[:a]+''' const testControls=node('section',undefined,'model-card ensemble-test-controls');
 const searchLabel=node('label','Find a test'),search=node('input');search.type='search';search.id='ensemble-test-search';search.placeholder='Material or test ID';searchLabel.append(search);
 const protocolLabel=node('label','Test type'),protocol=node('select');protocol.id='ensemble-test-protocol';protocol.append(new Option('All test types',''));for(const value of [...new Set(entries.map(e=>e.protocol))].sort())protocol.append(new Option(value.replaceAll('-',' '),value));protocolLabel.append(protocol);
 const availabilityLabel=node('label','Availability'),availability=node('select');availability.id='ensemble-test-availability';for(const [text,value]of [['All records',''],['Ensemble replay','replay'],['Measurements only','source']])availability.append(new Option(text,value));availabilityLabel.append(availability);
 const testLabel=node('label','Experimental test'),testSelect=node('select');testSelect.id='ensemble-test';testLabel.append(testSelect);const testCount=node('p',undefined,'control-hint');testCount.id='ensemble-test-count';testControls.append(searchLabel,protocolLabel,availabilityLabel,testLabel,testCount);root.append(testControls);
 function filterOptions(){const filtered=filterTests(entries,{search:search.value,protocol:protocol.value,availability:availability.value});testSelect.replaceChildren();if(!filtered.some(e=>e.id===entry.id))testSelect.append(new Option('Current: '+entry.id,entry.id));for(const e of filtered)testSelect.append(new Option(e.id+' · '+e.material+' · '+(e.replay?'ensemble':'measurements'),e.id));testSelect.value=entry.id;testCount.textContent=filtered.length+' matching / '+entries.length+' records · '+entries.filter(e=>e.replay).length+' ready for ensemble replay';}
 search.oninput=protocol.onchange=availability.onchange=filterOptions;
 const experiment=node('section',undefined,'model-card'),testHeading=node('h2'),testDescription=node('p'),source=node('a','Source experiment ↗'),gapNote=node('p',undefined,'ensemble-gap');gapNote.id='ensemble-test-gap';gapNote.setAttribute('role','status');source.target='_blank';source.rel='noopener noreferrer';experiment.append(testHeading,testDescription,source,gapNote);
 const loadingNote=node('p'),warnings=node('div');
 const disclosure=node('details');disclosure.append(node('summary','Loading, preparation and comparison assumptions'),loadingNote,node('p','All baselines are illustrative and uncalibrated for the selected specimen. Measured effective stress and void ratio initialize replay; other history uses the displayed unmeasured model assumptions. No consolidation history or physical-time evolution is inferred. Unsupported source channels are available for inspection without inventing a loading contract.'),warnings);experiment.append(disclosure);root.append(experiment);
 const confinementLabel=node('label','Confinement input'),confinement=node('select');confinement.id='ensemble-confinement';confinementLabel.htmlFor=confinement.id;for(const [value,text]of [['recorded','Recorded radial stress · includes measured fluctuations'],['constant','Constant starting radial stress · idealized comparison']])confinement.append(new Option(text,value));confinementLabel.append(confinement);experiment.append(confinementLabel);
 const sourceControls=node('div',undefined,'ensemble-source-controls'),sourceX=node('select'),sourceY=node('select');sourceX.id='ensemble-source-x';sourceY.id='ensemble-source-y';for(const [text,input]of [['X channel',sourceX],['Y channel',sourceY]]){const label=node('label',text);label.append(input);sourceControls.append(label);}experiment.append(sourceControls);
''' +s[b:]
s=s.replace("const charts={};for(const channel of ['stress','volume'])", "const charts={},panels={};for(const channel of ['stress','volume','path','pore','source'])")
s=s.replace("heading=node('h2',channel==='stress'?'Deviator stress':'Volumetric strain · compression positive')", "heading=node('h2',({stress:'Deviator stress',volume:'Volumetric strain · compression positive',path:'Effective stress path',pore:'Pore-pressure change',source:'Source measurements'})[channel])")
s=s.replace('panel.append(heading,chart,error);results.append(panel);','panel.append(heading,chart,error);results.append(panel);panels[channel]=panel;')
a=s.index(' function describeLoading(){');b=s.index(' function refreshCount()',a)
s=s[:a]+''' function updateTestInfo(){
  testHeading.textContent=entry.id+' · '+entry.protocol.replaceAll('-',' ');
  testDescription.textContent=record.material+' · '+record.rows.length.toLocaleString()+' observations'+(record.initial?.effective_stress?' · initial radial effective stress '+(record.initial.effective_stress[1]/1000).toFixed(2)+' kPa · e₀ = '+record.initial.void_ratio:'');
  source.href=record.provenance?.source_url||record.provenance?.license_url||'#';source.hidden=!record.provenance?.source_url;
  gapNote.textContent=testGap?'Measurements only. '+testGap:'Ensemble replay · all observations retained in acquisition order.';
  warnings.replaceChildren(...(record.warnings||[]).map(w=>node('p',w)),node('p',record.provenance?.attribution||''));
  const native=record.kind&&record.kind!=='experiment';sourceControls.hidden=!native;
  if(native)for(const [input,key]of [[sourceX,'x'],[sourceY,'y']]){input.replaceChildren();for(const c of record.columns)input.append(new Option(c.name+' ('+c.unit+')',c.key));input.value=record.source_plot[key];}
  confinementLabel.hidden=!!testGap||record.protocol==='undrained-triaxial';
  controls.hidden=!!testGap;legend.hidden=!!testGap;outcomes.hidden=detail.hidden=!!testGap;
  for(const [channel,panel]of Object.entries(panels))panel.hidden=native?channel!=='source':channel==='source'||channel==='pore'&&record.protocol!=='undrained-triaxial'||channel==='path'&&!record.rows.some(r=>Number.isFinite(r.p)||Number.isFinite(r.radial_effective_stress))||channel==='volume'&&!record.rows.some(r=>Number.isFinite(r.volumetric_strain));
 }
 function describeLoading(){loadingNote.textContent=testGap?testGap:record.protocol==='undrained-triaxial'?'Idealized undrained replay: impose acquired axial strain, zero volumetric strain and equal lateral effective stresses. Measured effective radial stress is an output comparison, not imposed loading. Pore-pressure change is inferred from measured cell-pressure change minus predicted lateral effective-stress change; saturated incompressible response is assumed.':confinement.value==='constant'?'Axial strain follows acquired endpoints; radial effective stress is held at its measured starting value. This is an idealized loading comparison; measured curves are unchanged.':'Acquired axial strain and measured membrane-corrected radial effective stress are imposed. This is a conditional comparison: the membrane correction uses measured specimen volume.';}
''' +s[b:]
s=s.replace("function refreshCount(){for", "function refreshCount(){if(loading||testGap)return;for")
s=s.replace('  describeLoading();','  if(loading)return;\n  describeLoading();')
s=s.replace("for(const chart of Object.values(charts))chart.update(record,jobs.filter(j=>!hidden.has(j.model)),selected,styles,viewRevision);", "for(const [channel,chart]of Object.entries(charts))if(!panels[channel].hidden)chart.update(record,jobs.filter(j=>!hidden.has(j.model)),selected,styles,viewRevision);")
s=s.replace(' async function start(prepared){',' async function start(prepared){\n  if(loading||testGap)return;')
s=s.replace(' function schedule(delay=350){',' function schedule(delay=350){\n  if(loading||testGap)return;')
s=s.replace("download('opara-txcd100-ensemble.json'", "download(record.id+'-ensemble.json'")
s=s.replace("job.model+'-opara-recorded.json'", "job.model+'-'+record.id+'-recorded.json'")
# Replayed exports select their own test and validate exact identity, not the previous selection.
a=s.index(' importButton.onclick=');b=s.index(" window.addEventListener('pagehide'",a)
s=s[:a]+''' async function selectTest(id,{run=true}={}){
  const requested=++testSequence;const next=entries.find(e=>e.id===id);if(!next)throw Error('Test is absent from this catalogue.');
  ++revision;clearPending();queue.cancel();loading=true;study=null;selected=null;stale=false;save.disabled=true;single.disabled=open.disabled=true;list.replaceChildren();raw.textContent='';detailText.textContent='Select a run to inspect its inputs.';gapNote.textContent='Loading '+id+'…';controls.hidden=true;outcomes.hidden=detail.hidden=legend.hidden=true;sourceControls.hidden=true;for(const panel of Object.values(panels))panel.hidden=true;
  try{
   const loaded=await fetchEnsembleTest(next);if(requested!==testSequence)return false;
   if(next.replay)validateExperiment(loaded);
   await activeRun;if(requested!==testSequence)return false;
   entry=next;record=loaded;testGap=entry.replay?'':replayGap(record)||'No verified replay loading asset is available for this record.';loading=false;++viewRevision;
   testSelect.value=entry.id;updateTestInfo();refreshCount();render();if(run&&!testGap)schedule(0);return true;
  }catch(error){if(requested===testSequence){loading=true;gapNote.textContent='Unable to load '+id+': '+error.message;testSelect.value=id;}return false;}
 }
 testSelect.onchange=()=>{void selectTest(testSelect.value);};
 sourceX.onchange=sourceY.onchange=()=>{record={...record,source_plot:{x:sourceX.value,y:sourceY.value}};++viewRevision;render();};
 importButton.onclick=()=>file.click();file.onchange=async()=>{try{
  const item=file.files[0];if(!item)return;if(item.size>100*1024*1024)throw Error('Import exceeds 100 MB.');
  const text=await item.text();const doc=JSON.parse(text),id=doc.study?.experiment?.id;
  const selectedTest=await selectTest(id,{run:false});if(!selectedTest)return;const selection=testSequence;
  const prepared=importStudy(text,catalogue,record);if(selection!==testSequence)return;
  populate(prepared.configurations);confinement.value=studyConfinement(prepared);refreshCount();await start(prepared);
 }catch(error){status.textContent='Import rejected: '+error.message;}finally{file.value='';}};
''' +s[b:]
s=s.replace(' populate(defaultConfigurations(catalogue));refreshCount();render();root.dataset.ready', ' populate(defaultConfigurations(catalogue));filterOptions();updateTestInfo();refreshCount();render();root.dataset.ready')
s=s.replace("if(!study&&pendingRun===null&&!activeRun)schedule(0)","if(!loading&&!testGap&&!study&&pendingRun===null&&!activeRun)schedule(0)")
p.write_text(s)
p=Path('web/ensemble.css');s=p.read_text()+'''\n#ensemble .ensemble-test-controls{display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px 14px}
#ensemble .ensemble-test-controls label{min-width:0;margin:0}
#ensemble .ensemble-test-controls select,#ensemble .ensemble-test-controls input{width:100%;box-sizing:border-box;min-width:0}
#ensemble .ensemble-test-controls label:has(#ensemble-test),#ensemble-test-count{grid-column:1/-1}
#ensemble .ensemble-gap{font-size:13px;line-height:1.5}
#ensemble .ensemble-source-controls{display:grid;grid-template-columns:1fr 1fr;gap:12px}
#ensemble [hidden]{display:none!important}
@media(max-width:520px){#ensemble .ensemble-test-controls{grid-template-columns:1fr 1fr}#ensemble .ensemble-test-controls label:has(#ensemble-test-search){grid-column:1/-1}}
''';p.write_text(s)
