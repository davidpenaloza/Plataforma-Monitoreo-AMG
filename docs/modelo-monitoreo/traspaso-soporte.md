# Traspaso operativo para soporte

## Objetivo

Explicar al equipo de soporte cómo usar el modelo de monitoreo para revisar alertas, diferenciar causas probables y recopilar evidencia útil para escalamiento.

## Qué necesita saber soporte

- El dashboard Grafana muestra estados calculados por funciones KQL versionadas en este repositorio.
- Una alerta visual debe trazarse desde el panel hacia un wrapper y luego hacia una función de dominio.
- Los dominios agrupan criterios operativos, por ejemplo jobs, pipelines, fuentes, freshness, lag o logs de error.
- El portal de soporte debe enlazar runbooks, pero la definición técnica oficial vive en esta documentación y en los archivos KQL del repositorio.
- Si un dato no está documentado, debe registrarse como **Por definir** o **Por validar**, no asumirse.

## Qué revisar ante una alerta

1. Identificar producto y dominio en el panel.
2. Confirmar rango temporal seleccionado en Grafana.
3. Revisar si el estado es `WARN` o `ALERT` y si hay detalle textual.
4. Ejecutar o solicitar ejecución de la función de dominio en LAW.
5. Validar si los sources tienen datos recientes.
6. Revisar si hay mantenimiento, despliegue o incidente conocido: **Por validar** si no está documentado.
7. Consultar el runbook del portal de soporte cuando exista.
8. Escalar con evidencia completa si el dominio confirma falla.

## Diferenciar tipo de problema

| Tipo de problema | Señales | Qué revisar |
|---|---|---|
| Producto | Logs muestran errores reales, jobs fallan o datos no llegan. | Dominio, helper de detalle, source y runbook del producto. |
| Fuente | Source sin datos o tabla no existe. | Función `fn_src_mlp_*`, permisos, workspace y ventana temporal. |
| Dashboard | LAW devuelve OK/datos, pero Grafana muestra vacío o color incorrecto. | Wrapper, macros de tiempo, thresholds y datasource. |
| Función KQL | Error de compilación, función desconocida o lógica inconsistente. | Catálogo, dependencias, validador y cambios recientes. |
| Operación/mantenimiento | Alertas esperadas durante ventana planificada. | Calendario o registro de mantenimiento: Por definir si no existe. |

## Evidencia mínima para escalar

- Producto y dominio.
- Ambiente.
- Fecha y hora UTC de detección.
- Rango temporal del dashboard.
- Estado observado (`OK`, `WARN`, `ALERT` o sin datos).
- Query o función ejecutada.
- Resultado resumido y filas relevantes.
- Captura de Grafana si aplica.
- Mensaje de error completo si existe.
- Runbook consultado y paso donde se detuvo.
- Impacto reportado por usuarios o sistemas: **Por definir** si no hay evidencia.

## Relación con runbooks del portal de soporte

El portal de soporte debe contener procedimientos operativos, responsables y pasos de atención. Esta documentación contiene el modelo técnico. La relación recomendada es:

```text
Alerta Grafana -> Runbook portal soporte -> Documentación técnica repo -> Función KQL / evidencia LAW
```

Si un runbook del portal contradice esta documentación, se debe levantar corrección para alinear ambos, manteniendo el repositorio como fuente técnica oficial.

## Preguntas rápidas para triage

- ¿El panel está en el rango temporal correcto?
- ¿La función de dominio devuelve ALERT también en LAW?
- ¿El source tiene datos en la ventana?
- ¿La alerta ocurre en un solo dominio o en el global?
- ¿Hay funciones desconocidas o errores de permisos?
- ¿El color viene de KQL o de un threshold local de Grafana?
- ¿Existe runbook para este dominio?

## Pendientes operativos

- Responsables por producto: **Por definir** si no están en el repositorio.
- Matriz de escalamiento: **Por definir**.
- Calendario de mantenimientos: **Por definir**.
- Ubicación definitiva de runbooks en portal de soporte: **Por definir**.

## Caso aplicado: PDM CAEX (UAT)

Este producto se incorporó al modelo con patrón completo (helpers + domains + wrappers + Power Automate).

### Qué debe usar soporte en PDM CAEX

- **Estado global**: `fn_prd_mlp_pdm_caex_dom_resumen_status`.
- **Estado fuentes global**: `fn_prd_mlp_pdm_caex_dom_fuentes_status`.
- **Estado por fuente**:
  - `fn_prd_mlp_pdm_caex_dom_fuente_horometros_status`
  - `fn_prd_mlp_pdm_caex_dom_fuente_minecare_status`
  - `fn_prd_mlp_pdm_caex_dom_fuente_dispatch_status`
- **Jobs dominio**: `fn_prd_mlp_pdm_caex_dom_jobs_status`.
- **Envío emails**: `fn_prd_mlp_pdm_caex_dom_emails_status`.

### Lección operativa clave

Si aparece error de función no encontrada (ejemplo: helper de umbrales), validar orden de despliegue:

1. Helpers de umbral.
2. Funciones dominio que consumen helpers.
3. Wrappers Grafana y query de Power Automate.

Para PDM CAEX, dejar disponible la query de automatización en:

- `refactor_ada_optimized/power_automate_queries/prd/mlp/pdm_caex/resumen_estado.kql`

Esto permite a soporte consumir el estado en formato estándar (`orden`, `producto`, `estado`, `color`, `icono`) sin reescribir lógica de negocio.
