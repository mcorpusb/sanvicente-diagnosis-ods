# Del taller al dashboard · Diagnosis IA y ODS

Dashboard web para el proyecto interdepartamental de Automoción e Informática.

## Flujo de datos

Informes de diagnosis → Gemini Gem → CSV → Google Sheets → Apps Script → `datos_dashboard` → GitHub Pages.

## Versión 3

Esta versión mejora la lectura y la escalabilidad del dashboard:

- Filtro por vehículo.
- Filtro por severidad.
- Buscador por vehículo, DTC u observación.
- Botón para limpiar filtros.
- Tarjetas compactas que muestran solo los primeros DTC.
- Tabla técnica con el listado completo.
- Diagnóstico interpretado por vehículo.
- Bloque de calidad del dato.
- Fuente indicada como Google Sheets conectado.
- Orden visual por severidad y número de DTC.

## Fuente de datos

La página lee directamente la pestaña `datos_dashboard` de Google Sheets:

https://docs.google.com/spreadsheets/d/1pgLQ5UucYZVDPbQIv2LD0wMxMb7P4B179nA3Ed3IQc4/gviz/tq?tqx=out:csv&sheet=datos_dashboard
