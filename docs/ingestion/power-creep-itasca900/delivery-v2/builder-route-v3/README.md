# Approved power-creep standard website integration v3

The uploaded artifact for commit51a9ef72538129ef16e0f14e6d81ea00215a1fb1 from run41291357415 lacked power-creep.html, power-creep-package.json and engine/. The original upload remains /private/tmp/power-creep-pages-51a9ef72/artifact.tar. This is retained as a release failure, despite its passing earlier Wasm job. The concurrent f51113bd standard-builder retirement caused the omission. Prior working-copy full-builder observations were insufficient committed-release proof.

This separately planned correction restores the approved bundle and unchanged analytical gate, plus explicit safe public timed routes and mandatory packaged-route presence checking. No model/solver/parameter/tolerance change. Independent review accepted all eight exact source candidates; see review/.

The isolated committed-source build command was:

    GITHUB_SHA=builder-route-v3 python3 -B /private/tmp/power-creep-release-51a9ef72/tools/build_web.py --wasm-dir /private/tmp/atlas-power-creep-site-wasm --power-creep-wasm-dir /private/tmp/atlas-power-creep-site-engine --output /private/tmp/power-creep-route-v3-site

standard-build.log records unchanged analytical creep/relaxation success and complete package. supported-package.json passes the existing twelve ordinary-model supported cases, with mandatory timed-page presence. Node fixtures11/11, existing power contract3/3 and saved recorded checks4/4 pass. Browser proof navigates the main catalogue card, accepted details and Test this model button to power-creep.html, automatically completes10s relaxation, exposes full state/engine identity and records no error/warning console messages. The exact model definition remains67f3fabd6aecfda19b977bf3baeae2dce45f9081fa81a4436a750a41825a4bef. Actual uploaded/live release verification remains open until recorded separately.
