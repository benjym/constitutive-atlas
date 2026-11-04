Prospective coordinator-only final Pages artifact/production verifier. No finalrevision ishardcoded. No actualarchive/API/HTTP/browser/compiled work hasoccurred; E8remainspending.

Run after actualsuccessfulfinaldeployment with exportedghAPI JSON (oneworkflowrun object, onegithub-pagesartifact object, onedeploymentobject, onesuccessdeploymentstatusobject) anddownloadedZIP:

```sh
python3 -B verify.py --revision FINAL40SHA --pages-run pages-run.json --artifact-metadata artifact.json --deployment deployment.json --deployment-status deployment-status.json --zip artifact.zip --base-url https://benjym.github.io/constitutive-atlas/ --output NEW_OWNED_OUTPUT
```

Verifier streams soleartifact.tar fromZIP; no1GB extractioncopy. It hashesall1549 members, rejectsduplicates/traversal/nonregularmembers andrequires reviewedmembership exactly. SemanticJSON capture max16MiB/file. Checks catalogue exact16/current hash,5model/definition/review+approval30 bytes,9namedenvelopes andindex identities,all15engine-rolepresence,allretainedidentityrelease_revision stamps equalrequiredrevision. SelectedproductionHTTP (5defs/reviews/recorddefs+registry+9examples+metadata/index+ordinaryJS/Wasm+stampidentities) streams comparedexactto actualartifact; headers/rawhashes retained. APIartifactdigest anddownloadZIPsha recordedseparately: APIcontentdigest isnotassumed identicalto ZIPtransportdigest. Noequivalence toprior localordinaryWasm binary isassumed; currentexactmodels and productionartifact identity providebinding.

Sourcecheck: `python3 -B check.py`5manufacturedarchive witnessesPASS, noactualinputs/network. Temporaryfixturetreesremoved. Existingacceptedlocalpackageinventory4fb3f1e suppliesmembernamespace; fullpackagechecks/source/CI/browserremainseparate. Final FastCI/FullCI/Pages anddeployment must allbegenuine; thisscriptvalidatesPagesmetadata only. Exactactualresultandindependent E8review stillrequired. Stoponanyfailure,preserveterminal/rawpacket; noautomaticretry/relaxation.

Parent58Pagesactivationfailure remainsoriginalevidence; no timeout/gatechange. Currentfinalrevision maychangeafterretainedharnessfailures; passactualfinalsha explicitly.
