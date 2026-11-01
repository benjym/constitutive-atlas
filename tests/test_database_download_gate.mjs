import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,writeFileSync,rmSync,unlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {validateDatabasePackage} from '../tools/validate_database_package.mjs';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
function fixture(fn){
 const dir=mkdtempSync(join(tmpdir(),'atlas-database-gate-'));
 const models=JSON.stringify({models:[{id:'one'}]}),catalogue=JSON.stringify({models:[{id:'one',executable:true}]});
 // Header-only synthetic bytes test identity checks, not SQLite semantics.
 const database=Buffer.from('SQLite format 3\0synthetic bytes');
 const manifest={kind:'constitutive-atlas-database-package',schema_version:'0.1',database:{path:'atlas.sqlite',media_type:'application/vnd.sqlite3',sha256:sha(database),bytes:database.length},package_inputs:{'models.json':sha(models),'catalogue.json':sha(catalogue)},ordinary_engine_model_ids:['one'],measurements_included:false,source_documents_included:false,compiled_engines_included:false};
 const put=(file,value)=>writeFileSync(join(dir,file),value);
 const save=()=>put('atlas-database.json',JSON.stringify(manifest));
 put('models.json',models);put('catalogue.json',catalogue);put('atlas.sqlite',database);save();
 try{fn({dir,put,manifest,save,database});}finally{rmSync(dir,{recursive:true,force:true});}
}
test('download identities match the packaged model and discovery bytes',()=>fixture(({dir})=>assert.equal(validateDatabasePackage(dir).kind,'constitutive-atlas-database-package')));
for(const file of ['atlas.sqlite','atlas-database.json','models.json','catalogue.json']){
 test('missing '+file+' blocks package',()=>fixture(({dir})=>{unlinkSync(join(dir,file));assert.throws(()=>validateDatabasePackage(dir));}));
}
for(const [name,mutate] of [
 ['wrong kind',m=>m.kind='other'],['wrong version',m=>m.schema_version='2'],
 ['unsafe filename',m=>m.database.path='../atlas.sqlite'],['wrong MIME',m=>m.database.media_type='text/plain'],
 ['wrong database hash',m=>m.database.sha256='0'.repeat(64)],['wrong size',m=>m.database.bytes++],
 ['wrong model hash',m=>m.package_inputs['models.json']='0'.repeat(64)],
 ['wrong catalogue hash',m=>m.package_inputs['catalogue.json']='0'.repeat(64)],
 ['missing membership',m=>delete m.ordinary_engine_model_ids],
 ['different membership',m=>m.ordinary_engine_model_ids=['two']],
 ['duplicate membership',m=>m.ordinary_engine_model_ids=['one','one']],
 ['measurement declaration',m=>m.measurements_included=true],
 ['source document declaration',m=>m.source_documents_included=true],
 ['engine declaration',m=>m.compiled_engines_included=true],
 ['missing declaration',m=>delete m.measurements_included],
])test(name+' blocks package',()=>fixture(({dir,manifest,save})=>{mutate(manifest);save();assert.throws(()=>validateDatabasePackage(dir));}));
test('corrupted database bytes block package',()=>fixture(({dir,put,database})=>{database[database.length-1]^=1;put('atlas.sqlite',database);assert.throws(()=>validateDatabasePackage(dir),/checksum/);}));
test('non-SQLite bytes reject even with matching checksum',()=>fixture(({dir,put,manifest,save})=>{const bytes=Buffer.from('not SQLite');put('atlas.sqlite',bytes);manifest.database.sha256=sha(bytes);manifest.database.bytes=bytes.length;save();assert.throws(()=>validateDatabasePackage(dir),/header/);}));
for(const file of ['models.json','catalogue.json'])test('changed packaged '+file+' blocks stale database',()=>fixture(({dir,put})=>{put(file,'{"models":[]}');assert.throws(()=>validateDatabasePackage(dir),/input differs/);}));
