#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAW = ROOT / "law_functions"
WRAPPERS = ROOT / "grafana_wrappers"

DEF_RE = re.compile(r"\blet\s+(fn_[A-Za-z0-9_]+)\s*=\s*\(")
CALL_RE = re.compile(r"\b(fn_[A-Za-z0-9_]+)\s*\(")

REQUIRED_HELPERS = {
    "fn_mon_status_to_color",
    "fn_mon_alert_from_job_success",
    "fn_mon_alert_from_pipeline_success",
    "fn_mon_global_from_color_set",
    "fn_prd_ada_alert_from_tables_lag",
}

REQUIRED_DOMAINS = {
    "fn_prd_ada_dom_dispatch_status",
    "fn_prd_ada_dom_drillit_status",
    "fn_prd_ada_dom_blockgrade_status",
    "fn_prd_ada_dom_pi_status",
    "fn_prd_ada_dom_plans_status",
    "fn_prd_ada_dom_meteodata_status",
    "fn_prd_ada_dom_alarm_status",
    "fn_prd_ada_dom_front_status",
    "fn_prd_ada_dom_kpi_status",
    "fn_prd_ada_dom_global_status",
}

REQUIRED_WRAPPERS = {
    "var_mlp_ada_global.kql",
    "var_mlp_ada_dispatch.kql",
    "var_mlp_ada_drillit.kql",
    "var_mlp_ada_pi.kql",
    "var_mlp_ada_plans.kql",
    "var_mlp_ada_blockgrade.kql",
    "var_mlp_ada_meteodata.kql",
    "var_mlp_ada_kpi.kql",
    "var_mlp_ada_alarm.kql",
    "var_mlp_ada_front.kql",
}

law_files = sorted(LAW.rglob("*.kql"))
wrapper_files = sorted(WRAPPERS.glob("*.kql"))
all_files = law_files + wrapper_files

func_defs = {}
def_count = {}
for path in law_files:
    text = path.read_text(encoding="utf-8")
    for m in DEF_RE.finditer(text):
        name = m.group(1)
        def_count[name] = def_count.get(name, 0) + 1
        func_defs[name] = path

errors = []

# Duplicate definitions
for name, count in sorted(def_count.items()):
    if count > 1:
        errors.append(f"Duplicate function definition: {name} appears {count} times")

# Missing required wrappers
wrapper_names = {p.name for p in wrapper_files}
for req in sorted(REQUIRED_WRAPPERS - wrapper_names):
    errors.append(f"Missing required wrapper: {req}")

# Missing required helper/domain functions
for req in sorted((REQUIRED_HELPERS | REQUIRED_DOMAINS) - set(func_defs)):
    errors.append(f"Missing required function definition: {req}")

# Undefined references
for path in all_files:
    text = path.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    for call in calls:
        if call not in func_defs:
            errors.append(f"Undefined call: {call} referenced in {path.relative_to(ROOT)}")

# Ensure wrappers call exactly one function and it's a required domain function
for path in wrapper_files:
    text = path.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    if len(calls) != 1:
        errors.append(f"Wrapper must call exactly one function: {path.name} has {calls}")
    else:
        fn = calls[0]
        if fn not in REQUIRED_DOMAINS:
            errors.append(f"Wrapper {path.name} points to non-domain function: {fn}")

# Ensure global depends only on domain functions + cross helper
global_file = ROOT / "law_functions/domains/fn_prd_ada_dom_global_status.kql"
if global_file.exists():
    text = global_file.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    allowed = set(REQUIRED_DOMAINS) | {"fn_mon_global_from_color_set", "fn_prd_ada_dom_global_status"}
    unexpected = [c for c in calls if c not in allowed]
    if unexpected:
        errors.append(f"Global function has unexpected dependencies: {unexpected}")

if errors:
    print("KQL package audit FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print("KQL package audit OK")
print(f"Defined functions: {len(func_defs)}")
print(f"Checked files: {len(all_files)}")
print("Required wrappers: OK")
print("Required helpers/domains: OK")
