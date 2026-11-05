import assert from 'node:assert/strict';import{readFileSync,lstatSync,realpathSync}from'node:fs';import{join,resolve}from'node:path';import{createHash}from'node:crypto';import{strictJSON}from'/private/tmp/atlas-baseline-delivery-20261105/source/web/controlled-time-engine.mjs';const hash=b=>createHash('sha256').update(b).digest('hex');
// Historical authority remains literal; this admits only the separately reviewed C4 source view.
export function controlledTimePackagerSources(root,expected){
 const packager='tools/build_controlled_time_web.py';
 const read=name=>{assert.ok(!name.startsWith('/')&&!name.split('/').includes('..'),'Unsafe source view path');const path=join(root,name);assert.ok(lstatSync(path).isFile()&&!lstatSync(path).isSymbolicLink(),'Nonregular source view member');assert.equal(realpathSync(path),resolve(path),'Source view symlink');return readFileSync(path);};
 const snapshot={};const pin=(name,sha)=>{const body=read(name);assert.equal(hash(body),sha,'Changed source view: '+name);snapshot[name]=hash(body);return body;};
 if(hash(read(packager))===expected){pin(packager,expected);return snapshot;}
 assert.equal(expected,'02b1dd6e36c2c23ca91a78d321c4af5060dd7b68dbf8385e142061f4149a4758','Unknown historical packager');
 const packet='docs/delivery/unheld-finalisation-20261105-v1/';
 const proof=strictJSON(pin(packet+'interface-receipt-source-closure-v1/proof.json','54f68390c72d71374799e3ecd427f93e3d9384df72a4c030e8ceee0a08bc6edd').toString());
 const review=strictJSON(pin(packet+'shared-current17-review-v1/interface-receipt-source-closure-v1/source-view-decision.json','4fec2a1da7ee05f253f7c5f5cb3c98dc69d545fd014de212fa2cef6e4174f970').toString());
 assert.equal(proof.identity,'interface-receipt-current-source-view-proof-v1');
 assert.equal(review.identity,'interface-receipt-current-source-view-review-v1');assert.equal(review.decision,'accepted');assert.equal(review.author_run,'/root/baseline_migration');assert.ok(typeof review.reviewer_run==='string'&&review.reviewer_run.trim()&&review.reviewer_run!==review.author_run);assert.deepEqual(review.unresolved_blockers,[]);assert.equal(review.proof_sha256,'54f68390c72d71374799e3ecd427f93e3d9384df72a4c030e8ceee0a08bc6edd');assert.deepEqual(review.implementation,proof.implementation);
 for(const [name,sha]of Object.entries(proof.implementation))pin(name,sha);
 for(const [name,sha]of Object.entries(proof.ancestors))pin(name,sha);
 for(const [name,alias]of Object.entries(proof.aliases)){pin(name,alias.current_sha256);pin(alias.archive,alias.predecessor_sha256);}
 assert.equal(proof.aliases[packager].predecessor_sha256,expected);assert.equal(proof.implementation[packager],proof.aliases[packager].current_sha256);
 return snapshot;
}

