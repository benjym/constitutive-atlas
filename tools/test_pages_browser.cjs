// Smoke-test the package as served under a GitHub Pages project path.
const assert = require('node:assert/strict');
const {createServer} = require('node:http');
const {createReadStream} = require('node:fs');
const {stat, readFile} = require('node:fs/promises');
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
    const recorded = [
      ['extended-mohr-coulomb-2013-exact-generalized-work-be-exact-domain-v3', 3,
        'extended-mohr-coulomb-2013/certified-public-backend-v1/recorded-wasm.json'],
      ['clay2014-trace-calibrated-igs-fixed-plane-v1', 33,
        'hypoplastic-clay-2014/delivery-20261111/generic-boundary-v1/radius-bounded-v2/production/reversal-v4/strain-wasm/synthetic-NCL-H0--mixed-six-components.json'],
    ];
    for (const [id, count, reference] of recorded) {
      await page.setViewportSize({width: 1280, height: 900});
      await page.goto(url + '#catalogue/' + id);
      await page.locator('#catalogue-explore').click();
      const done = () => page.getByText('Response up to date · ' + count + ' ordered observations.', {exact: true}).waitFor();
      await done();
      const downloading = page.waitForEvent('download');
      await page.getByRole('button', {name: 'Reproducible run'}).click();
      const downloaded = await (await downloading).path();
      const replay = JSON.parse(await readFile(downloaded, 'utf8'));
      const expected = JSON.parse(await readFile(resolve(__dirname, '../docs/ingestion', reference), 'utf8'));
      assert.deepEqual(replay.result, expected);
      assert.ok(await page.locator('#recorded-lab-parameters input[readonly]').count() > 0);
      await page.getByRole('button', {name: 'Return to standard laboratory'}).click();
      await page.locator('#run-file').setInputFiles(downloaded);
      await done();
      await page.setViewportSize({width: 390, height: 844});
      await page.reload();
      await done();
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth), false);
      await page.getByRole('img', {name: 'Recorded deviator stress versus mean stress'}).waitFor();
    }
    assert.deepEqual(errors, []);
    console.log('Packaged laboratory, Cam Clay comparison, database links and both fixed recorded model replays passed.');
  } finally {
    try { await browser?.close(); }
    finally { await new Promise(ok => server.close(ok)); }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
