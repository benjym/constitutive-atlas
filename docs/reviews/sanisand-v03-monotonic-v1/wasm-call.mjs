// Read requests from a file. Await writes; never process.exit with buffered output.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [artifact, requestPath] = process.argv.slice(2);
const request = JSON.parse(fs.readFileSync(requestPath, 'utf8'));
const {default:createAtlas} = await import(pathToFileURL(artifact).href);
const engine = await createAtlas();
const response = engine.ccall(request.function, 'string', request.types, request.args);
await new Promise((resolve, reject) => process.stdout.write(response + '\n', error => error ? reject(error) : resolve()));
