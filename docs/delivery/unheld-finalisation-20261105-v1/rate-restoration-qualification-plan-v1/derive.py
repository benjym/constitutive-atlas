"""Source-only plan derivation. No compiler, generated execution or numerical run."""
from pathlib import Path
import hashlib,json
R=Path('/Users/bmar5496/code/constitutive-atlas');N=R/'docs/delivery/unheld-finalisation-20261105-v1';O=N/'rate-restoration-qualification-plan-v1';OLD=R/'docs/delivery/unheld-finalisation-20261102-v1/baseline-qualification-plan-v5';V=N/'current16-qualification-plan-v1';M=R/'docs/ingestion/manzari-dafalias-1997/delivery-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(v):return json.dumps(v,indent=2)+'\n'
def emit(n,s):(O/n).write_text(s)
def pin(p):return{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
emit('GATES.json',js({'identity':'rate-restoration-fresh-build-qualification-policy-v1','author_run':'/root/publication_operations_review','frozen_before_implementation':True,'solver_expected':'0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc','source_checkout':'/private/tmp/atlas-baseline-delivery-20261105/source','qualification':['fresh native+Wasm builds only, explicit atlas_solver parallel1, no reuse640 executable acceptance','original v5 collector/policy/wasm-cli/reference oracles unchanged, original701/42/87 and pair','strict17membership/generated JSON/header and fiveoriginal model bytes','exact original failed editedIGS101 controls/settings; newNative versus prior702native and newWasm versus702browser original1e-10 physical/exact-other comparator; catalogue key transition only','MD exactlive640drained/undrained specs; newWasm results exactly live640Wasm exceptelapsed; native/Wasm original1e-10 physical/exact-other comparator','samebackend fresh replay exactexceptelapsed for all3 supplementalrequests','all failures retained, no gate/settings changes; parent serial observer1800/mandatoryreap'],'prior640qualification':'historical separate, does not qualify solverB newbuilds','no_actual_execution':True}))
rows=[{'id':'igs97-edited-initial','document':pin(R/'output/playwright/baseline-five-current17-20261105-v1/hypoplastic-sand-igs97-initial.json'),'native_reference':pin(N/'current17-igs97-native-replay-v2/prior702.stdout'),'wasm_reference':pin(N/'live-release702-browser-v1/hypoplastic-sand-igs97-initial.json'),'comparison':'original-browser-physical-parity' }]
for kind in('drained','undrained'):
 p=M/'final-live-v1'/('live-640-'+kind+'.json');rows.append({'id':'md1997-'+kind,'document':pin(p),'wasm_reference':pin(p),'comparison':'wasm-exact-exceptelapsed'})
for row in rows:
 doc=json.loads(Path(row['document']['path']).read_text());row['specification']=doc['specification'];assert len(row['specification']['loading']['controls_bits'])==101
emit('requests.json',js(rows))
external=[pin(OLD/n)for n in('collector.py','policy.json','wasm-cli.mjs')]+[pin(V/'build.py'),pin(N/'nine-example-refresh-plan-v1/collector-core.mjs'),pin(N/'nine-example-refresh-plan-v1/policy.json'),pin(N/'nine-example-refresh-plan-v1/context/web/laboratory-scope.mjs'),pin(M/'ensemble-ci-fix-v1/test_ensemble.mjs'),pin(N/'current17-browser-plan-v1/catalogue17.json')]
for row in rows:
 external +=[row[k]for k in('document','native_reference','wasm_reference')if k in row]
# Scope helpers' transitive modules are part of the original frozen source plan.
context=N/'nine-example-refresh-plan-v1/context/web'
external +=[pin(p)for p in sorted(context.glob('*.mjs'))]
external.append(pin(N/'rate-control-regression-test-plan-v1/proposed/tests/test_solver.cpp'))
external.append(pin(N/'rate-restoration-cache-copy-v1.json'))
external.append(pin(N/'shared-current17-review-v1/rate-regression-test-source-v1/decision.json'))
external.append(pin(N/'shared-current17-review-v1/rate-restoration-source-v1/decision.json'))
external.append(pin(M/'ensemble-ci-fix-v1/decision.json'))
observer=R/'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py';external.append(pin(observer));emit('external-pins.json',js(external))
s=(V/'build.py').read_text();s=s.replace("PLAN=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261102-v1/baseline-qualification-plan-v5')","PLAN=HERE")
s=s.replace("a.add_argument('--slot-handoff',required=True);args=a.parse_args()", "a.add_argument('--slot-handoff',required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--plan-manifest-sha256',required=True);args=a.parse_args();m.verify_plan(args.plan_manifest_sha256)")
s=s.replace("out=HERE/'actual-build-v1'", "out=args.output.resolve()")
s=s.replace(" def bound():\n", " def bound():\n  m.verify_plan(args.plan_manifest_sha256);m.verify(receipt['execution_script']);m.assert_source(repo)\n")
s=s.replace("bound();assert (work/'em-cache').is_dir()","bound();m.verify_cache(work/'em-cache');assert (work/'em-cache').is_dir()")
emit('build.py',s)
emit('plan.json',js({'identity':'rate-restoration-original-qualification-plan-v1','source':'/private/tmp/atlas-baseline-delivery-20261105/source','actual':'/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/rate-restoration-qualification-actual-v1','work':'/private/tmp/atlas-baseline-delivery-20261105/rate-control-build-v1','original_collector':str(OLD/'collector.py'),'original_policy_sha256':sha(OLD/'policy.json'),'original_cli_sha256':sha(OLD/'wasm-cli.mjs'),'observer':pin(observer),'phases':['source-freeze','build','freeze','native','wasm','pair','extra-native','extra-wasm','extra-pair'],'slot_handoff':'unheld-baseline-five-native-then-wasm-v1','fresh_build_required':True,'compiled_observations':False,'parent_only_execution':True}))
print('prospective source derivation complete')
