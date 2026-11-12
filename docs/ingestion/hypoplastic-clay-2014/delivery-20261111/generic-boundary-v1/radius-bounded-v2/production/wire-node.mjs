import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {join,resolve} from 'node:path';

const [launcher,fixtures,out,match] = process.argv.slice(2);
const cases = JSON.parse(await readFile(fixtures, 'utf8'));
const create = (await import(pathToFileURL(resolve(launcher)))).default;
const atlas = await create();
await mkdir(out);
for (const row of cases) {
  if (match && !row.id.includes(match)) continue;
  const result = atlas.ccall('atlas_replay_recorded_scope', 'string', Array(9).fill('string'), row.args);
  JSON.parse(result);
  await writeFile(join(out,row.id+'.json'), result+'\n', {flag:'wx'});
  console.log(row.id, JSON.parse(result).ok);
}
