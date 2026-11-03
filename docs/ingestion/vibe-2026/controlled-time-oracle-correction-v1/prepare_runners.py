"""Freeze corpus-only runner deltas without importing/evaluating runner modules."""
from pathlib import Path
import hashlib,json,difflib,ast
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OLD='docs/ingestion/vibe-2026/controlled-time-qualification-v1/reference-corpus-v1.json'
NEW='docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/reference-corpus-v2.json'
ORIGINALS=[('native','tests/test_controlled_time_native.py','41f6e074b2ccf99f7b62e5053a25ae88ffb7b92c16f8310f70bed24838446b5d',2),('wasm','tools/test_controlled_time_wasm.mjs','4e033234293dca7f0f000a2aaf26f77dfd835a7d0a27a733227fde5493f8a602',1)]
def prepare(write=False):
 result=[]
 for kind,path,expected,count in ORIGINALS:
  raw=(ROOT/path).read_bytes();assert hashlib.sha256(raw).hexdigest()==expected,path
  text=raw.decode();assert text.count(OLD)==count
  transformed=text.replace(OLD,NEW);assert transformed.replace(NEW,OLD)==text
  if kind=='native':ast.parse(transformed)
  snapshot=HERE/(kind+'-runner-v2.source.txt');diff=''.join(difflib.unified_diff(text.splitlines(True),transformed.splitlines(True),fromfile=path,tofile=kind+'-runner-v2.source.txt'))
  if write:
   with snapshot.open('x') as f:f.write(transformed)
   with (HERE/(kind+'-corpus-only.diff')).open('x') as f:f.write(diff)
  else:assert snapshot.read_bytes()==transformed.encode()
  result.append(dict(kind=kind,original_path=path,original_sha256=expected,old_corpus_path=OLD,new_corpus_path=NEW,literal_occurrences=count,snapshot=snapshot.name,snapshot_sha256=hashlib.sha256(transformed.encode()).hexdigest(),only_change='single logical corpus location (native receipt+reader, Wasm receipt+reader shared variable)',reverse_replacement_byte_identity=True))
 return dict(status='pass-source-only',compiled_calls=0,module_evaluations=0,corpus_sha256=hashlib.sha256((ROOT/NEW).read_bytes()).hexdigest(),runners=result)
if __name__=='__main__':
 import sys
 write='--write' in sys.argv;report=prepare(write)
 if write:
  with (HERE/'runner-delta-proof.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
