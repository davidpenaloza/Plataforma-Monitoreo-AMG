# Estándar de funciones KQL

## Objetivo

Definir reglas mínimas para crear funciones KQL mantenibles, testeables y consumibles por Grafana, Power Automate y soporte.

## Convenciones para crear funciones

1. Una función debe tener un propósito único: fuente, helper, dominio o wrapper.
2. La firma debe ser explícita y estable.
3. Toda función que consulte datos temporales debe recibir `startTime:datetime` y `endTime:datetime`.
4. Las funciones de dominio deben tener una salida homogénea para paneles y soporte.
5. Los wrappers de Grafana no deben contener lógica compleja ni umbrales nuevos.
6. No incluir secretos, tokens, credenciales ni IDs sensibles en documentación o ejemplos.

## Estructura esperada

```kusto
let fn_prd_mlp_<producto>_dom_<dominio>_status = (startTime:datetime, endTime:datetime) {
  let base = ...;
  let metricas = ...;
  let status = ...;
  print
    producto = "<producto>",
    dominio = "<dominio>",
    status = status,
    color = fn_mon_status_to_color(status)
};
```

Para sources:

```kusto
let fn_src_mlp_ws_<fuente> = (sourceType:string, startTime:datetime, endTime:datetime) {
  <tabla o union>
  | where TimeGenerated between (startTime .. endTime)
  | where source_table == sourceType or sourceType == "<tabla>"
};
```

## Parámetros estándar

| Parámetro | Tipo | Uso |
|---|---|---|
| `startTime` | `datetime` | Inicio de ventana de evaluación. |
| `endTime` | `datetime` | Fin de ventana de evaluación. |
| `sourceType` o `tableName` | `string` | Selección de tabla o tipo de fuente en sources. |
| `env` | `string` | Ambiente lógico cuando una misma función cubre DEV/UAT/PRD. |
| `tables` | `dynamic` | Lista de tablas o entidades para evaluación masiva. |
| Parámetros opcionales con default | Varios | Solo para helpers genéricos y con valores seguros. |

## Manejo de `startTime`/`endTime`

- Usar siempre `where TimeGenerated between (startTime .. endTime)` o equivalente.
- Evitar `ago()` dentro de funciones de dominio si la función ya recibe ventana temporal; usarlo solo en pruebas manuales.
- Si una regla necesita ampliar ventana, hacerlo explícito y documentar la razón, por ejemplo `startTime - 4h` para contar ejecuciones esperadas.
- En Grafana, usar `bin($__timeFrom, 1m)` y `bin($__timeTo, 1m)` para entregar datetimes alineados.

## Manejo de ambientes

- El ambiente debe quedar en el path y/o nombre cuando sea parte del contrato: `prd`, `dev`, `uat`.
- Si una función acepta `env`, validar valores permitidos y documentarlos.
- No mezclar criterios DEV/UAT/PRD en una misma función si cambian fuentes, umbrales o semántica.
- Si un ambiente no está confirmado en el repositorio, documentarlo como **Por validar**.

## Buenas prácticas

- Proyectar solo columnas necesarias para reducir costo y ruido.
- Usar `union isfuzzy=true` solo cuando se entiende el impacto ante tablas ausentes.
- Encapsular umbrales en helpers o datatables versionadas.
- Usar helpers cross-producto para transformar estados a colores.
- Evitar duplicar listas de jobs en múltiples dominios.
- Nombrar variables internas con intención: `expected_*`, `real_*`, `*_alert`, `lag`, `status`.
- Mantener ejemplos de uso junto al catálogo o guía de implementación.

## Errores a evitar

- Crear wrappers con lógica de negocio que no exista en funciones LAW.
- Usar rangos temporales fijos que ignoren el selector de tiempo de Grafana.
- Depender de columnas no proyectadas en sources agregadas.
- Hacer `toscalar()` sobre resultados que puedan devolver múltiples filas sin agregación determinística.
- Usar `union` sin normalizar columnas esperadas.
- Crear funciones específicas con nombres que parezcan cross-producto.
- Documentar rutas productivas sensibles o IDs completos.

## Criterios cross-producto vs específico

| Criterio | Cross-producto | Específico |
|---|---|---|
| Depende de tablas concretas | No | Sí |
| Depende de jobs/pipelines de un producto | No | Sí |
| Convierte `OK/WARN/ALERT` a color | Sí | No |
| Evalúa lag de un set de tablas particular | Solo si recibe configuración genérica | Sí |
| Agrega estado global por colores | Sí | No |
| Define umbrales funcionales de dominio | No, salvo estándar corporativo | Sí |
