# Plataforma Monitoreo AMG

Repositorio técnico del modelo de monitoreo utilizado por Soporte Data & Analítica Avanzada para estandarizar monitoreo de productos, fuentes, dominios, jobs, pipelines, funciones KQL, dashboards Grafana y reglas operativas.

## Documentación principal

- [Modelo de monitoreo](docs/modelo-monitoreo/README.md): fuente oficial técnica y operativa del nuevo modelo.
- [Documentación técnica previa](readme_codex.md): análisis consolidado del estado del repositorio y contexto histórico.
- [README refactor ADA optimized](refactor_ada_optimized/README.md): documentación del paquete de funciones/wrappers refactorizados.

## Artefactos principales

- `refactor_ada_optimized/law_functions`: funciones KQL para Azure Log Analytics Workspace.
- `refactor_ada_optimized/grafana_wrappers`: wrappers consumidos desde Grafana.
- `refactor_ada_optimized/power_automate_queries`: consultas auxiliares para integraciones operativas.
- `Plataforma_Monitoreo_AMG.json`: dashboard Grafana exportado.
- `docs/modelo-monitoreo`: documentación oficial del modelo de monitoreo.

> No incluir secretos, tokens, credenciales ni IDs sensibles en la documentación o ejemplos operativos. Si un dato no está disponible en el repositorio, documentarlo como **Por definir** o **Por validar**.
