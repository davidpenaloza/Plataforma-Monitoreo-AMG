# Traspaso técnico-operativo — Plataforma Monitoreo AMG

## Resumen ejecutivo

Este documento de traspaso prepara al equipo de soporte para operar, diagnosticar y replicar el modelo de monitoreo de Plataforma Monitoreo AMG. El objetivo práctico es que una persona nueva pueda leer un panel, identificar la variable o wrapper asociado, ejecutar la función KQL correspondiente, validar la fuente de datos y escalar con evidencia.

El repositorio ya contiene una base reutilizable para ADA, ADA AMG, NOTPII y SIROSAG, pero el traspaso debe considerar brechas abiertas: el validador KQL falla actualmente, ADA AMG requiere normalización, no existe procedimiento automatizado de despliegue y los permisos/RBAC no están documentados. Por eso este documento separa estado actual, modelo recomendado, brechas, despliegue, ejercicios y criterios de aceptación.

## 1. Objetivo del documento

Este documento transfiere conocimiento al equipo de soporte para que pueda entender, operar, mantener y replicar el modelo de monitoreo contenido en este repositorio.

La meta no es solo saber dónde están los archivos, sino comprender cómo se transforma una señal técnica —logs, jobs, pipelines o tablas— en un estado operativo visible en Grafana o consumible por Power Automate.

## 2. Público objetivo

| Rol | Uso esperado del documento |
|---|---|
| Soporte Nivel 1 | Interpretar estados, validar datos visibles y escalar con contexto. |
| Soporte Nivel 2 | Diagnosticar queries, fuentes, funciones y falsos positivos. |
| Analistas | Leer KQL, adaptar consultas y documentar paneles. |
| Analistas senior | Diseñar nuevas reglas y validar paridad con modelos legacy. |
| Líderes técnicos | Gobernar estándares, despliegues, revisiones y deuda técnica. |
| Constructores de dashboards | Crear o mantener paneles operativos reutilizables. |

## 3. Qué debe aprender el equipo de soporte

Al finalizar el traspaso, soporte debe poder:

- Entender el modelo por capas: source, helper, domain, wrapper y dashboard.
- Identificar qué fuente alimenta cada dominio monitoreado.
- Leer una query KQL y reconocer filtros de tiempo, tablas, jobs y umbrales.
- Interpretar estados `OK`, `ALERT`, `NOOK`, `Alertar` y colores.
- Usar el dashboard para separar alerta real, falta de datos, problema de permisos o problema visual.
- Validar si una función está desplegada y devuelve columnas esperadas.
- Adaptar el patrón a otro producto sin duplicar lógica innecesariamente.
- Documentar nuevos paneles, fuentes y reglas.
- Escalar incidentes con evidencia: dominio, fuente, ventana, query y resultado.

## 4. Modelo conceptual de monitoreo

### 4.1 Qué es monitorear

Monitorear es observar señales técnicas y funcionales para tomar decisiones operativas oportunas. En este repositorio, las señales provienen principalmente de Log Analytics Workspaces y se transforman en estados de salud.

### 4.2 Monitoreo técnico, funcional y operativo

| Tipo | Qué observa | Ejemplo en este repositorio | Decisión que habilita |
|---|---|---|---|
| Técnico | Logs, jobs, pipelines, tablas, errores | `ContainerAppSystemLogs_CL`, `AzureDiagnostics`, `DatabricksJobs` | Revisar ejecución, permisos, latencia o fallas de infraestructura. |
| Funcional | Cumplimiento de reglas del producto | Expected-vs-real, lag de tablas, fallas consecutivas | Determinar si un dominio del producto está sano. |
| Operativo | Estado consolidado para soporte | `GlobalStatus`, colores de Grafana, resumen SIROSAG/NOTPII/ADA | Priorizar atención, escalar y comunicar impacto. |

### 4.3 De datos crudos a indicadores

```mermaid
flowchart TD
    A[Logs y tablas crudas] --> B[Source KQL]
    B --> C[Helper: regla reutilizable]
    C --> D[Domain: estado por dominio]
    D --> E[Wrapper Grafana o query Power Automate]
    E --> F[Panel / flujo / operación]
    F --> G[Acción de soporte]
```

### 4.4 Consolidación de estados

Un estado global no debería inventar reglas nuevas: debe consolidar dominios. En ADA, el dominio global consulta dominios como Dispatch, Drillit, Blockgrade, PI, Plans, Meteodata, KPI, Alarmas, Front, Optimizador y Settings, y marca global en alerta si alguno está en `ALERT`.

## 5. Arquitectura del modelo de monitoreo del repositorio

```mermaid
flowchart LR
    subgraph Azure[Azure Log Analytics]
      T1[ContainerAppSystemLogs_CL]
      T2[ContainerAppConsoleLogs_CL]
      T3[AppServiceConsoleLogs]
      T4[AzureDiagnostics]
      T5[DatabricksJobs]
      T6[Logs_MLP_ADA_CL]
    end

    T1 --> S[Sources fn_src_mlp_*]
    T2 --> S
    T3 --> S
    T4 --> S
    T5 --> S
    T6 --> S

    S --> H[Helpers de reglas]
    H --> D[Domains por producto]
    D --> W[Wrappers var_mlp_*]
    W --> P[Dashboard Grafana]
    D --> PA[Power Automate queries]
    P --> N1[Soporte N1]
    P --> N2[Soporte N2]
```

### Rol de cada capa

| Capa | Rol | Qué debe revisar soporte |
|---|---|---|
| Fuente | Trae datos desde workspace/tabla. | Workspace correcto, tabla existe, columnas esperadas, permisos. |
| Helper | Aplica regla reusable. | Umbral, ventana, job, tabla, excepciones. |
| Domain | Devuelve estado funcional. | Qué condiciones disparan `ALERT`. |
| Wrapper | Adapta la salida a Grafana. | Columna proyectada (`color`, `status` o detalle), macros de tiempo. |
| Dashboard | Visualiza estado. | Variables, paneles, refresh, tiempo seleccionado. |
| Power Automate | Automatiza consumo de estado. | Query usada, salida esperada y frecuencia. |

## 6. Flujo general de funcionamiento

