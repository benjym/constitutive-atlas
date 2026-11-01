// Literal exact controls only; no Wasm or solver.
import {readFileSync,writeFileSync}from 'node:fs';
import {createLoading}from '../../../web/loading.mjs';
const rows=JSON.parse(readFileSync(new URL('../gis2024-browser-preparation-v1/laboratory-cases.json',import.meta.url),'utf8')).cases;
for(const row of rows)if(row.loading_wire==='exact')row.specification.loading=createLoading(row.specification);
writeFileSync(new URL('./laboratory-requests.json',import.meta.url),JSON.stringify(rows,null,2)+'\n');
