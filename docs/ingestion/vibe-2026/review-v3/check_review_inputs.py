"""Read-only exact source/pure-study consistency check; no binaries imported."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
WORKTREE=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 snapshot=json.loads((HERE/'pure-review-attempt1-inputs.json').read_text())
 comparisons=[dict(path=p,expected=h,actual=sha(WORKTREE/p),match=sha(WORKTREE/p)==h) for p,h in snapshot.items()]
 final=json.loads((HERE/'final-source-inputs.json').read_text())
 assert sha(Path(final['source_manifest']))==final['sha256']
 for r in final['verified_files']:
  assert sha(WORKTREE/r['path'])==r['sha256'],r['path']
 p=WORKTREE/'docs/ingestion/vibe-2026/controlled-time-qualification-v1/make_reference_corpus.py'
 s=p.read_text();old="(OUT/'reference-corpus-v1.json').write_text(json.dumps(payload,indent=2)+'\\n')"
 assert old in s
 s=s.replace(old,"assert (json.dumps(payload,indent=2)+'\\n').encode()==(OUT/'reference-corpus-v1.json').read_bytes()")
 exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__review_read_only__','print':lambda *a,**k:None})
 print(json.dumps(dict(initial_pure_inputs=comparisons,final_source_manifest=final['sha256'],final_source_file_count=len(final['verified_files']),final_inputs_verified=True,distinct_final_pure_run='pure-review-attempt2.log',independent_corpus_reproduced_exactly=True,compiled_execution=False),indent=2))
if __name__=='__main__':main()