1. **Nacen los datos:** servicios, jobs, pipelines, Databricks o aplicaciones escriben logs en Azure Log Analytics.
2. **Se consultan:** una función `fn_src_mlp_ws_*` lee la tabla correspondiente y filtra por ventana de tiempo.
3. **Se transforman:** helpers calculan lag, expected-vs-real, fallas consecutivas, warnings o errores.
4. **Se evalúan reglas:** domains convierten señales técnicas en estados como `OK` o `ALERT`.
5. **Se consolidan:** domains globales unen estados por dominio y determinan estado global.
6. **Se visualizan:** wrappers alimentan variables o paneles de Grafana.
7. **Soporte interpreta:** soporte revisa color/estado, baja al detalle, valida fuentes y escala si corresponde.

## 7. Componentes que debe dominar soporte

| Componente | Qué es | Para qué sirve | Qué debe revisar soporte | Errores detectables | Acción sugerida |
|---|---|---|---|---|---|
| `Plataforma_Monitoreo_AMG.json` | Dashboard Grafana exportado. | Visualización del monitoreo. | Variables, paneles, datasource, rango de tiempo. | Variables sin datos, panel HTML sin color, datasource incorrecto. | Validar variable en Grafana Explore y revisar wrapper. |
| `law_functions/prd/mlp/sources` | Capa de acceso a datos. | Encapsula workspaces/tablas. | Workspace, tabla, columnas, permisos. | Tabla inexistente, workspace incorrecto, datos atrasados. | Consultar source directamente con rango corto. |
| `ada/domains` | Estados de ADA. | Define salud por dominio. | Condición que genera alerta. | Falso positivo por umbral o lag. | Ejecutar domain y helpers relacionados. |
| `ada/helpers` | Reglas reutilizables ADA. | Evita duplicar lógica. | Umbrales, catálogos, ventanas, excepciones. | Cambio de job, KPI excluido, timezone. | Validar paso a paso. |
| `ada_amg/domain` | Variante ADA AMG. | Monitoreo ADA AMG. | Estructura y compatibilidad con validador. | Archivo sin `.kql`, wrappers fuera del set requerido. | Regularizar antes de producción formal. |
| `notpii` | Reglas autoloader/ingesta. | Monitorear NOTPII DEV/UAT e ingesta. | DatabricksJobs y PI System. | Estados `Alertar`, warnings, jobs sin ejecución. | Revisar helper específico. |
| `sirosag` | Resumen SIROSAG. | Evaluar ejecución, desfase y desactualización. | Job names, ventanas, logs SSAG. | Datos desactualizados o desfase. | Revisar helpers `eval_*`. |
| `grafana_wrappers` | Entrypoints Grafana. | Simplificar variables. | Función llamada y columna final. | Mismatch `project color` vs salida `status`. | Ajustar contrato o documentar excepción. |
| Scripts Python | Auditoría estática. | Validación previa a cambios. | Salida de comandos y brechas. | Referencias indefinidas, mirrors faltantes, conflictos. | Corregir o registrar pendiente. |

## 8. Cómo leer un dashboard de monitoreo

### 8.1 Panel resumen

1. Confirmar el rango de tiempo seleccionado.
2. Revisar el estado global por producto.
3. Identificar dominios en rojo o alerta.
4. No asumir impacto de negocio sin revisar detalle: un `ALERT` puede ser fuente sin datos, job fallido, lag o problema visual.

### 8.2 Bajar al detalle

- Si el global está en alerta, identificar qué dominio lo activó.
- Ejecutar la variable o wrapper asociada.
- Si existe detalle tabular (`jobs_detail`), revisar `domain`, `jobName`, `status`, `realCount`, `expectedCount`, `isAlert` y `reason`.
- Validar si la ventana del dashboard coincide con la ventana de la regla.

### 8.3 Diferenciar alerta real de falso positivo

| Señal | Probable causa | Validación |
|---|---|---|
| Dashboard sin datos | Datasource, permisos, rango, variable rota | Probar source directo. |
| Domain en `ALERT` pero fuente sin filas | Producto no emitió logs o source incorrecto | Consultar workspace/tabla con rango amplio. |
| Wrapper falla por columna | Contrato salida-wrapper inconsistente | Revisar `project color/status`. |
| Solo un usuario ve error | Permisos Grafana/Azure | Comparar con usuario con permisos conocidos. |
| Alerta intermitente | Ventana muy corta, latencia o job tardío | Ampliar rango y revisar expected-vs-real. |

## 9. Cómo interpretar estados, colores y alertas

| Estado/color | Significado observado | Acción soporte |
|---|---|---|
| `OK` / `#EAF4EA` | Estado normal o sin condición de alerta detectada. | Mantener observación. |
| `ALERT` / `#E53935` | Condición de alerta. | Revisar dominio, helper y fuente; escalar si hay impacto. |
| `WARN` / `WARNING` / `#FFF4CC` | Advertencia potencial. | Revisar tendencia y confirmar si requiere acción. |
| `NOOK` | Variante usada en ADA AMG para representar no OK. | Tratar como alerta funcional hasta normalizar. |
| `Alertar` | Estado usado por NOTPII antes de mapear a color. | Revisar autoloader o ingesta correspondiente. |
| `a`, `w`, `n`, `e` | Estados granulares en helpers/jobs: alerta, warning, normal o error según contexto. | Revisar `statusText`/`reason` y documentación del helper. |

**Pendiente de confirmar:** matriz oficial de severidades de negocio y procedimientos por color. El repositorio muestra estados y colores, pero no define SLA/SLO formal.

## 10. Cómo implementar este modelo en otro producto

1. **Levantar objetivo del producto:** qué debe saber soporte para operar.
2. **Identificar componentes críticos:** jobs, APIs, pipelines, tablas, app services, Databricks.
3. **Identificar fuentes:** workspaces, tablas, columnas y permisos.
4. **Definir reglas:** qué es OK, alerta, warning, ausencia de datos, retraso aceptable.
5. **Crear sources:** un `fn_src_mlp_ws_*` por workspace o fuente lógica.
6. **Crear helpers:** lag, ejecución, desfase, catálogos o parsing de logs.
7. **Crear domains:** una función por dominio y una global.
8. **Crear wrappers:** una query liviana por variable/panel.
9. **Crear paneles:** resumen accionable arriba, detalle abajo.
10. **Validar datos:** probar source → helper → domain → wrapper → panel.
11. **Documentar:** actualizar README, traspaso, inventario y plantilla de panel.
12. **Presentar a soporte:** explicar estados, acciones y escalamiento.
13. **Operar en producción:** revisar falsos positivos, costo y performance.

## 11. Checklist de implementación

