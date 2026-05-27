# Análisis comparativo de documentos base — Plataforma Monitoreo AMG

**Fecha:** 27 de mayo de 2026  
**Objetivo:** Determinar qué documento conviene usar como base para construir la documentación definitiva y la guía operativa de traspaso al equipo de soporte.

## 1. Documentos revisados

| Documento | Rol observado | Fortalezas | Riesgos o brechas |
|---|---|---|---|
| `README.md` | Índice general del repositorio. | Es breve, ordena los artefactos principales y declara que no se deben incluir secretos, tokens, credenciales ni IDs sensibles. | No sirve como documento de traspaso; es demasiado resumido. |
| `readme_codex.md` | Documentación técnica consolidada del repositorio. | Es la mejor fuente para entender estado actual, arquitectura, alcance, productos, brechas, madurez y recomendaciones. | Es extenso y mezcla diagnóstico, documentación técnica, pendientes y recomendaciones; requiere depuración para quedar como documento oficial. |
| `traspaso_codex.md` | Guía práctica para implementar funciones y dashboards. | Es la mejor base para el traspaso operativo: explica capas, sources, helpers, domains, wrappers, validación, Grafana y procedimiento de implementación. | Le falta mayor contexto ejecutivo, gobernanza, criterios de aceptación, matriz de roles y control formal de despliegue. |
| `CLAUDE.md` | Guía completa generada para traspaso. | Aporta secciones muy útiles: despliegue en LAW, integración con Grafana, Power Automate, implementación de nuevos productos, glosario y troubleshooting. | Debe depurarse porque puede afirmar como existente algo que otros documentos marcan como brecha, por ejemplo `law_functions_body_only`. También trae ejemplos con identificadores que conviene reemplazar por placeholders. |

## 2. Decisión de consolidación

No conviene usar un único documento como definitivo. La mejor solución es fusionar los aportes de los cuatro documentos:

| Entregable final | Base principal | Complementos utilizados | Criterio aplicado |
|---|---|---|---|
| `DOCUMENTACION_MODELO_MONITOREO_DEFINITIVA.md` | `readme_codex.md` | `README.md` y secciones conceptuales de `CLAUDE.md` | Documento técnico oficial, con foco en arquitectura, alcance, contratos, estándares, brechas y modelo futuro. |
| `GUIA_TRASPASO_OPERATIVA_SOPORTE.md` | `traspaso_codex.md` | Secciones prácticas de `CLAUDE.md` | Guía paso a paso para que soporte implemente, valide, despliegue y opere el modelo. |

## 3. Criterios usados para depurar la versión final

1. **Separar documentación técnica de guía operativa.** La documentación explica el modelo; la guía enseña cómo implementarlo.
2. **No asumir elementos no confirmados.** Si un archivo, carpeta, pipeline o automatización no está confirmado, queda como `Por validar`.
3. **Evitar datos sensibles.** Los ejemplos usan placeholders como `<SUBSCRIPTION_ID>`, `<RESOURCE_GROUP>` y `<WORKSPACE_NAME>`.
4. **Priorizar trazabilidad.** Todo debe permitir recorrer: `Panel/Variable -> Wrapper -> Domain -> Helper -> Source -> Workspace/Tabla`.
5. **Estandarizar contratos.** Para nuevas funciones, se recomienda devolver `domain`, `status`, `color`, `reason`, `startTime`, `endTime`, `evidence` y `severity`.
6. **Mantener brechas visibles.** No se ocultan problemas actuales como validación KQL pendiente, contratos `status/color` inconsistentes o JSON Grafana con lógica legacy.

## 4. Recomendación final

- Dejar `README.md` como entrada liviana del repositorio.
- Reemplazar o versionar `readme_codex.md` por `DOCUMENTACION_MODELO_MONITOREO_DEFINITIVA.md`.
- Reemplazar o versionar `traspaso_codex.md` y `CLAUDE.md` por `GUIA_TRASPASO_OPERATIVA_SOPORTE.md`.
- Mantener `CLAUDE.md` solo como antecedente histórico o eliminarlo si genera confusión, porque mezcla manual general, runbook, inventario y ejemplos de implementación en un solo archivo.
