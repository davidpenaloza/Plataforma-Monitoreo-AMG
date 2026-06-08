#!/usr/bin/env python3
"""Static readiness checks for importing the CROSS dashboard into Grafana 12."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VALID_UID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
AZURE_MONITOR_TYPE = "grafana-azure-monitor-datasource"
EXPECTED_TOP_LEVEL_SECTIONS = [
    "Ingestas Cross",
    "Resumen Ejecutivo",
    "MONITOREO ANALITICA AVANZADA  Productos CROSS",
    "MONITOREO REPORTABILIDAD  Productos CROSS",
]
EXPECTED_SITE_SUMMARIES = {
    "Resumen Fuentes MLP",
    "Resumen Fuentes CEN",
    "Resumen Fuentes ANT",
    "Resumen Fuentes CMZ",
    "Resumen Fuentes AMSA CROSS",
    "Resumen Productos MLP",
    "Resumen Productos CENTINELA",
    "Resumen Productos ANT",
    "Resumen Productos  ZALDIVAR",
    "Resumen Productos AMSA CROSS",
}

LEGACY_ANGULAR_PANEL_TYPES = {
    "graph-old",
    "singlestat",
    "table-old",
    "worldmap-panel",
}


def walk_panels(panels: list[dict[str, Any]]):
    for panel in panels:
        yield panel
        yield from walk_panels(panel.get("panels", []))


def validate(path: Path) -> list[str]:
    dashboard = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if dashboard.get("schemaVersion", 0) <= 0:
        errors.append("schemaVersion must be a positive integer")

    dashboard_uid = dashboard.get("uid", "")
    if not VALID_UID.fullmatch(dashboard_uid):
        errors.append(f"invalid dashboard UID: {dashboard_uid!r}")

    top_level_panels = dashboard.get("panels", [])
    panels = list(walk_panels(top_level_panels))

    section_titles = [
        panel.get("title") for panel in top_level_panels if panel.get("type") == "row"
    ]
    if section_titles != EXPECTED_TOP_LEVEL_SECTIONS:
        errors.append(
            "top-level operational flow changed; expected sections "
            f"{EXPECTED_TOP_LEVEL_SECTIONS!r}, got {section_titles!r}"
        )

    panel_titles = {panel.get("title") for panel in panels}
    missing_summaries = sorted(EXPECTED_SITE_SUMMARIES - panel_titles)
    if missing_summaries:
        errors.append(
            f"missing source/product summaries required for triage: {missing_summaries!r}"
        )

    if len(panels) != 20:
        errors.append(
            f"expected 20 panels from the operational baseline, found {len(panels)}"
        )
    panel_ids = [panel.get("id") for panel in panels]
    if len(panel_ids) != len(set(panel_ids)):
        errors.append("panel IDs are not unique")

    for panel in panels:
        panel_type = panel.get("type")
        if panel_type in LEGACY_ANGULAR_PANEL_TYPES:
            errors.append(
                f"panel {panel.get('id')} uses removed Angular type {panel_type!r}"
            )
        if panel_type == "text":
            options = panel.get("options", {})
            if options.get("mode") != "html":
                errors.append(
                    f"text panel {panel.get('id')} must remain in HTML mode"
                )
            content = options.get("content", "")
            if "<style" in content.lower():
                errors.append(
                    f"text panel {panel.get('id')} contains an unsupported <style> block"
                )

    links = []
    for panel in panels:
        content = panel.get("options", {}).get("content", "")
        links.extend(re.findall(r'href=["\']([^"\']+)', content, re.IGNORECASE))
    if len(links) != 17:
        errors.append(
            f"expected 17 drill-down links from the operational baseline, found {len(links)}"
        )

    variables = dashboard.get("templating", {}).get("list", [])
    if len(variables) != 91:
        errors.append(
            f"expected 91 variables from the operational baseline, found {len(variables)}"
        )
    query_variables = [variable for variable in variables if variable.get("type") == "query"]
    for variable in query_variables:
        name = variable.get("name", "<unnamed>")
        datasource = variable.get("datasource")
        if not isinstance(datasource, dict):
            errors.append(f"query variable {name} has no explicit datasource")
            continue
        if datasource.get("type") != AZURE_MONITOR_TYPE:
            errors.append(
                f"query variable {name} uses unexpected datasource type "
                f"{datasource.get('type')!r}"
            )
        uid = datasource.get("uid", "")
        if not VALID_UID.fullmatch(uid):
            errors.append(f"query variable {name} has invalid datasource UID {uid!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dashboard",
        nargs="?",
        default="Plataforma Monitoreo CROSS Refactorizado-1780931150712.json",
        type=Path,
    )
    args = parser.parse_args()

    errors = validate(args.dashboard)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.dashboard} is statically ready for Grafana 12 import")
    return 0


if __name__ == "__main__":
    sys.exit(main())