| Ítem | Estado |
|---|---|
| Producto identificado | ☐ |
| Objetivo de monitoreo definido | ☐ |
| Componentes críticos identificados | ☐ |
| Workspaces identificados | ☐ |
| Tablas y columnas validadas | ☐ |
| Permisos validados | ☐ |
| Sources creados/adaptados | ☐ |
| Helpers creados/adaptados | ☐ |
| Domains creados/adaptados | ☐ |
| Estado global definido | ☐ |
| Wrappers creados | ☐ |
| Variables Grafana configuradas | ☐ |
| Panel resumen creado | ☐ |
| Panel detalle creado | ☐ |
| Queries probadas con datos reales | ☐ |
| Funciones desplegadas en LAW | ☐ |
| Dashboard importado/probado | ☐ |
| Alertas/colores validados | ☐ |
| Power Automate validado, si aplica | ☐ |
| Documentación actualizada | ☐ |
| Equipo de soporte capacitado | ☐ |
| Plan de rollback definido | ☐ |

## 12. Buenas prácticas para soporte

- No duplicar lógica si existe helper o domain reutilizable.
- Centralizar reglas comunes en KQL, no en HTML del dashboard.
- Documentar cada panel con objetivo, fuente, interpretación y acción.
- Mantener nombres claros y trazables.
- Validar siempre rango de tiempo y timezone.
- Revisar permisos antes de declarar caída de producto.
- Evitar queries costosas con ventanas amplias sin necesidad.
- Separar resumen ejecutivo de detalle diagnóstico.
- Diseñar paneles accionables: si no guía una acción, cuestionar su valor.
- Mantener trazabilidad desde alerta hasta fuente.
- Registrar falsos positivos y ajustar umbrales con aprobación técnica.

## 13. Buenas prácticas de diseño de dashboards

| Práctica | Aplicación recomendada |
|---|---|
| Resumen arriba | Mostrar global y dominios principales al inicio. |
| Detalle abajo | Tablas de jobs, razones y fuentes para diagnóstico. |
| Colores consistentes | Verde normal, rojo alerta, amarillo warning. |
| Texto claro | Cada panel debe responder “qué miro” y “qué hago si falla”. |
| Evitar saturación | No llenar con métricas sin acción asociada. |
| Variables explícitas | Nombres `var_mlp_<producto>_<dominio>`. |
| Drill-down | Desde global a dominio, desde dominio a source/helper. |
| Reutilización | Wrappers livianos para no repetir KQL en paneles. |

## 14. Buenas prácticas de KQL o consultas

- Iniciar por rango de tiempo: `where TimeGenerated between (startTime .. endTime)`.
- Filtrar por `ResourceGroup`, `JobName_s`, `OperationName` o tabla lo antes posible.
- Usar sources para esconder workspaces reales.
- Evitar accesos directos a `workspace()` fuera de `sources`, salvo excepción documentada.
- Probar cada bloque con `take 10` o `summarize count()` antes de unir.
- Mantener output estable: si el wrapper proyecta `color`, el domain debe producir `color`.
- Documentar umbrales y razones de excepciones.
- Evitar ampliar ventanas sin evaluar costo.
- Usar `union isfuzzy=true` con cautela y validar datos faltantes.
- Probar en orden: source → helper → domain → wrapper.

## 15. Diagnóstico operativo

### 15.1 El dashboard no muestra datos

1. Confirmar rango de tiempo.
2. Confirmar datasource de Grafana.
3. Ejecutar variable en Grafana Explore.
4. Ejecutar wrapper equivalente.
5. Ejecutar domain directo.
6. Ejecutar source directo.
7. Revisar permisos del usuario.
8. Registrar si falta tabla, workspace o columna.

### 15.2 El estado aparece en alerta

1. Identificar dominio exacto.
2. Revisar regla del domain.
3. Consultar helper que calcula la condición.
4. Comparar `real` vs `expected` si aplica.
5. Revisar últimos logs del job o tabla.
6. Confirmar si hay mantención o ventana especial.
7. Escalar al equipo responsable con evidencia.

### 15.3 La query falla

- Revisar si la función existe en LAW.
- Revisar nombres exactos de columnas.
- Revisar si el wrapper llama una función definida.
- Revisar si el archivo tiene extensión `.kql` y fue desplegado.
- Revisar errores por permisos cross-workspace.

### 15.4 La función no responde o está lenta

- Reducir ventana de tiempo.
- Probar source de forma aislada.
- Identificar `union` o `mv-expand` costosos.
- Revisar cantidad de filas con `summarize count()`.
- Consultar si hubo aumento de ingesta o cambio de esquema.

### 15.5 Hay diferencia entre usuarios

- Comparar permisos en Grafana.
- Comparar permisos sobre Log Analytics Workspace.
- Validar datasource y organización Grafana.
- Probar con un usuario de referencia.

### 15.6 Hay datos atrasados

- Revisar `max(TimeGenerated)` por tabla.
- Comparar hora UTC vs hora local.
- Validar latencia de ingesta.
- Revisar job/pipeline que produce la tabla.

### 15.7 La alerta parece falsa

- Revisar ventana y refresh.
- Confirmar si la regla tiene excepciones por mantención/horario.
- Verificar si una fuente cambió de formato.
- Registrar evidencia y proponer ajuste de umbral con aprobación.

## 16. Matriz de responsabilidades sugerida

| Rol | Responsabilidades |
|---|---|
| Soporte Nivel 1 | Revisar dashboard, registrar alertas, validar rango de tiempo, ejecutar checklist inicial y escalar con evidencia. |
| Soporte Nivel 2 | Ejecutar wrappers/domains/helpers, diagnosticar fuentes, confirmar falso positivo y proponer corrección operativa. |
| Líder técnico | Aprobar cambios de reglas, gobernar estándares, revisar PRs y coordinar despliegues. |
| Equipo de plataforma | Gestionar workspaces, permisos, datasource Grafana, disponibilidad de Log Analytics y costos. |
| Equipo de desarrollo | Corregir jobs, pipelines, aplicaciones o formatos de logs que originan la alerta. |
| Dueño del producto | Definir criticidad, ventanas aceptables, reglas funcionales y prioridad de incidentes. |

## 17. Runbook base de operación diaria

