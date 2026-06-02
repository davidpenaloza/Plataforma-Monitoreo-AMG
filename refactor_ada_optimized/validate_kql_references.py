#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAW = ROOT / "law_functions"
BODY = ROOT / "law_functions_body_only"
WRAPPERS = ROOT / "grafana_wrappers"
AMBIENTE = "prd"
FAENA = "mlp"
LAW_SCOPE = LAW / AMBIENTE / FAENA
BODY_SCOPE = BODY / AMBIENTE / FAENA

DEF_RE = re.compile(r"\blet\s+(fn_[A-Za-z0-9_]+)\s*=\s*\(")
CALL_RE = re.compile(r"\b(fn_[A-Za-z0-9_]+)\s*\(")
CONFLICT_RE = re.compile(r"^(<<<<<<< .+|=======|>>>>>>> .+)$", re.M)

REQUIRED_HELPERS = {
    "fn_mon_status_to_color",
    "fn_prd_mlp_ada_lag_helpers",
}

REQUIRED_DOMAINS = {
    "fn_prd_mlp_ada_dom_dispatch_status",
    "fn_prd_mlp_ada_dom_drillit_status",
    "fn_prd_mlp_ada_dom_blockgrade_status",
    "fn_prd_mlp_ada_dom_pi_status",
    "fn_prd_mlp_ada_dom_plans_status",
    "fn_prd_mlp_ada_dom_meteodata_status",
    "fn_prd_mlp_ada_dom_alarm_status",
    "fn_prd_mlp_ada_dom_front_status",
    "fn_prd_mlp_ada_dom_kpi_status",
    "fn_prd_mlp_ada_dom_optimizador_status",
    "fn_prd_mlp_ada_dom_settings_status",
    "fn_prd_mlp_ada_dom_global_status",
    "fn_prd_mlp_notpii_dom_autoloader_dev_status",
    "fn_prd_mlp_notpii_dom_autoloader_uat_status",
    "fn_prd_mlp_notpii_dom_ingesta_status",
    "fn_prd_mlp_notpii_dom_global_status",
    "fn_prd_mlp_ssag_dom_resumen_status",
    "fn_uat_mlp_svfn_dom_fuente_notpii_interpolated_status",
    "fn_uat_mlp_svfn_dom_tags_status",
    "fn_uat_mlp_svfn_dom_transformacion_status",
    "fn_uat_mlp_svfn_dom_prediccion_status",
    "fn_uat_mlp_svfn_dom_resumen_status",
    "fn_uat_ant_mtsa_dom_resumen_status",
    "fn_uat_ant_mtsa_dom_frontend_status",
    "fn_uat_ant_mtsa_dom_procesamiento_status",
    "fn_uat_ant_mtsa_dom_regla_negocio_status",
    "fn_uat_ant_mtsa_dom_ingestas_status",
    "fn_uat_cen_minco_sm_dom_ingestas_status",
    "fn_uat_cen_minco_sm_dom_regla_negocio_status",
    "fn_uat_cen_minco_sm_dom_procesamiento_status",
    "fn_uat_cen_minco_sm_dom_frontend_status",
    "fn_uat_cen_minco_sm_dom_resumen_status",
    "fn_uat_cen_minco_sm_dom_global_status",
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
    "var_mlp_ada_jobs_detail.kql",
    "var_mlp_ada_jobs_detail_legacyfmt.kql",
    "var_mlp_notpii_autoloader_dev.kql",
    "var_mlp_notpii_autoloader_uat.kql",
    "var_mlp_notpii_ingesta.kql",
    "var_mlp_notpii_difusion_global.kql",
    "var_mlp_sirosag_resumen.kql",
    "var_mlp_svfn_resumen.kql",
    "var_mlp_svfn_global.kql",
    "var_mlp_svfn_fuente_notpii_interpolated.kql",
    "var_mlp_svfn_tags.kql",
    "var_mlp_svfn_transformacion.kql",
    "var_mlp_svfn_prediccion.kql",
    "var_ant_mtsa_frontend.kql",
    "var_ant_mtsa_procesamiento.kql",
    "var_ant_mtsa_regla_negocio.kql",
    "var_ant_mtsa_ingestas.kql",
    "var_ant_mtsa_global.kql",
    "var_ant_mtsa_resumen.kql",
    "var_cen_minco_sm_ingestas.kql",
    "var_cen_minco_sm_regla_negocio.kql",
    "var_cen_minco_sm_procesamiento.kql",
    "var_cen_minco_sm_frontend.kql",
    "var_cen_minco_sm_resumen.kql",
    "var_cen_minco_sm_global.kql",
}

ALLOWED_NON_DOMAIN_WRAPPERS = {
    "var_mlp_ada_jobs_detail.kql": {"fn_prd_mlp_ada_jobs_status_detail"},
    "var_mlp_ada_jobs_detail_legacyfmt.kql": {"fn_prd_mlp_ada_jobs_status_detail"},
}

