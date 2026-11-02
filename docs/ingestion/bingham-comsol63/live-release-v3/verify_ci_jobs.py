"""Require the current full six-job workflow and separate controlled-path run."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = "43ea5c45f0e6112661fe996b685a3adcdac12ce6"
RUN = 41388826742
CONTROLLED = 41388826735
REPO = "repos/benjym/constitutive-atlas/"

def api(path):
    return json.loads(subprocess.check_output(["gh", "api", REPO + path]))

run = api(f"actions/runs/{RUN}")
jobs = api(f"actions/runs/{RUN}/jobs?per_page=100")
controlled = api(f"actions/runs/{CONTROLLED}")
for name, value in (("CI-GATE-RUN.json", run), ("CI-GATE-JOBS.json", jobs),
                    ("CI-GATE-CONTROLLED.json", controlled)):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")
expected = {"native (ubuntu-latest, 3.12)", "native (macos-26, 3.14)",
            "wasm", "wasm-linux", "controlled-path", "deploy"}
checks = {
    "current_full_source": run["head_sha"] == HEAD,
    "current_controlled_source": controlled["head_sha"] == HEAD,
    "main_push": run["event"] == "push" and run["head_branch"] == "main",
    "full_run_success": run["status"] == "completed" and run["conclusion"] == "success",
    "all_six_jobs_present": jobs["total_count"] == 6 and len(jobs["jobs"]) == 6
        and {j["name"] for j in jobs["jobs"]} == expected,
    "every_job_terminal_success": all(j["status"] == "completed" and
        j["conclusion"] == "success" for j in jobs["jobs"]),
    "separate_controlled_success": controlled["status"] == "completed"
        and controlled["conclusion"] == "success",
}
out = {"passed": all(checks.values()), "source_revision": HEAD, "run_id": RUN,
       "checks": checks, "no_remote_mutation_or_material_execution": True}
(HERE / "ALL-JOBS-CHECK.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out))
raise SystemExit(0 if out["passed"] else 1)
