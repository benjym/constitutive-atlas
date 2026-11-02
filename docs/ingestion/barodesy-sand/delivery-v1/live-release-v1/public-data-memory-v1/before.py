"""Scientific channel semantics and public-asset integrity, without HDF5 deps."""
import copy
import hashlib
import io
import zipfile
from unittest.mock import patch
import json
from pathlib import Path
import tempfile
import unittest

from atlas.public_data import OPARA_CHANNELS, load_curated, normalize_opara
from tools.build_experiments import bundle
from tools.ingest_tables import source_series
from tools.ingest_leap import read_leap
from tools.source_downloads import zip_member

ROOT = Path(__file__).resolve().parents[1]


class OparaMappingTests(unittest.TestCase):
    def setUp(self):
        self.channels = {name: [0., 1., 2.] for name in OPARA_CHANNELS}
        self.attributes = {name: {'unit': unit} for name, (_, unit, _) in OPARA_CHANNELS.items()}
        self.channels.update(axial_strain=[0, .01, .005], volumetric_strain=[0, -.002, -.001],
                             pore_water_pressure=[700, 720, 710],
                             effective_axial_stress=[20, 50, 30], effective_radial_stress=[20, 10, 15],
                             # Intentionally distinct rounded/corrected values: do not replace them
                             # with values rederived from the two principal stress channels.
                             deviatoric_stress=[0, 39.999, 14.999], mean_effective_stress=[20, 23.334, 20.001])
        self.inputs = {k: dict(value=v, attributes={'unit': u}) for k, v, u in
                       [('initial_void_ratio', .64, '-'), ('effective_confining_pressure', 20, 'kPa')]}
        self.file_attributes = dict(virtual=False, schema='analysis/triaxial_test/consolidated_undrained')
        self.provenance = dict(test_id='OPARA-TXCU-20')

    def normalize(self):
        return normalize_opara(self.channels, self.attributes, self.inputs,
                               self.file_attributes, self.provenance)

    def test_units_pressure_reference_and_order(self):
        r = self.normalize()
        self.assertEqual(r['initial']['effective_stress'], [20000, 20000, 20000, 0, 0, 0])
        self.assertEqual(r['initial']['void_ratio'], .64)
        self.assertEqual([x['axial_strain'] for x in r['rows']], [0, .01, .005])
        self.assertEqual(r['rows'][1]['volumetric_strain'], -.002)
        self.assertEqual(r['rows'][1]['pore_pressure_absolute'], 720000)
        self.assertEqual(r['rows'][1]['pore_pressure'], 20000)
        self.assertEqual(r['rows'][1]['q'], 39999)
        self.assertEqual(r['rows'][1]['p'], 23334)
        self.assertEqual(r['rows'][1]['axial_displacement'], .001)
        self.assertEqual(r['rows'][1]['cross_sectional_area'], .0001)
        self.assertEqual(r['rows'][1]['volume_change'], .000001)
        self.assertEqual(r['rows'][1]['axial_force'], 1000)
        self.assertIn('source_channel_attributes', r['provenance'])

    def test_unreviewed_units_and_channels_fail_closed(self):
        self.attributes['axial_strain']['unit'] = '%'
        with self.assertRaisesRegex(ValueError, 'unit'):
            self.normalize()
        self.attributes['axial_strain']['unit'] = '-'
        self.channels['unexpected'] = [1, 2, 3]
        with self.assertRaisesRegex(ValueError, 'layout'):
            self.normalize()

    def test_misalignment_nonfinite_simulations_and_reordered_time_rejected(self):
        for change in ['length', 'nan', 'virtual', 'time']:
            with self.subTest(change=change):
                fixture = copy.deepcopy(self.channels)
                if change == 'length': self.channels['deviatoric_stress'] = [1]
                elif change == 'nan': self.channels['axial_strain'][1] = float('nan')
                elif change == 'virtual': self.file_attributes['virtual'] = True
                else: self.channels['time'] = [0, 2, 1]
                with self.assertRaises(ValueError): self.normalize()
                self.channels = fixture
                self.file_attributes['virtual'] = False


