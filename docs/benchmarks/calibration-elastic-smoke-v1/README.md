# Recorded calibration: three-candidate native elasticity check

Task CAL-recorded-runner-v1, 1 November 2026. The reusable
[recorded calibration runner](../../CALIBRATION_RECORDED.md) passes a bounded
end-to-end analytical check with the existing native executable. No compilation,
real-data fit, experimental validation or scientific admission occurred.

The [prospective protocol](evidence/protocol.json) froze the candidate budget,
expected parameter sequence and acceptance bounds before any native process.
One metadata call and exactly three serial recorded material calls ran. Their
Young moduli were 20, 10 and 30 MPa; the driver selected the analytical 30 MPa.
The existing synthetic fixture includes six observations, reversal, nonzero strain
origin and a duplicated observation. It is independent isotropic-elasticity
arithmetic, not an experimental specimen or evidence for the other eight laws.

| Quantity | Observed | Frozen upper bound |
| --- | --- | --- |
| Best complete objective | 5.190430076058726e-31 | 1e-12 |
| Maximum selected q error | 4.3655745685100555e-11 Pa | 0.002 Pa |
| Maximum selected volumetric strain error | 8.673617379884035e-19 | 2e-10 |

[Assessment](evidence/assessment.json), [complete search result](evidence/run/result.json),
[preparation/configuration freeze](evidence/run/freeze.json) and every candidate's
request, response and assessment are retained under `evidence/`.
The [saved-only verifier](verify.py) checks all evidence hashes, allocation and
reservation bytes, native descriptor, parameter/preparation/request identities,
then reconstructs predictions from saved stresses/strains and replays the entire
three-candidate search and objective exactly. It neither reads nor invokes the
native executable. Source hashes are checked against the currently frozen files;
future source revisions need their exact preserved bytes for this audit.

The executable SHA-256 is
`960d6f8ebcc0c3296555dd6e294a3650a5ec2318108d30850216ee5a69e4f574`,
from the [traceable build receipt](../current-source-build-v1/README.md), source
commit `6ff25a9fb01de0fa9360c1bd04149877490319ef`. Its compiled nine-model catalogue
matches the frozen descriptor. This is reuse of that identified build, not a claim
that today's entire checkout was rebuilt. The unchanged baseline elastic definition
is retained in its existing version; no new legacy model record was authored.

Eight synthetic runner test groups and the 41 search/objective/metric/allocation
tests pass (49 total). They include distinct initial void ratios for two whole
tests, exact candidate preparation resets, failed-prefix retention, corrupted
identity/order/completion/control responses, descriptor mismatch, transport errors,
and receipt-write failure stopping before another candidate. No native calls are
made by these unit tests. The generic API's explicit limits remain: fixed drained
preparation, no fitted initialization, no raw material-process command/stdout/stderr
receipt, no original input-file provenance reconstruction or certified crash/resume.
See the [API contract](../../CALIBRATION_RECORDED.md) before a production study.

Audit saved evidence only:

```sh
python3 -B docs/benchmarks/calibration-elastic-smoke-v1/verify.py
```

An intentional repeat requires an existing byte-identical executable/catalogue
and a new output directory; this command executes exactly three native candidates
and does not build:

```sh
python3 -B docs/benchmarks/calibration-elastic-smoke-v1/reproduce.py \
  --solver /path/to/atlas_solver --catalogue /path/to/generated/models.json \
  --output /private/tmp/new-elastic-calibration-smoke
```

This closes the software connection slice. Prospective calibration allocations,
parameter/preparation/source decisions and independent scientific review remain
open. The completed KFS campaign and all historical scores remain unchanged.