law_files = sorted(LAW.rglob("*.kql"))
wrapper_files = sorted(WRAPPERS.rglob("*.kql"))
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

# Legacy layout guardrails: wrappers must live under <ambiente>/<faena>/<producto>
legacy_wrapper_dirs = {"ada", "notpii", "sirosag"}
for legacy_dir in sorted(legacy_wrapper_dirs):
    if (WRAPPERS / legacy_dir).exists():
        errors.append(
            f"Legacy wrapper folder detected: grafana_wrappers/{legacy_dir}. "
            f"Use grafana_wrappers/{AMBIENTE}/{FAENA}/{legacy_dir} instead."
        )

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

# Naming guardrails: enforce MLP prefix in source files
for path in (LAW_SCOPE / "sources").glob("fn_src*.kql"):
    if not path.name.startswith("fn_src_mlp_"):
        errors.append(f"Non-standard source filename (missing mlp prefix): {path.relative_to(ROOT)}")


# Ensure source files are mirrored between full/body_only and avoid legacy source wrapper names
legacy_source_names = {
    "fn_src_mlp_ada_consolelogs.kql",
    "fn_src_mlp_ws_ada_table.kql", "fn_src_mlp_ws_ada_systemlogs.kql", "fn_src_mlp_ws_ada_consolelogs.kql",
    "fn_src_mlp_ws_pisystem_table.kql", "fn_src_mlp_ws_pisystem_systemlogs.kql", "fn_src_mlp_ws_pisystem_consolelogs.kql",
    "fn_src_mlp_ws_ssag_table.kql", "fn_src_mlp_ws_ssag_systemlogs.kql", "fn_src_mlp_ws_ssag_consolelogs.kql",
    "fn_src_mlp_ws_notpii_databricksjobs_dev.kql", "fn_src_mlp_ws_notpii_databricksjobs_uat.kql",
    "fn_src_mlp_ws_dispatch_pipelineruns.kql", "fn_src_mlp_ws_drillit_pipelineruns.kql", "fn_src_mlp_ws_blkgrde_pipelineruns.kql",
    "fn_src_mlp_ws_meteo_systemlogs.kql", "fn_src_mlp_ws_plans_systemlogs.kql", "fn_src_mlp_ws_pdmsagi_systemlogs.kql",
}
for fname in sorted(legacy_source_names):
    if (LAW_SCOPE / "sources" / fname).exists() or (BODY_SCOPE / "sources" / fname).exists():
        errors.append(f"Legacy source wrapper must be removed: {fname}")

law_source_files = {p.name for p in (LAW_SCOPE / "sources").glob("*.kql")}
body_source_files = {p.name for p in (BODY_SCOPE / "sources").glob("*.kql")}
for missing in sorted(law_source_files - body_source_files):
    errors.append(f"Missing body_only source mirror: law_functions_body_only/{AMBIENTE}/{FAENA}/sources/{missing}")
for extra in sorted(body_source_files - law_source_files):
    errors.append(f"Extra body_only source without full counterpart: law_functions_body_only/{AMBIENTE}/{FAENA}/sources/{extra}")


# Merge-conflict marker guard
for path in LAW.rglob("*.kql"):
    text = path.read_text(encoding="utf-8")
    if CONFLICT_RE.search(text):
        errors.append(f"Merge-conflict marker detected in {path.relative_to(ROOT)}")
for path in BODY.rglob("*.kql"):
    text = path.read_text(encoding="utf-8")
    if CONFLICT_RE.search(text):
        errors.append(f"Merge-conflict marker detected in {path.relative_to(ROOT)}")

# Undefined references
for path in all_files:
    text = path.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    for call in calls:
        if call not in func_defs:
            errors.append(f"Undefined call: {call} referenced in {path.relative_to(ROOT)}")

# Ensure wrappers call exactly one domain/detail function; color helpers are allowed.
for path in wrapper_files:
    text = path.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    domain_calls = [c for c in calls if c != "fn_mon_status_to_color"]
    if len(domain_calls) != 1:
        errors.append(f"Wrapper must call exactly one domain/detail function: {path.name} has {calls}")
    else:
        fn = domain_calls[0]
        allowed_extra = ALLOWED_NON_DOMAIN_WRAPPERS.get(path.name, set())
        if fn not in REQUIRED_DOMAINS and fn not in allowed_extra:
            errors.append(f"Wrapper {path.name} points to non-domain function: {fn}")

# Ensure global depends only on domain functions + cross helper
global_file = LAW_SCOPE / "ada/domains/fn_prd_mlp_ada_dom_global_status.kql"
if global_file.exists():
    text = global_file.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    allowed = set(REQUIRED_DOMAINS) | {"fn_prd_mlp_ada_dom_global_status"}
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
