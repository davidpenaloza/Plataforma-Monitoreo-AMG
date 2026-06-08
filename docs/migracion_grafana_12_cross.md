# Preparación del dashboard CROSS para Grafana 12

## Decisión de compatibilidad

El dashboard continúa usando el modelo JSON clásico. Grafana 12 mantiene compatibilidad con este modelo, mientras que el dashboard schema v2 y los layouts dinámicos no son necesarios para esta migración. No se debe convertir el archivo a schema v2 durante la actualización inicial.

## Ajustes aplicados

- Todas las variables `query` declaran explícitamente el datasource nativo Azure Monitor.
- El UID `eetf6c2xjxukgd` cumple el formato estricto exigido por Grafana 12.
- Los paneles visuales siguen siendo paneles `text` React en modo `html`; no se utilizan paneles Angular retirados.
- El HTML conserva estilos inline y no utiliza bloques `<style>`, de acuerdo con el comportamiento comprobado en Azure Managed Grafana.
- El layout, las consultas KQL, los recursos Azure y los enlaces no se modifican para la migración.

## Dependencia de plataforma

El dashboard requiere que la instancia mantenga habilitada la configuración equivalente a `disable_sanitize_html`. Esta opción pertenece a la instancia de Grafana y no puede declararse dentro del JSON del dashboard. Debe verificarse en el ambiente Grafana 12 antes del cambio productivo.

## Procedimiento de migración recomendado

1. Exportar y respaldar el dashboard actual desde la instancia de origen.
2. Confirmar que el datasource Azure Monitor de destino conserva el UID `eetf6c2xjxukgd`.
3. Ejecutar el validador estático:

   ```bash
   python3 refactor_ada_optimized/validate_grafana12_dashboard.py
   ```

4. Importar el JSON en una instancia Grafana 12 de prueba.
5. Confirmar que los paneles Text renderizan HTML y no muestran etiquetas como texto.
6. Validar una variable por cada workspace/ambiente utilizado: UAT, DEV y PRD.
7. Comprobar los enlaces a dashboards secundarios.
8. Guardar el dashboard desde Grafana 12 y exportar una copia posterior a la migración. Grafana actualizará los metadatos de schema y plugin que correspondan a la versión instalada.

## Qué no debe modificarse manualmente

- `schemaVersion`: debe actualizarlo Grafana al guardar el dashboard.
- `pluginVersion`: debe reflejar la versión que Grafana asigna después de importar/guardar.
- El dashboard schema v2: no habilitarlo como parte de esta migración inicial.

## Criterios de aceptación

- El dashboard importa sin errores.
- Las 46 variables Azure Log Analytics resuelven usando el datasource esperado.
- Los 16 paneles Text conservan el diseño HTML original.
- No aparecen paneles migrados desde Angular.
- Los colores dinámicos y enlaces funcionan igual que antes de la migración.