class PublicAssetTests(unittest.TestCase):
    def test_geolab_native_observations_and_missingness_are_preserved(self):
        records = [r for r in load_curated(ROOT) if r['provenance']['source_id'] == 'geolab-v2' and r['kind'] == 'experiment']
        self.assertEqual(len(records), 37)
        signatures = set()
        for record in records:
            table = {r[0]: r[1:] for r in record['source_table']['values']}
            self.assertEqual(len(record['rows']), len(record['provenance']['source_rows']))
            self.assertNotIn('effective_stress', record['initial'])
            for row, excel_row in zip(record['rows'], record['provenance']['source_rows']):
                native = table[excel_row]
                self.assertAlmostEqual(row['axial_strain'], float(native[0]) / 100)
                self.assertAlmostEqual(row['q'], float(native[4]) * 1000)
                self.assertNotIn('p', row)
                if 'BASKARP' in record['id'] or native[1] is None:
                    self.assertNotIn('volumetric_strain', row)
                else:
                    self.assertAlmostEqual(row['volumetric_strain'], float(native[1]) / 100)
            signature = hashlib.sha256(json.dumps(record['source_table']['values']).encode()).hexdigest()
            self.assertNotIn(signature, signatures, 'Duplicate GEOLAB history: ' + record['id'])
            signatures.add(signature)

    def test_committed_records_and_public_projection_are_consistent(self):
        records = load_curated(ROOT)
        opara = [r for r in records if r['provenance']['source_id'] == 'opara-sand-fines']
        self.assertEqual(len(opara), 12)
        self.assertEqual(sum(len(r['rows']) for r in opara), 13628)
        for protocol in ['drained-triaxial', 'undrained-triaxial']:
            selected = [r for r in opara if r['protocol'] == protocol]
            self.assertEqual({r['initial']['nominal_confinement'] for r in selected},
                             {20000, 40000, 60000, 100000, 200000, 300000})
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            index = bundle(dest)
            by_id = {r['id']: r for r in records}
            self.assertEqual(set(by_id), {r['id'] for r in index['experiments']})
            for entry in index['experiments']:
                content = (dest / entry['path']).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), entry['sha256'])
                packed = json.loads(content)
                source = by_id[entry['id']]
                self.assertEqual(len(source['rows']), len(packed['values']))
                conversions = {}
                if source['kind'] != 'experiment':
                    originals = {c['key']: c for c in source['columns']}
                    for column in packed['metadata']['columns']:
                        self.assertEqual(column['source_unit'], originals[column['key']]['unit'])
                        if column['unit_status'] == 'standardized':
                            conversions[column['key']] = column['unit_conversion']
                        else:
                            self.assertEqual(column['unit_status'], 'unresolved')
                            self.assertEqual(column['unit'], column['source_unit'])
                            self.assertNotIn('unit_conversion', column)
                for row, values in zip(source['rows'], packed['values']):
                    expected = []
                    for channel in packed['columns']:
                        value = row.get(channel)
                        if value is not None and channel in conversions:
                            transform = conversions[channel]
                            value = value * transform['scale'] + transform['offset']
                        expected.append(value)
                    self.assertEqual(expected, values)
                self.assertEqual(packed['metadata']['provenance']['license'], source['provenance']['license'])
                if source['provenance']['source_id'] == 'opara-sand-fines':
                    self.assertEqual(source['rows'][0]['pore_pressure'], 0)
            before = {p.name: p.read_bytes() for p in dest.iterdir()}
            bundle(dest)
            self.assertEqual(before, {p.name: p.read_bytes() for p in dest.iterdir()})

    def test_geolab_remaining_protocols_and_source_context(self):
        records = load_curated(ROOT)
        geba = [r for r in records if r['id'].startswith('GEOLAB-GEBA-BE-')]
        self.assertEqual(len(geba),5)
        self.assertEqual(sum(len(r['rows']) for r in geba),15)
        self.assertEqual(geba[0]['columns'][1]['unit'],'ms')
        self.assertIn('Basic Properties',geba[0]['provenance']['workbook_context'])
        self.assertEqual(len([r for r in records if r['id'].startswith('GEOLAB-OVP-SIMPLES-CU-')]),6)
        perth = [r for r in records if r['id'].startswith('GEOLAB-PERTH-SIMPLES-CYC-CD-')]
        self.assertEqual(len(perth),3)
        self.assertTrue(all(r['columns'][1]['unit']=='(-)' for r in perth))
        self.assertEqual(len([r for r in records if r['protocol']=='grain-size-distribution']),12)
        direct = [r for r in records if r['id'].startswith('GEOLAB-LOCE-DIRECTS-CU-') and r['kind']=='measurement-series']
        self.assertEqual(len(direct),6)
        self.assertTrue(all(len(r['columns'])==3 for r in direct))
        self.assertTrue(all('c1' not in r['rows'][0] for r in direct))

    def test_castlegate_trigger_blocks_and_summary_are_distinct(self):
        records = [r for r in load_curated(ROOT) if r['provenance']['source_id'] == 'castlegate']
        blocks = [r for r in records if r['kind'] == 'measurement-series']
        self.assertEqual(len(blocks), 68)
        hydro = [r for r in blocks if r['id'].startswith('CASTLEGATE-4AT-HYDRO-')]
        self.assertEqual(len(hydro), 8)
        self.assertEqual(sum(len(r['rows']) for r in hydro), 88377)
        first = next(r for r in hydro if r['id'].endswith('01'))
        self.assertEqual(first['rows'][0]['c1'], 56.061523)
        self.assertEqual(first['rows'][0]['c4'], .21728514)
        self.assertEqual(first['columns'][3]['unit'], 'MPa')
        self.assertEqual(first['provenance']['source_rows'][0], 13)
        self.assertNotIn('q', first['rows'][0])
        summary = next(r for r in records if r['kind'] == 'test-summary')
        self.assertEqual(len(summary['rows']), 33)
        self.assertEqual(summary['source_table']['original_rows'][1][1], '4at42')

    def test_leap_campaigns_preserve_full_histories_and_unlabelled_channels(self):
        records = load_curated(ROOT)
        for source, count in [('leap-2015',36),('leap-2017',26),('leap-2020',66),('leap-2022',54)]:
            selected = [r for r in records if r['provenance']['source_id'] == source]
            self.assertEqual(len(selected),count)
            self.assertTrue(all(r['kind'] != 'experiment' and not r['initial'] for r in selected))
        large = next(r for r in records if r['id']=='LEAP-2020-EO_0_576_PO_100_CSA_0_050')
        self.assertEqual(len(large['rows']),102399)
        self.assertEqual(large['columns'][1]['unit'],'%')
        extra = next(r for r in records if r['id']=='LEAP-2022-EO_0_631_SIGV_40_CSR_0_120_TAU_0_')
        self.assertEqual(len(extra['columns']),9)
        self.assertEqual(extra['columns'][6]['unit'],'not specified')
        self.assertNotIn('c7',extra['rows'][1])
        self.assertIn('c7',extra['rows'][0])
        footer = next(r for r in records if r['id']=='LEAP-2020-EO_0_602_SIGV_40_CSR_0_35')
        self.assertEqual(footer['provenance']['source_footer'][0][:3],[1973,'Phase','Cyclic'])
        self.assertTrue(all('Phase' not in row.values() for row in footer['rows']))

    def test_rockfill_material_identity_and_hurley_population_separation(self):
        records = load_curated(ROOT)
        rock = [r for r in records if r['provenance']['source_id'] == 'rockfills']
        self.assertEqual(len(rock), 33)
        self.assertEqual(sum(len(r['rows']) for r in rock), 158)
        self.assertTrue(all(r['kind'] == 'test-summary' for r in rock))
        # Repeated broad material names retain their distinct original references.
        self.assertEqual(sum('Leached waste rock' in r['material'] for r in rock), 2)
        hurley = [r for r in records if r['provenance']['source_id'] == 'hurley']
        macro = [r for r in hurley if r['kind'] == 'measurement-series']
        populations = [r for r in hurley if r['kind'] == 'test-summary']
        self.assertEqual(len(macro), 3)
        self.assertEqual(sum(len(r['rows']) for r in macro), 20)
        self.assertEqual(len(populations), 22)
        self.assertTrue(all(len(r['columns']) == 59 for r in populations))
        twenty = next(r for r in macro if r['id'] == 'HURLEY-20-MACRO')
        self.assertNotIn('strSampP', [c['name'] for c in twenty['columns']])
        self.assertEqual(twenty['rows'][0]['c1'], 0)
        self.assertTrue(all(not r['initial'] for r in hurley))

    def test_native_collections_cover_specimens_and_independent_curves(self):
        records = load_curated(ROOT)
        finnish = [r for r in records if r['provenance']['source_id'] == 'finnish-oedometer']
        self.assertEqual(len(finnish), 50)
        self.assertEqual(sum(r['id'].startswith('FI-HAARAJOKI-') for r in finnish), 24)
        self.assertEqual(sum(r['id'].startswith('FI-SUURPELTO-') for r in finnish), 26)
        crs = next(r for r in finnish if r['id'] == 'FI-HAARAJOKI-776')
        # Early missing stresses survive as missing, with the measured strain/e.
        self.assertNotIn('c2', crs['rows'][0])
        self.assertEqual(crs['rows'][0]['c1'], .24)
        self.assertEqual(crs['rows'][5]['c2'], 12.6)
        il = next(r for r in finnish if r['id'] == 'FI-HAARAJOKI-1601')
        self.assertEqual(il['source_table']['original_rows'][1][2], '1h')
        self.assertNotIn('c2', il['rows'][0])  # native time text is not elapsed seconds
        hostun = [r for r in records if r['id'].startswith('GEOLAB-HOSTUN-TRIAX-CD')]
        self.assertEqual(len(hostun), 10)
        self.assertTrue(all(len(r['columns']) == 2 for r in hostun))
        self.assertFalse(any(r['id'].endswith('OED-MULT-3') for r in records))
        for r in finnish + hostun:
            self.assertNotIn('q', r['rows'][0])
            self.assertEqual(r['conventions']['stress_unit'], 'per-channel')


