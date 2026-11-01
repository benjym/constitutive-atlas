"""Generate a review-only diff against the frozen published workflow."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import difflib,hashlib,json
D=Path(__file__).resolve().parent
original=(D/'published-37d/.github/workflows/verify.yml').read_text()
start=original.index('      - name: Native checks and full exact archival replay\n')
end=original.index('      - name: Linux portable Python suite\n',start)
old=original[start:end]
new='''      - name: Retain strict original and MD legacy failures and reject unknown fixtures
        run: python -B tools/check_native_fixture_dispatch.py check --catalogue build/generated/models.json --source-root . --build build --output "$RUNNER_TEMP/native-ci-dispatch/contracts.json"
      - name: Native checks and full exact archival replay
        if: runner.os == 'macOS'
        run: |
          python -B tools/check_native_fixture_dispatch.py ctest --catalogue build/generated/models.json --source-root . --build build --suite macos-main --output "$RUNNER_TEMP/native-ci-dispatch/macos-main.json"
          python -B tools/check_native_fixture_dispatch.py ctest --catalogue build/generated/models.json --source-root . --build build --suite recorded --output "$RUNNER_TEMP/native-ci-dispatch/macos-recorded.json"
      - name: Linux native checks
        if: runner.os == 'Linux'
        run: |
          python -B tools/check_native_fixture_dispatch.py ctest --catalogue build/generated/models.json --source-root . --build build --suite linux-main --output "$RUNNER_TEMP/native-ci-dispatch/linux-main.json"
          python -B tools/check_native_fixture_dispatch.py ctest --catalogue build/generated/models.json --source-root . --build build --suite recorded --output "$RUNNER_TEMP/native-ci-dispatch/linux-recorded.json"
      - name: Retain native dispatch process evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: native-ci-dispatch-${{ matrix.os }}
          path: ${{ runner.temp }}/native-ci-dispatch/
'''
proposed=original[:start]+new+original[end:]
diff=''.join(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile='a/.github/workflows/verify.yml',tofile='b/.github/workflows/verify.yml'))
(D/'workflow-proposal.diff').write_text(diff)
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
(D/'workflow-diff-proof.json').write_text(json.dumps({'identity':'published37d-native-dispatch-workflow-proposal-v2','published_sha256':sha(original),'proposed_sha256':sha(proposed),'replaced_original_block':old,'proposed_block':new,'prefix_sha256':sha(original[:start]),'suffix_sha256':sha(original[end:]),'outside_block_unchanged':True,'roundtrip_replace_recovers_original':proposed.replace(new,old,1)==original,'main_filters':{'macos-main':'^atlas_recorded$','linux-main':'^(atlas_python|atlas_recorded)$'},'recorded_filter':'^atlas_recorded$','all_non_native_workflow_gates_unchanged':True},indent=2)+'\n')
