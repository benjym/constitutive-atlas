"""Static source extraction for pinned torsion workbooks; never executes VBA.

Restricted to named modules in the reviewed release. Module source offsets come
from the compressed VBA directory; this is not a scan for executable content.
MS-OVBA compression: https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-ovba/4742b896-b32b-4eb0-8372-fbf01e3c65fd
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'paper/results/dependencies'))
from xlrd.compdoc import CompDoc


def decompress(data):
    if not data or data[0] != 1:
        raise ValueError('Invalid compressed-container signature')
    pos = 1
    output = bytearray()
    while pos < len(data):
        start = pos
        header = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        end = start + (header & 0xFFF) + 3
        if ((header >> 12) & 7) != 3 or end > len(data):
            raise ValueError('Invalid compressed-chunk header or extent')
        chunk_start = len(output)
        if not header & 0x8000:
            if end - pos != 4096:
                raise ValueError('Invalid raw chunk size')
            output.extend(data[pos:end])
            pos = end
            continue
        while pos < end:
            flags = data[pos]
            pos += 1
            for bit in range(8):
                if pos == end:
                    break
                if flags & (1 << bit):
                    if pos + 2 > end:
                        raise ValueError('Truncated copy token')
                    token = struct.unpack_from('<H', data, pos)[0]
                    pos += 2
                    offset_bits = max(4, (len(output) - chunk_start - 1).bit_length())
                    length_bits = 16 - offset_bits
                    length = (token & ((1 << length_bits) - 1)) + 3
                    offset = (token >> length_bits) + 1
                    if offset > len(output) - chunk_start:
                        raise ValueError('Copy starts before this chunk')
                    for _ in range(length):
                        output.append(output[-offset])
                else:
                    output.append(data[pos])
                    pos += 1
                if len(output) - chunk_start > 4096:
                    raise ValueError('Decompressed chunk exceeds4096bytes')
    return bytes(output)


def main():
    inventory_path = ROOT / 'paper/study/ottawa_cyclic_inventory.json'
    inventory_bytes = inventory_path.read_bytes()
    records = [r for r in json.loads(inventory_bytes)['records']
               if r['protocol'] == 'cyclic-torsional-shear-source']
    output_dir = ROOT / 'paper/results/sources/torsion-vba'
    output_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for r in records:
        path = ROOT / 'tmp/dataset-survey' / r['source_file']
        source_bytes = path.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != r['source_file_sha256']:
            raise ValueError('Source hash mismatch')
        compound = CompDoc(source_bytes)
        prefix = '_VBA_PROJECT_CUR/VBA/'
        directory = decompress(compound.get_named_stream(prefix + 'dir'))
        codepages = [struct.unpack('<H', m.group(1))[0] for m in re.finditer(
            rb'\x03\x00\x02\x00\x00\x00(..)', directory, re.DOTALL)]
        if codepages != [932]:
            raise ValueError('Expected the reviewed project codepage932')
        module_starts = list(re.finditer(
            rb'\x19\x00[\x01-\x40]\x00\x00\x00(?:Sheet[1-4]|ThisWorkbook)', directory))
        if len(module_starts) != 5:
            raise ValueError('Expected five known modules in the reviewed release')
        modules = []
        for idx, match in enumerate(module_starts):
            end = module_starts[idx + 1].start() if idx + 1 < len(module_starts) else len(directory)
            block = directory[match.start():end]
            name_size = struct.unpack_from('<I', block, 2)[0]
            name = block[6:6 + name_size].decode('ascii')
            offsets = list(re.finditer(rb'\x31\x00\x04\x00\x00\x00(.{4})', block, re.DOTALL))
            if len(offsets) != 1:
                raise ValueError('Ambiguous or missing MODULEOFFSET')
            offset = struct.unpack('<I', offsets[0].group(1))[0]
            stream = compound.get_named_stream(prefix + name)
            raw_source = decompress(stream[offset:])
            source = raw_source.decode('cp932')
            if f'Attribute VB_Name = "{name}"' not in source:
                raise ValueError('Decompressed source has unexpected module name')
            dest = output_dir / (r['id'] + '-' + name + '.bas')
            dest.write_bytes(raw_source)
            modules.append({'module': name, 'stream': prefix + name,
                            'source_offset': offset, 'source_encoding': 'cp932',
                            'source_sha256': hashlib.sha256(raw_source).hexdigest(),
                            'local_copy': str(dest.relative_to(ROOT))})
        if hashlib.sha256(path.read_bytes()).hexdigest() != r['source_file_sha256']:
            raise ValueError('Source changed during inspection')
        result.append({'curated_loading_id': r['id'], 'source_file': r['source_file'],
                       'source_file_sha256': r['source_file_sha256'], 'modules': modules})
    if inventory_path.read_bytes() != inventory_bytes:
        raise ValueError('Inventory changed during read')
    report = {'paper_record_version': 1, 'date': '2026-10-31',
              'status': 'static_vba_source_extraction_no_execution',
              'scope': 'Five named VBA modules per pinned workbook. No macros, '
                       'Office application, workbook recalculation or response evaluation run. '
                       'Compiled VBA cache is not interpreted; extracted source alone '
                       'does not prove agreement with cached/compiled behaviour.',
              'inputs_sha256': {
                  'paper/study/ottawa_cyclic_inventory.json': hashlib.sha256(inventory_bytes).hexdigest(),
                  'paper/scripts/read_torsion_vba.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              'specimens': result}
    (ROOT / 'paper/study/torsion_vba_source_inventory.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print('Statically extracted', sum(len(r['modules']) for r in result), 'source modules.')


if __name__ == '__main__':
    main()
