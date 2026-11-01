// Verify downloadable artifact identity without executing any material engine.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function validateDatabasePackage(directory){
 const read=name=>readFileSync(join(directory,name));
 const manifest=JSON.parse(read('atlas-database.json'));
 assert.equal(manifest.kind,'constitutive-atlas-database-package','Unknown database package');
 assert.equal(manifest.schema_version,'0.1','Unknown database manifest version');
 assert.equal(manifest.database?.path,'atlas.sqlite','Unexpected database download path');
 assert.equal(manifest.database.media_type,'application/vnd.sqlite3','Unexpected database media type');
 const database=read('atlas.sqlite');
 assert.ok(database.subarray(0,16).equals(Buffer.from('SQLite format 3\0')),'Invalid SQLite header');
 assert.equal(database.length,manifest.database.bytes,'Database download size differs');
 assert.equal(sha(database),manifest.database.sha256,'Database download checksum differs');
 for(const name of ['models.json','catalogue.json']){
  assert.equal(sha(read(name)),manifest.package_inputs?.[name],'Database package input differs: '+name);
 }
 const models=JSON.parse(read('models.json')).models;
 assert.ok(Array.isArray(models),'Missing packaged models');
 const ids=models.map(model=>model.id),declared=manifest.ordinary_engine_model_ids;
 assert.ok(Array.isArray(declared)&&declared.every(id=>typeof id==='string'),'Missing database engine membership');
 assert.equal(new Set(declared).size,declared.length,'Duplicate database engine membership');
 assert.deepEqual([...declared].sort(),[...ids].sort(),'Database engine membership differs');
 for(const flag of ['measurements_included','source_documents_included','compiled_engines_included']){
  assert.equal(manifest[flag],false,'Unexpected database content declaration: '+flag);
 }
 return manifest;
}