1. Abrir dashboard `Plataforma Monitoreo Prod`.
2. Confirmar rango de tiempo activo.
3. Revisar estado global de productos.
4. Revisar dominios en alerta.
5. Si hay alerta, abrir detalle o ejecutar wrapper/domain.
6. Validar fuente con rango corto.
7. Confirmar impacto funcional con dueño del producto si corresponde.
8. Registrar hallazgo: hora, producto, dominio, query, resultado y acción.
9. Escalar a N2, plataforma o desarrollo según causa.
10. Hacer seguimiento hasta normalización.
11. Cerrar caso con causa raíz o pendiente documentado.
12. Si fue falso positivo, registrar recomendación de ajuste.

## 18. Plantilla para documentar nuevos paneles

```markdown
## Panel: <nombre del panel>

- **Producto:** <producto>
- **Objetivo:** <qué decisión permite tomar>
- **Fuente de datos:** <workspace / tabla / source>
- **Query o función asociada:** <wrapper / domain / helper>
- **Qué representa:** <estado, tendencia, tabla, conteo>
- **Cómo se interpreta:** <reglas de lectura>
- **Estados posibles:** <OK / ALERT / WARN / otros>
- **Acciones ante alerta:** <pasos de soporte>
- **Responsable funcional:** <rol/equipo>
- **Responsable técnico:** <rol/equipo>
- **Ventana de tiempo recomendada:** <rango>
- **Dependencias:** <jobs, tablas, permisos>
- **Observaciones:** <pendientes o excepciones>
```

## 19. Plantilla para documentar nuevos productos monitoreados

```markdown
# Producto monitoreado: <nombre>

## Objetivo del monitoreo
<describir objetivo>

## Componentes críticos
| Componente | Tipo | Criticidad | Señal esperada |
|---|---|---|---|

## Fuentes
| Workspace | Tabla | Source KQL | Columnas clave |
|---|---|---|---|

## Reglas
| Dominio | Regla OK | Regla ALERT | Umbral | Ventana |
|---|---|---|---|---|

## Dashboards y paneles
| Panel | Wrapper | Interpretación | Acción soporte |
|---|---|---|---|

## Alertas y escalamiento
| Condición | Severidad | Escala a | Evidencia requerida |
|---|---|---|---|

## Consideraciones
- Pendientes:
- Riesgos:
- Supuestos:
```

## 20. Errores comunes y cómo evitarlos

| Error común | Cómo se ve | Cómo evitarlo |
|---|---|---|
| Ruta incorrecta de función | Validador reporta función no definida. | Mantener estructura `prd/mlp/<producto>` y extensión `.kql`. |
| Query duplicada en JSON | Alto costo y difícil mantenimiento. | Reemplazar por wrapper liviano. |
| Función no desplegada | Grafana falla aunque el archivo exista. | Verificar despliegue en LAW antes de dashboard. |
| Workspace incorrecto | No hay datos o hay falsos OK/ALERT. | Encapsular en source y validar catálogo. |
| Variable mal configurada | Panel queda vacío o sin color. | Confirmar nombre, refresh y columna proyectada. |
| Falta de permisos | Un usuario ve error y otro no. | Documentar RBAC y probar con usuario soporte. |
| Ventana mal interpretada | Alerta intermitente o sin sentido. | Revisar `$__timeFrom`, `$__timeTo`, UTC y horario local. |
| Dashboard sin descripción | Soporte no sabe actuar. | Usar plantilla de panel. |
| Estados no normalizados | Un panel usa `NOOK`, otro `ALERT`. | Definir catálogo común de estados. |
| Mirrors/documentación desactualizados | Auditoría contradice docs. | Actualizar docs y scripts junto con cambios. |

## 21. Recomendaciones finales

- Corregir brechas actuales antes de considerar el modelo listo para traspaso productivo completo.
- Normalizar salida de domains y wrappers: decidir si el contrato oficial es `status`, `color` o ambos.
- Incorporar ADA AMG formalmente al validador o separarlo como paquete experimental.
- Evitar volver a cargar KQL pesado dentro del JSON de Grafana.
- Crear procedimiento de despliegue de funciones LAW y dashboard.
- Documentar permisos mínimos por workspace y datasource.
- Mantener inventario de sources y dependencias actualizado.
- Agendar revisión periódica de falsos positivos, costos y performance.
- Capacitar soporte con casos reales: “sin datos”, “alerta real”, “falso positivo” y “error de permisos”.
- Hacer que cada alerta sea trazable hasta una fuente y una acción concreta.

## 22. Pendientes identificados para el traspaso

| Pendiente | Prioridad | Motivo |
|---|---|---|
| Resolver falla de `validate_kql_references.py` | Alta | El paquete no pasa auditoría estática actual. |
| Confirmar proceso de despliegue a LAW | Alta | Sin procedimiento, soporte no puede reproducir instalación. |
| Confirmar datasource y permisos Grafana/Azure | Alta | Requisito para operación diaria. |
| Normalizar ADA AMG | Media/Alta | Hay estructura y extensiones inconsistentes. |
| Actualizar JSON para usar wrappers refactorizados | Media | Reduce costo y duplicación. |
| Crear documentación por panel dentro de Grafana | Media | Facilita lectura operativa. |
| Definir severidades oficiales y matriz SLA/SLO | Media | Permite priorización consistente. |


## 23. Plan sugerido de capacitación para soporte

Para que el traspaso sea efectivo, no basta con entregar los archivos. Se recomienda realizar una capacitación práctica en sesiones cortas.

| Sesión | Duración sugerida | Objetivo | Actividad práctica | Resultado esperado |
|---|---:|---|---|---|
| 1. Contexto y arquitectura | 60 min | Entender capas del modelo y productos cubiertos. | Recorrer `readme_codex.md`, dashboard JSON y carpetas principales. | Soporte puede explicar source → helper → domain → wrapper → dashboard. |
| 2. Lectura de dashboard | 60 min | Interpretar resumen, detalle, estados y colores. | Simular lectura de `OK`, `ALERT`, sin datos y panel lento. | Soporte distingue alerta real de problema de monitoreo. |
| 3. Diagnóstico KQL básico | 90 min | Probar queries por capas. | Ejecutar secuencia source → helper → domain → wrapper en un entorno autorizado. | Soporte N2 obtiene evidencia técnica para escalar. |
| 4. Implementación en otro producto | 90 min | Replicar el patrón sin duplicar lógica. | Completar plantilla de nuevo producto y panel. | Equipo entiende cómo reutilizar el modelo. |
| 5. Operación y escalamiento | 60 min | Alinear roles, evidencias y comunicación. | Ejecutar runbook con un caso ficticio. | Soporte sabe qué registrar y a quién escalar. |

