// Smoke-test the package as served under a GitHub Pages project path.
const assert = require('node:assert/strict');
const {createServer} = require('node:http');
const {createReadStream} = require('node:fs');
const {stat} = require('node:fs/promises');
const {extname, resolve, sep} = require('node:path');
const {chromium} = require('playwright');

const root = resolve(process.argv[2] || 'web/dist');
const prefix = '/constitutive-atlas/';
const mime = {'.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.wasm': 'application/wasm'};
const server = createServer(async (req, res) => {
  try {
    const path = new URL(req.url, 'http://localhost').pathname;
    assert.ok(path.startsWith(prefix));
    const file = resolve(root, decodeURIComponent(path.slice(prefix.length)) || 'index.html');
    assert.ok(file.startsWith(root + sep));
    const info = await stat(file);
    assert.ok(info.isFile());
    res.writeHead(200, {'Content-Type': mime[extname(file)] || 'application/octet-stream',
      'Content-Length': info.size});
    if (req.method === 'HEAD') res.end();
    else createReadStream(file).pipe(res);
  } catch {
    res.writeHead(404).end();
  }
});

async function main() {
  await new Promise((ok, fail) => server.listen(0, '127.0.0.1', ok).once('error', fail));
  const url = 'http://127.0.0.1:' + server.address().port + prefix;
  let browser;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url + '#laboratory');
    await page.locator('#laboratory').waitFor({state: 'visible'});
    await page.waitForFunction(() => document.querySelector('#model').options.length > 0);
    await page.goto(url + '#experiment?preset=clay');
    try {
      await page.waitForFunction(() => document.querySelector('#guided-status').textContent === 'Both curves updated.');
    } catch (error) {
      throw new Error('Cam Clay comparison: ' + await page.locator('#guided-status').innerText(), {cause: error});
    }
    assert.match(await page.locator('#guided-values').innerText(), /Reference at .*Comparison at /s);
    for (const path of ['atlas.sqlite', 'atlas-database.json']) {
      const link = page.locator('a[href="' + path + '"]').first();
      const href = await link.getAttribute('href');
      const response = await page.request.head(new URL(href, url).href);
      assert.equal(response.status(), 200, path);
      assert.ok(Number(response.headers()['content-length']) > 0, path);
    }
    assert.deepEqual(errors, []);
    console.log('Packaged laboratory, Cam Clay comparison and database links passed.');
  } finally {
    try { await browser?.close(); }
    finally { await new Promise(ok => server.close(ok)); }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
