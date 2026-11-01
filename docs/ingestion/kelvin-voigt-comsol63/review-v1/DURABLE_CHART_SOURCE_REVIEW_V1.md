# Durable chart regression test — independent source review

The installed isolated app is byte-identical to accepted interface-v8 proposal `8a8f15fc889e5f86c20d885414f61476c4c54121c276db848f714c02f5fdc721`. `tests/test_chart_axis.mjs` reads the actual application by default, with an explicit optional `ATLAS_CHART_APP` override. It extracts the real helper and real chart body, checks original x ranges at both large signed origins, stable y padding, unchanged ordinary spans and inputs, and actual SVG-mock polyline separation. Its independent ordinary-range reference avoids simply duplicating the new tolerance predicate.

The durable chart test and existing supported-package policy mock suite pass independently; command: `node --test tests/test_chart_axis.mjs tests/test_supported_package.mjs` from the isolated release-source. Output: `durable-chart-policy-tests-v1.log`. This executes pure source/mocks, without constructing an engine or invoking compiled code.

The exact Kelvin candidate remains `080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da`; accepted review remains `7dc232c311541aea981981e1efcfc97448509fbc31d9602b9cead4a7890223c4`.

At this source snapshot the policy still lists fourteen ordinary definitions and `verify.yml` does not yet invoke the durable chart test. The coordinator was notified while the remote 37d integration was being prepared. This is not acceptance of the final fifteen-model policy or CI wiring. Final current-source policy/CI bindings, package-v4, database export and actual browser-v3 evidence remain to be examined under new review identities.