**Pendiente de confirmar:** disponibilidad de un entorno seguro para ejecutar KQL durante la capacitación y usuarios con permisos equivalentes a soporte.

## 24. Criterios de aceptación para considerar el traspaso listo

| Criterio | Aceptación mínima | Responsable sugerido |
|---|---|---|
| Documentación leída y validada | Soporte confirma que entiende arquitectura, fuentes, estados y runbook. | Líder técnico + Soporte N2 |
| Dashboard accesible | Usuarios de soporte pueden abrir el dashboard y ver variables sin errores de permisos. | Plataforma/Grafana |
| Queries críticas probadas | Al menos un source, un helper, un domain y un wrapper por producto probado con datos reales. | Soporte N2 |
| Validador acordado | `validate_kql_references.py` pasa o sus fallas quedan aceptadas formalmente como pendientes. | Líder técnico |
| Severidades definidas | Existe criterio oficial para actuar ante rojo/amarillo/verde. | Dueño del producto |
| Escalamiento validado | Cada dominio crítico tiene equipo responsable y canal de escalamiento. | Soporte + Producto |
| Rollback documentado | Existe forma de volver a query/panel anterior si una migración falla. | Plataforma + Líder técnico |

## 25. Evidencia mínima para escalar incidentes

Cuando soporte escale un incidente, debe adjuntar evidencia suficiente para evitar reprocesos.

| Dato | Obligatorio | Ejemplo |
|---|---|---|
| Producto | Sí | ADA |
| Dominio | Sí | Dispatch |
| Estado observado | Sí | `ALERT` / `#E53935` |
| Hora de detección | Sí | `2026-05-08 14:10 UTC` |
| Rango consultado | Sí | `now-30m` o fechas absolutas |
| Panel o variable | Sí | `var_mlp_ada_dispatch` |
| Función KQL | Sí para N2 | `fn_prd_mlp_ada_dom_dispatch_status` |
| Source o tabla | Deseable | `fn_src_mlp_ws_ada`, `ContainerAppSystemLogs_CL` |
| Resultado resumido | Sí | `job17 sin ejecuciones esperadas en 2 intervalos` |
| Impacto confirmado | Si existe | Usuarios/producto afectado, si fue confirmado por dueño del producto |
| Acción realizada | Sí | Validado source, escalado a desarrollo |

## 26. Escenarios prácticos de diagnóstico

### 26.1 Escenario A: variable roja en Grafana

1. Identificar variable y dominio.
2. Ejecutar wrapper con el mismo rango de tiempo.
3. Ejecutar domain directamente.
4. Si el domain devuelve alerta, revisar helper o source asociado.
5. Si el wrapper falla pero el domain funciona, revisar proyección `color/status`.
6. Registrar evidencia y escalar según matriz.

### 26.2 Escenario B: dashboard vacío

1. Confirmar que el rango no sea demasiado restrictivo.
2. Validar datasource y permisos del usuario.
3. Probar una query simple contra el workspace.
4. Probar source con `summarize count()`.
5. Si no hay datos, confirmar si el producto dejó de emitir logs o si cambió la tabla.
6. Escalar a plataforma si es permisos/datasource o a desarrollo si es emisión de logs.

### 26.3 Escenario C: falso positivo recurrente

1. Registrar ocurrencias con fecha, rango y dominio.
2. Revisar si coincide con ventanas de mantención, horarios especiales o latencia normal.
3. Comparar `expectedCount` vs `realCount` cuando exista detalle.
4. Revisar si el umbral es demasiado estricto.
5. Proponer ajuste documentado y validarlo con dueño del producto.
6. No modificar reglas sin aprobación.

### 26.4 Escenario D: falla después de adaptar a otro producto

1. Confirmar que los sources apuntan a workspaces del nuevo producto.
2. Confirmar nombres de tablas y columnas.
3. Confirmar que los jobs esperados existen con los nombres configurados.
4. Ejecutar source → helper → domain → wrapper.
5. Revisar si el validador contempla el nuevo producto.
6. Actualizar documentación e inventario.

## 27. Paquete mínimo que debe recibir soporte por cada nuevo producto

Cada vez que se replique el modelo en otro producto, soporte debería recibir un paquete documental mínimo:

| Entregable | Contenido mínimo |
|---|---|
| Inventario de fuentes | Workspaces, tablas, columnas clave, permisos y responsables. |
| Inventario de dominios | Regla OK/ALERT, umbral, ventana, helpers y sources. |
| Dashboard o paneles | Capturas o descripción, variables, datasource y rango recomendado. |
| Runbook específico | Pasos de diagnóstico por dominio crítico. |
| Matriz de escalamiento | Responsable técnico, producto, plataforma y canal. |
| Evidencia de validación | Queries probadas, resultados y fecha de validación. |
| Pendientes aceptados | Brechas conocidas y plan de cierre. |
| Rollback | Cómo volver a versión anterior del dashboard/query si falla. |

## 28. Cómo mantener viva esta documentación

- Revisar `readme_codex.md` y `traspaso_codex.md` en cada cambio de función, wrapper, dashboard o source.
- Agregar fecha y responsable en documentos específicos si se crean nuevas guías por producto.
- No aceptar nuevos paneles sin plantilla de interpretación y acción soporte.
- Mantener sincronizados inventario, dashboard y scripts de validación.
- Convertir brechas repetidas en tareas de backlog técnico.
- Revisar trimestralmente si las reglas siguen representando la operación real.


## 29. Estado actual detectado en el repositorio

| Elemento | Estado actual | Qué debe saber soporte |
|---|---|---|
| Dashboard | Existe `Plataforma_Monitoreo_AMG.json` con resumen y detalle de productos MLP. | Validar que el dashboard importado corresponda a la versión del repositorio. |
| Modelo KQL | Existe estructura por capas para ADA, NOTPII y SIROSAG; ADA AMG existe con brechas. | Diagnosticar por capas y no asumir que todos los productos tienen la misma madurez. |
| Validación | `validate_kql_references.py` reporta fallas existentes. | Un fallo del validador no debe ignorarse; debe cerrarse o aceptarse formalmente. |
| Despliegue | No se identificó pipeline automatizado. | Usar procedimiento manual controlado hasta que exista automatización. |
| Permisos | RBAC/datasources no están documentados. | Confirmar permisos antes de declarar caída de producto. |

