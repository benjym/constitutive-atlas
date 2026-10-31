import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
const bad=[null,false,'',{length:0}];
const report={candidateCalls:0,originalFalsePasses:bad.map(points=>({points,accepted:!points||points.length===0})),strictRejects:bad.map(points=>!Array.isArray(points)),unitOkFalsePasses:[null,0].map(ok=>({ok,assertFalseWouldPass:!ok}))};
assert.ok(report.originalFalsePasses.every(x=>x.accepted));
writeFileSync(new URL('harness-original-witnesses.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log('Four original observer shape false passes and two unittest truthiness false passes retained; no candidate calls.');
