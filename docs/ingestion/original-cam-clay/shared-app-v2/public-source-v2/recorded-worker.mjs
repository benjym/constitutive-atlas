// Shared worker dispatch, isolated from engine initialization for contract tests.
import {runRecorded} from './recorded.mjs';
import {runScopedRecorded} from './recorded-scope-execution.mjs';
import {parseRecordedDocument,createRecordedDocument} from './recorded-document.mjs';
export function replayRecorded(engine,specification,catalogue){
 const s=parseRecordedDocument(JSON.stringify(specification),catalogue).specification;
 const result=s.version==='experimental-recorded-run-0.2'?runScopedRecorded(engine,s,catalogue):runRecorded(engine,s);
 return createRecordedDocument(s,result,catalogue).result;
}