## 30. Modelo recomendado para futuras implementaciones

| Capa | Recomendación para futuros productos | Beneficio para soporte |
|---|---|---|
| Source | Encapsular cada workspace/tabla en `fn_src_mlp_ws_*`. | Soporte sabe dónde validar datos crudos. |
| Helper | Crear helpers para reglas compartidas y diagnósticos. | Reduce duplicidad y permite explicar alertas. |
| Domain | Devolver contrato estándar con `domain`, `status`, `color`, `reason`, `severity`, ventana y evidencia. | Soporte puede escalar con contexto. |
| Wrapper | Mantener wrappers livianos y trazables. | Facilita resolver fallas de panel o variable. |
| Dashboard | Diseñar resumen ejecutivo + detalle accionable. | Soporte opera sin interpretar queries complejas dentro del panel. |
| Documentación | Exigir matriz de trazabilidad, runbook y descripción de panel. | El traspaso queda repetible. |

## 31. Brechas que deben cerrarse antes de producción

| Brecha | Riesgo | Acción antes de producción |
|---|---|---|
| Validador KQL en rojo. | Cambios no confiables o referencias rotas. | Corregir errores o aprobar excepción documentada. |
| ADA AMG no normalizado. | Wrappers/domains pueden no desplegarse o auditarse correctamente. | Normalizar extensión, carpeta y alcance del validador. |
| Contrato `status/color` inconsistente. | Paneles con error de columna. | Definir contrato estándar y adaptar wrappers. |
| Dashboard con KQL legacy pesado. | Mayor costo y complejidad. | Migrar gradualmente a wrappers livianos. |
| Sin RBAC documentado. | Diagnósticos inconsistentes entre usuarios. | Definir roles mínimos de Grafana y Log Analytics. |
| Sin rollback formal. | Riesgo al importar dashboard o alterar funciones LAW. | Respaldar dashboard y cuerpos KQL antes de cambios. |

## 32. Matriz de trazabilidad completa

| Producto | Panel o variable Grafana | Wrapper | Domain | Helper principal | Source | Workspace/Tabla | Qué valida | Acción de soporte |
|---|---|---|---|---|---|---|---|---|
| ADA | `var_mlp_ada_global` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_global.kql` | `fn_prd_mlp_ada_dom_global_status` | Dominios ADA consolidados | Sources ADA/PI/Plans/Meteo/Dataplatform/Genshare/PRFCI | Múltiples workspaces/tablas | Estado global ADA. | Bajar a dominio específico. |
| ADA | `var_mlp_ada_dispatch` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_dispatch.kql` | `fn_prd_mlp_ada_dom_dispatch_status` | `fn_prd_mlp_ada_lag_helpers`, `fn_prd_mlp_ada_alert_from_dispatch_nrt_logs` | `fn_src_mlp_ws_ada` | `mlp-prd-law-ada / ContainerAppSystemLogs_CL, ContainerAppConsoleLogs_CL` | Lag Dispatch, NRT y job17. | Revisar job17 y tablas Dispatch. |
| ADA | `var_mlp_ada_drillit` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_drillit.kql` | `fn_prd_mlp_ada_dom_drillit_status` | `fn_prd_mlp_ada_lag_helpers` | `fn_src_mlp_pipeline_runs_all`, `fn_src_mlp_ws_ada` | `mlp-prd-law-drillit / AzureDiagnostics`; ADA tablas Drillit | Pipeline y lag Drillit. | Revisar pipeline y tablas `drillit_*`. |
| ADA | `var_mlp_ada_blockgrade` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_blockgrade.kql` | `fn_prd_mlp_ada_dom_blockgrade_status` | `fn_prd_mlp_ada_lag_helpers`, `fn_prd_mlp_ada_en_mantencion` | `fn_src_mlp_pipeline_runs_all`, `fn_src_mlp_ws_dataplatform` | `mlp-prd-law-blkgrde / AzureDiagnostics`; `ams-dev-dataplatform-laws / Logs_MLP_ADA_CL` | Blockgrade y mantención. | Confirmar mantención y pipeline. |
| ADA | `var_mlp_ada_pi` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_pi.kql` | `fn_prd_mlp_ada_dom_pi_status` | `fn_prd_mlp_ada_lag_helpers` | `fn_src_mlp_systemlogs_all` | `mlp-prd-law-pisystem / ContainerAppSystemLogs_CL` | PI expected-vs-real y lag. | Revisar jobs PI y frescura. |
| ADA | `var_mlp_ada_plans` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_plans.kql` | `fn_prd_mlp_ada_dom_plans_status` | `fn_prd_mlp_ada_lag_helpers` | `fn_src_mlp_systemlogs_all`, `fn_src_mlp_ws_plans` | `mlp-prd-law-plans / ContainerAppSystemLogs_CL` | Plans y tablas `planes_*`. | Revisar jobs/lag Plans. |
| ADA | `var_mlp_ada_meteodata` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_meteodata.kql` | `fn_prd_mlp_ada_dom_meteodata_status` | `fn_prd_mlp_ada_lag_helpers` | `fn_src_mlp_systemlogs_all`, `fn_src_mlp_ws_meteo` | `mlp-prd-law-meteo / ContainerAppSystemLogs_CL` | Jobs meteo y lag. | Revisar logs Meteo. |
| ADA | `var_mlp_ada_kpi` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_kpi.kql` | `fn_prd_mlp_ada_dom_kpi_status` | `fn_prd_mlp_ada_jobs_status_detail`, `fn_prd_mlp_ada_kpi_alert_rows` | `fn_src_mlp_ws_ada`, `fn_src_mlp_ws_dataplatform` | ADA logs; `Logs_MLP_ADA_CL` | Jobs KPI y KPIs no esperados. | Revisar detalle KPI y excepciones. |
| ADA | `var_mlp_ada_alarm` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_alarm.kql` | `fn_prd_mlp_ada_dom_alarm_status` | `fn_prd_mlp_ada_jobs_status_detail` | `fn_src_mlp_ws_ada` | `mlp-prd-law-ada / ContainerAppConsoleLogs_CL` | Alarmas, incidentes largos, storage. | Revisar job06/job07 y errores. |
| ADA | `var_mlp_ada_front` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_front.kql` | `fn_prd_mlp_ada_dom_front_status` | No identificado en el repositorio | `fn_src_mlp_ws_ada` | `mlp-prd-law-ada / AppServiceConsoleLogs` | Errores Front/token. | Revisar app logs y autenticación. |
| ADA | `var_mlp_ada_jobs_detail` | `grafana_wrappers/prd/mlp/ada/var_mlp_ada_jobs_detail.kql` | No aplica | `fn_prd_mlp_ada_jobs_status_detail` | `fn_src_mlp_ws_ada` | `ContainerAppSystemLogs_CL` | Diagnóstico por job. | Usar para soporte N2. |
| ADA AMG | `var_mlp_ada_amg_*` | `grafana_wrappers/prd/mlp/ada_amg/*.kql` | `fn_prd_mlp_ada_amg_dom_*_status` | Pendiente de confirmar por dominio | Sources ADA compartidos | Pendiente de confirmar por dominio | Monitoreo ADA AMG. | Normalizar antes de producción. |
| NOTPII | `var_mlp_notpii_autoloader_dev` | `grafana_wrappers/prd/mlp/notpii/var_mlp_notpii_autoloader_dev.kql` | `fn_prd_mlp_notpii_dom_autoloader_dev_status` | `fn_prd_mlp_notpii_autoloader_alert` | `fn_src_mlp_ws_notpii_databricksjobs` | `ams-dev-dataplatform-laws / DatabricksJobs` | Autoloader DEV. | Revisar jobs Databricks DEV. |
| NOTPII | `var_mlp_notpii_autoloader_uat` | `grafana_wrappers/prd/mlp/notpii/var_mlp_notpii_autoloader_uat.kql` | `fn_prd_mlp_notpii_dom_autoloader_uat_status` | `fn_prd_mlp_notpii_autoloader_alert` | `fn_src_mlp_ws_notpii_databricksjobs` | `ams-uat-dataplatform-laws / DatabricksJobs` | Autoloader UAT. | Revisar jobs Databricks UAT. |
| NOTPII | `var_mlp_notpii_ingesta` | `grafana_wrappers/prd/mlp/notpii/var_mlp_notpii_ingesta.kql` | `fn_prd_mlp_notpii_dom_ingesta_status` | `fn_prd_mlp_notpii_ingesta_job04_alert` | `fn_src_mlp_ws_pisystem` | `mlp-prd-law-pisystem / ContainerApp*` | Ingesta job04. | Revisar warnings/errores PI System. |
| NOTPII | `var_mlp_notpii_difusion_global` | `grafana_wrappers/prd/mlp/notpii/var_mlp_notpii_difusion_global.kql` | `fn_prd_mlp_notpii_dom_global_status` | Dominios NOTPII | Sources NOTPII/PI | DatabricksJobs y PI logs | Global NOTPII. | Bajar a autoloader o ingesta. |
| SIROSAG | `var_mlp_sirosag_resumen` | `grafana_wrappers/prd/mlp/sirosag/var_mlp_sirosag_resumen.kql` | `fn_prd_mlp_ssag_dom_resumen_status` | `fn_prd_mlp_ssag_eval_ejecucion`, `fn_prd_mlp_ssag_eval_desfase`, `fn_prd_mlp_ssag_eval_desactualizacion` | `fn_src_mlp_ws_ssag`, `fn_src_mlp_ssag_systemlogs_all` | SSAG, Plans, PDMSAGI, PISystem logs | Ejecución, desfase y desactualización. | Revisar helper SIROSAG específico. |