class SourceDownloadTests(unittest.TestCase):
    def test_zip_ranges_recover_original_member_and_reject_changed_metadata(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('original.dat', b'1 2 3\n')
        content = stream.getvalue()
        class Response(io.BytesIO):
            status = 206
            def __init__(self, start, end):
                super().__init__(content[start:end+1])
                self.headers = {'Content-Range': f'bytes {start}-{end}/{len(content)}', 'ETag': 'fixture'}
        def request(req, timeout):
            start,end = map(int,req.headers['Range'][6:].split('-'))
            return Response(start,end)
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            crc = archive.getinfo('original.dat').CRC
        file = dict(url='https://data.openei.org/files/4075/fixture.zip',zip_member='original.dat',
                    zip_crc32=crc,size_bytes=6)
        with patch('urllib.request.urlopen',request):
            self.assertEqual(zip_member(file),b'1 2 3\n')
            with self.assertRaisesRegex(ValueError,'metadata'):
                zip_member(dict(file,zip_crc32=0))
        with self.assertRaisesRegex(ValueError,'host'):
            zip_member(dict(file,url='https://example.org/unknown.zip'))


class LeapReaderTests(unittest.TestCase):
    def test_quoted_headers_order_missing_cells_and_source_units(self):
        raw = b'"Cycle","Shear\nStrain","Stress",""\n0.25,1,10,4\n0.125,-1,,\n,,,\n'
        source = dict(id='synthetic',campaign='fixture',source_url='https://example.org',license='ODC-BY-1.0',
                      license_url='https://opendatacommons.org/licenses/by/1-0/',attribution='Synthetic fixture')
        file = dict(filename='fixture.csv',sha256=hashlib.sha256(raw).hexdigest(),source_path='/fixture.csv',
                    delimiter=',',id='LEAP-FIXTURE',protocol='simple-shear',x=2,y=3,
                    headers=['Cycle','Shear\nStrain','Stress',''],units=['cycles','%','kPa','not specified'])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp);(path/'fixture.csv').write_bytes(raw)
            record = read_leap(dict(source,files=[file]),path)[0]
            self.assertEqual(record['rows'],[dict(c1=.25,c2=1,c3=10,c4=4),dict(c1=.125,c2=-1)])
            self.assertEqual(record['columns'][2]['unit'],'kPa')
            self.assertIn('Unlabelled',record['columns'][3]['name'])
            self.assertEqual(record['provenance']['source_rows'],[2,3])
            bad=dict(file,headers=['Cycle','unexpected','Stress',''])
            with self.assertRaisesRegex(ValueError,'headers'):
                read_leap(dict(source,files=[bad]),path)


