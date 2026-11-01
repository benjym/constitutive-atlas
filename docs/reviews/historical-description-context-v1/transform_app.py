def transform(source):
    old="import {formulationSection} from './formulation-view.mjs';"
    assert old in source
    source=source.replace(old,"import {formulationSection,recordedDescription} from './formulation-view.mjs';")
    old="evidenceIndex=validateEvidenceIndex(await response.json());evidenceState='loaded';"
    assert source.count(old)==1
    source=source.replace(old,old+'refreshRecordedDescriptions();')
    helper='''function refreshRecordedDescriptions(){
  const selected=models.find(m=>m.id===$('model').value);
  if(selected){
    $('model-description').textContent=recordedDescription(selected.description,selected.id,evidenceIndex);
    const equationDescription=$('equation-content')?.querySelector('p');
    if(equationDescription)equationDescription.textContent=recordedDescription(selected.description,selected.id,evidenceIndex);
  }
  const id=catalogueRoute(location.hash).modelId,entry=catalogue.find(e=>e.id===id);
  if(!entry||!$('catalogue-dialog').open)return;
  const spec=models.find(m=>m.id===id),body=$('catalogue-detail-body');
  const note=body.querySelector('.catalogue-detail-note');
  if(note)note.textContent=recordedDescription(entry.note||spec?.description||'Bibliographic and formulation review pending.',id,evidenceIndex);
  const description=body.querySelector('.definition-description');
  if(description&&spec)description.textContent=recordedDescription(spec.description,id,evidenceIndex);
}
'''
    marker='function restoreCatalogueFocus(){';assert marker in source
    source=source.replace(marker,helper+marker)
    if "$('model-description').textContent=entry?.dossier?entry.note:m.description;" in source:
        source=source.replace("$('model-description').textContent=entry?.dossier?entry.note:m.description;","$('model-description').textContent=recordedDescription(entry?.dossier?entry.note:m.description,m.id,evidenceIndex);")
    else:
        old="$('model-description').textContent=m.description;";assert old in source
        source=source.replace(old,"$('model-description').textContent=recordedDescription(m.description,m.id,evidenceIndex);")
    old="content.replaceChildren(element('p',m.description));";assert old in source
    source=source.replace(old,"content.replaceChildren(element('p',recordedDescription(m.description,m.id,evidenceIndex)));")
    old="element('p',entry.note||spec?.description||'Bibliographic and formulation review pending.','catalogue-detail-note')";assert old in source
    source=source.replace(old,"element('p',recordedDescription(entry.note||spec?.description||'Bibliographic and formulation review pending.',entry.id,evidenceIndex),'catalogue-detail-note')")
    old='formulationSection(document,spec)';assert old in source
    source=source.replace(old,'formulationSection(document,spec,{evidenceIndex})')
    return source