## 33. Procedimiento real de despliegue

### 33.1 Prevalidación del repositorio

1. Revisar `git status` y confirmar alcance.
2. Ejecutar `check_conflict_markers.py`.
3. Ejecutar `validate_kql_references.py`.
4. Ejecutar `analyze_source_catalog.py` si cambian sources.
5. Registrar brechas aceptadas antes de continuar.

### 33.2 Orden de despliegue de funciones LAW

1. Sources.
2. Helpers cross-product.
3. Helpers de producto.
4. Domains de producto.
5. Queries Power Automate o consumidores externos.
6. Dashboard Grafana.

### 33.3 Validación de sources

- Probar cada source con rango corto.
- Confirmar conteo de filas y `max(TimeGenerated)`.
- Confirmar workspace/tabla correcta.

### 33.4 Validación de helpers

- Ejecutar helper con datos reales.
- Confirmar columnas de diagnóstico.
- Validar umbrales y excepciones.

### 33.5 Validación de domains

- Ejecutar domain individual.
- Confirmar `status/color/reason` o contrato actual.
- Confirmar que global coincide con dominios individuales.

### 33.6 Validación de wrappers

- Ejecutar wrapper en Grafana Explore.
- Confirmar macro de tiempo y columna proyectada.
- Si falla, comparar salida del domain.

### 33.7 Importación o actualización del dashboard en Grafana

- Respaldar dashboard actual.
- Importar o actualizar JSON.
- Confirmar datasource y UID.
- Confirmar permisos de visualización para soporte.

### 33.8 Validación de variables

- Ejecutar variables globales y por dominio.
- Confirmar formato `color/status` esperado.
- Verificar refresh y rango de tiempo.

### 33.9 Validación de paneles

- Revisar panel resumen y detalle.
- Confirmar render de colores.
- Confirmar que cada alerta tenga ruta de diagnóstico.

### 33.10 Pruebas antes de producción

- Probar `now-30m` y `now-6h`.
- Validar un flujo completo por producto: source → helper → domain → wrapper → panel.
- Comparar con modelo legacy si existe.
- Obtener aprobación del líder técnico y soporte.

### 33.11 Rollback o reversa

- Restaurar dashboard respaldado.
- Revertir wrapper o función LAW a versión anterior.
- Mantener copia de cuerpos KQL críticos.
- Documentar causa, impacto y siguiente acción.

## 34. Criterios de aceptación del traspaso

### 34.1 Criterios técnicos

- Sources, helpers, domains y wrappers críticos fueron probados.
- El validador está correcto o sus fallas están aceptadas formalmente.
- El dashboard renderiza variables sin errores críticos.
- Existe rollback documentado.

### 34.2 Criterios operativos

- Soporte sabe leer global, dominio y detalle.
- Soporte puede diferenciar falla real, falso positivo, permisos y falta de datos.
- Hay matriz de escalamiento o responsables pendientes identificados.
- El runbook fue ejercitado al menos una vez.

### 34.3 Criterios de documentación

