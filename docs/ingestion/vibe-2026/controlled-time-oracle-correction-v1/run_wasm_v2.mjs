// Opt-in corpus-only source runner. Default/--inspect never evaluates target modules.
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';import vm from 'node:vm';
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../../../..'),proof=JSON.parse(fs.readFileSync(path.join(here,'runner-delta-proof.json'))),entry=proof.runners.find(x=>x.kind==='wasm'),hash=b=>createHash('sha256').update(b).digest('hex');
const original=path.join(root,entry.original_path),source=fs.readFileSync(path.join(here,entry.snapshot),'utf8'),before=fs.readFileSync(original,'utf8');
if(hash(Buffer.from(before))!==entry.original_sha256||hash(Buffer.from(source))!==entry.snapshot_sha256||hash(fs.readFileSync(path.join(root,entry.new_corpus_path)))!==proof.corpus_sha256||source.split(entry.new_corpus_path).length-1!==entry.literal_occurrences||source.replaceAll(entry.new_corpus_path,entry.old_corpus_path)!==before)throw Error('Frozen corpus-only runner proof changed');
if(!process.argv.includes('--execute')){console.log(JSON.stringify(proof,null,2));process.exit(0);}
if(process.argv.includes('--inspect'))throw Error('Choose inspect or execution');
if(typeof vm.SourceTextModule!=='function')throw Error('Explicit reviewed execution requires node --experimental-vm-modules');
process.argv.splice(process.argv.indexOf('--execute'),1);
// The only transformed source bytes select the corpus. Preserve original import.meta.url
// so all unmodified fixture and receipt URLs resolve exactly as in the original tools runner.
const module=new vm.SourceTextModule(source,{identifier:pathToFileURL(original).href,initializeImportMeta(meta){meta.url=pathToFileURL(original).href;},importModuleDynamically:specifier=>import(specifier)});
await module.link(async specifier=>{if(!specifier.startsWith('node:'))throw Error('Unexpected static runner import');const namespace=await import(specifier),names=Object.keys(namespace);return new vm.SyntheticModule(names,function(){for(const name of names)this.setExport(name,namespace[name]);},{identifier:specifier});});
await module.evaluate();
