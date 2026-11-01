// Package only explicitly registered documents; never generate numerical results.
import {readFile,writeFile,mkdir,realpath}from 'node:fs/promises';
import {resolve,join,sep}from 'node:path';
import {webcrypto}from 'node:crypto';
import {fileURLToPath}from 'node:url';
import {validateExampleIndex,prepareExample}from '../web/laboratory-examples.mjs';
export async function bundle(root,destination,catalogue){
 root=await realpath(root);const read=async(path)=>{const full=await realpath(resolve(root,path));if(!full.startsWith(root+sep))throw Error('Example path escapes source root.');return readFile(full,'utf8');};
 const manifest=JSON.parse(await read('catalogue/laboratory-examples.json'));if(manifest.schema_version!=='0.1'||!Array.isArray(manifest.examples))throw Error('Unsupported laboratory-example manifest.');
 const index={schema_version:'0.1',catalogue_hash:catalogue.sha256,examples:[]},assets=new Map();
 for(const entry of manifest.examples){
  if(typeof entry.document_path!=='string'||!/^protocols\/[a-z0-9-]+\.json$/.test(entry.document_path))throw Error('Invalid example source path.');
  const published={...entry,document_url:'./laboratory-examples/'+entry.id+'.json',definition_url:'./models/'+entry.model+'.json'};delete published.document_path;
  index.examples.push(published);assets.set(published.document_url,await read(entry.document_path));assets.set(published.definition_url,await read('models/'+entry.model+'.json'));
 }
 validateExampleIndex(index,catalogue);
 for(const entry of index.examples)await prepareExample(entry,index,catalogue,{crypto:webcrypto,fetcher:async url=>({ok:assets.has(url),text:async()=>assets.get(url)})});
 // Validate the whole index before modifying output, including an empty index.
 await mkdir(destination,{recursive:true});await mkdir(join(destination,'laboratory-examples'),{recursive:true});
 for(const entry of index.examples)await writeFile(join(destination,'laboratory-examples',entry.id+'.json'),assets.get(entry.document_url));
 await writeFile(join(destination,'laboratory-examples.json'),JSON.stringify(index,null,2)+'\n');return index;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const [root,destination,catalogueFile]=process.argv.slice(2);if(!root||!destination||!catalogueFile)throw Error('Expected root, destination, compiled catalogue JSON.');await bundle(root,destination,JSON.parse(await readFile(catalogueFile,'utf8')));
}
