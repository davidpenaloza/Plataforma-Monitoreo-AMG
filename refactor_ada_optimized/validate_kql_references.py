#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
LAW = ROOT / "law_functions"
WRAPPERS = ROOT / "grafana_wrappers"

DEF_RE = re.compile(r"\blet\s+(fn_[A-Za-z0-9_]+)\s*=\s*\(")
CALL_RE = re.compile(r"\b(fn_[A-Za-z0-9_]+)\s*\(")

law_files = sorted(LAW.rglob("*.kql"))
wrapper_files = sorted(WRAPPERS.glob("*.kql"))
all_files = law_files + wrapper_files

func_defs = {}
for path in law_files:
    text = path.read_text(encoding="utf-8")
    for m in DEF_RE.finditer(text):
        name = m.group(1)
        func_defs[name] = path

errors = []
for path in all_files:
    text = path.read_text(encoding="utf-8")
    calls = sorted(set(CALL_RE.findall(text)))
    for call in calls:
        if call not in func_defs:
            errors.append(f"Undefined call: {call} referenced in {path.relative_to(ROOT)}")

if errors:
    print("KQL reference validation FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print("KQL reference validation OK")
print(f"Defined functions: {len(func_defs)}")
print(f"Checked files: {len(all_files)}")
