# Dashboard Diagnosis IA · ODS

Dashboard web para el proyecto interdepartamental de Automoción e Informática.

## Flujo de datos

Informes de diagnosis → Gemini Gem → CSV → Google Sheets → Apps Script → `datos_dashboard` → GitHub Pages.

## Instalación en GitHub Pages

1. Crea un repositorio nuevo o una carpeta nueva dentro del repositorio.
2. Sube `index.html`.
3. Activa GitHub Pages desde Settings → Pages.
4. Abre la URL pública del dashboard.

## Fuente de datos

El dashboard lee directamente esta hoja de Google Sheets:

https://docs.google.com/spreadsheets/d/1pgLQ5UucYZVDPbQIv2LD0wMxMb7P4B179nA3Ed3IQc4/gviz/tq?tqx=out:csv&sheet=datos_dashboard

La hoja debe estar compartida como:
`Cualquier persona con el enlace → Lector`.

## Contenido

- KPIs principales.
- Tarjetas por vehículo.
- Filtro por severidad.
- Buscador por vehículo, DTC u observación.
- Tabla técnica.
- Relación con ODS 4, 9, 12 y 13.