- Matriz de trazabilidad completa disponible.
- Brechas y pendientes priorizados.
- Plantillas de panel y producto disponibles.
- Descripciones de panel listas para Grafana.

### 34.4 Criterios de capacitación

- Equipo completó ejercicios prácticos.
- Soporte N1 entiende interpretación visual.
- Soporte N2 entiende diagnóstico KQL por capas.
- Dudas pendientes quedaron registradas.

## 35. Ejercicios prácticos para capacitar al equipo

### 35.1 Dashboard sin datos

| Campo | Detalle |
|---|---|
| Objetivo | Diagnosticar panel vacío sin asumir caída de producto. |
| Contexto | El dashboard no muestra datos en uno o más paneles. |
| Pasos | Validar rango, datasource, variable, wrapper, source y permisos. |
| Resultado esperado | Identificar si el problema es rango, Grafana, permisos, source o emisión de logs. |
| Aprendizaje | Un panel vacío requiere diagnóstico por capas. |

### 35.2 Estado global en alerta

| Campo | Detalle |
|---|---|
| Objetivo | Bajar desde estado global hasta dominio/fuente. |
| Contexto | ADA, NOTPII o SIROSAG aparece en alerta global. |
| Pasos | Ejecutar global, identificar dominio, ejecutar domain/helper/source y registrar evidencia. |
| Resultado esperado | Dominio causante y fuente probable identificados. |
| Aprendizaje | El global prioriza; no reemplaza el diagnóstico. |

### 35.3 Wrapper con error de columna

| Campo | Detalle |
|---|---|
| Objetivo | Reconocer mismatch entre wrapper y salida del domain. |
| Contexto | Wrapper proyecta `color`, pero el domain devuelve `status`. |
| Pasos | Ejecutar domain, revisar columnas, comparar con wrapper y documentar ajuste. |
| Resultado esperado | Error aislado en contrato wrapper/domain. |
| Aprendizaje | Los contratos de salida deben ser estables. |

### 35.4 Usuario sin permisos

| Campo | Detalle |
|---|---|
| Objetivo | Separar incidente de permisos de incidente del producto. |
| Contexto | Un usuario ve error y otro ve datos. |
| Pasos | Comparar usuarios, validar datasource, validar acceso LAW y escalar a plataforma. |
| Resultado esperado | Problema RBAC confirmado o descartado. |
| Aprendizaje | Los permisos son parte del monitoreo operativo. |

### 35.5 Alerta falsa por ventana de tiempo

| Campo | Detalle |
|---|---|
| Objetivo | Evaluar impacto del rango temporal y latencia. |
| Contexto | Un dominio alerta en ventana corta y normaliza en ventana mayor. |
| Pasos | Probar `now-15m`, `now-6h`, revisar cadencia, expected-vs-real y umbrales. |
| Resultado esperado | Falso positivo identificado y documentado. |
| Aprendizaje | La ventana de tiempo debe alinearse con cadencias reales. |

## 36. Contrato estándar recomendado para funciones domain

| Campo | Por qué es importante para soporte |
|---|---|
| `domain` | Permite identificar el dominio operativo en tablas globales y reportes. |
| `status` | Define la decisión principal: normal, alerta o advertencia. |
| `color` | Permite render visual directo en Grafana sin lógica duplicada. |
| `reason` | Explica causa de estado y reduce tiempo de diagnóstico. |
| `startTime` | Deja explícita la ventana evaluada. |
| `endTime` | Permite reproducir la evaluación. |
| `evidence` | Entrega datos de respaldo: job, conteos, tabla, timestamp o error. |
| `severity` | Permite priorizar atención y escalar correctamente. |

## 37. Ruta recomendada de lectura para una persona nueva

1. Leer el resumen ejecutivo de este documento.
2. Leer el resumen ejecutivo de `readme_codex.md`.
3. Revisar matriz de trazabilidad completa.
4. Revisar estado actual, modelo recomendado y brechas.
5. Leer procedimiento real de despliegue.
6. Ejecutar ejercicios prácticos con un mentor.
7. Revisar anexos de comandos y descripciones de panel.

## 38. Anexo con comandos de validación

| Comando | Qué valida | Qué hacer si falla |
|---|---|---|
| `python refactor_ada_optimized/validate_kql_references.py` | Referencias KQL, wrappers, funciones requeridas, mirrors body-only y layout. | Corregir errores o registrar aceptación formal de brecha. |
| `python refactor_ada_optimized/check_conflict_markers.py` | Marcadores de conflicto Git. | Resolver conflictos antes de PR/despliegue. |
| `python refactor_ada_optimized/analyze_source_catalog.py` | Catálogo de sources, consumidores y workspaces. | Revisar impacto y actualizar documentación de fuentes; si devuelve `0` sources, validar alcance/ruta esperada por el script. |
| `python refactor_ada_optimized/resolve_required_resources.py <function_name>` | Recursos requeridos por una función específica. | Ejecutar con un nombre real; si falla, confirmar definición KQL y extensión `.kql`. |

## 39. Anexo con descripciones breves listas para pegar en paneles de Grafana

| Panel/variable | Descripción breve sugerida |
|---|---|
| ADA Global | Estado global ADA. Si está en alerta, revisar dominios ADA y bajar a detalle. |
| ADA Dispatch | Valida lag Dispatch, señal NRT y job17. Revisar logs ADA y tablas Dispatch ante alerta. |
| ADA Drillit | Valida pipeline y frescura Drillit. Revisar AzureDiagnostics y tablas `drillit_*`. |
| ADA Blockgrade | Valida pipeline, lag y mantención Blockgrade. Confirmar condición operacional. |
| ADA PI | Valida ejecución y frescura PI. Revisar jobs PI y `pisystem_interpolated`. |
| ADA Plans | Valida ejecución y frescura de planes. Revisar logs Plans y tablas `planes_*`. |
| ADA KPI | Valida jobs KPI y KPIs no esperados. Revisar detalle y excepciones. |
| ADA Alarmas | Valida jobs de alarmas, incidentes largos y storage. Revisar job06/job07. |
| ADA Front | Valida errores de aplicación/token. Revisar `AppServiceConsoleLogs`. |
| NOTPII Autoloader | Valida jobs Databricks DEV/UAT. Revisar failed/running/cancelled. |
| NOTPII Ingesta | Valida job04 PI System. Revisar errores, warnings y ejecución. |
| SIROSAG Resumen | Valida ejecución, desfase y desactualización. Revisar helpers SIROSAG. |