class SourceSeriesTests(unittest.TestCase):
    def test_independent_coordinates_native_units_and_missingness(self):
        sheet = [[None, 'strain', 'stress', None, 'p', 'q'],
                 [None, '%', 'kPa', None, 'kPa', 'kPa'],
                 [None, 0, 5, None, 100, 0],
                 [None, .5, None, None, 90, 10],
                 [None, 1, 30, None, None, 20]]
        source = dict(id='synthetic', source_url='https://example.org', license='CC0-1.0',
                      license_url='https://creativecommons.org/publicdomain/zero/1.0/', attribution='Synthetic fixture')
        file = dict(filename='synthetic.xlsx', material='Synthetic')
        base = dict(sheet='test', protocol='source-curve', header_rows=[1], units_row=2, data_start=3)
        strain = source_series(source, file, sheet, dict(base, id='A', columns=[2, 3]), archive_sha256='a'*64)
        path = source_series(source, file, sheet, dict(base, id='B', columns=[5, 6]), archive_sha256='a'*64)
        self.assertEqual(strain['rows'][1], {'c2': .5})
        self.assertEqual(path['rows'][1], {'c5': 90, 'c6': 10})
        self.assertEqual(strain['rows'][2]['c3'], 30)  # native kPa, not silently Pa
        self.assertEqual(strain['source_table']['values'][1], [4, .5, None])
        self.assertEqual(strain['columns'][0]['unit'], '%')


if __name__ == '__main__':
    unittest.main()
