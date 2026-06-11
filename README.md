# Dashboard de Diagnosis de Vehículos con IA Generativa

> Proyecto interdepartamental de **Formación Profesional** · IES San Vicente  
> Tecnologías: Python · Flask · Google Gemini · Google Sheets · ODS

---

## ¿Qué es este proyecto?

Un dashboard web para que los alumnos del ciclo de **Electromecánica de Vehículos**
puedan registrar diagnósticos de automóviles usando códigos de avería OBD-II.
La aplicación envía los datos a **Google Gemini** para obtener un diagnóstico con IA
generativa, almacena el historial en **Google Sheets** y permite exportar el registro
completo como hoja de cálculo en formato **ODS** (OpenDocument Spreadsheet, compatible
con LibreOffice Calc).

```
Usuario / Alumno
      │
      ▼
┌─────────────────────────────────┐
│  Dashboard Web  (Flask + HTML)  │
│  · Formulario de diagnóstico    │
│  · Tabla de historial           │
│  · Botón de exportación ODS     │
└──────────┬──────────────────────┘
           │
    ┌──────┼─────────┐
    ▼      ▼         ▼
 Gemini  Google    Archivo
  API    Sheets     .ods
```

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 🤖 **Diagnóstico con IA** | Envía marca, modelo, año, km, códigos OBD-II y síntomas a Google Gemini y obtiene diagnóstico + recomendaciones en español |
| 📊 **Google Sheets** | Cada diagnóstico se guarda automáticamente en una hoja de cálculo compartida |
| ⬇️ **Exportar ODS** | Descarga todo el historial en formato ODS para abrirlo con LibreOffice Calc |
| 📋 **Historial** | Tabla en tiempo real con todos los diagnósticos almacenados |
| 🔧 **Modo demo** | Si no hay clave de API configurada, la aplicación funciona en modo demo |

---

## Estructura del proyecto

```
sanvicente-diagnosis-ods/
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias Python
├── .env.example               # Variables de entorno de ejemplo
├── app/
│   ├── __init__.py            # Application factory (create_app)
│   ├── models/
│   │   └── diagnosis.py       # Modelo DiagnosisRecord
│   ├── routes/
│   │   ├── diagnosis.py       # GET / · POST /api/diagnose · GET /api/records
│   │   └── export.py          # GET /api/export/ods
│   ├── services/
│   │   ├── ai_service.py      # Integración con Google Gemini
│   │   ├── sheets_service.py  # Integración con Google Sheets API
│   │   └── ods_service.py     # Generación de ficheros ODS
│   └── templates/
│       ├── base.html
│       └── index.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── tests/
    ├── test_diagnosis_model.py
    ├── test_ai_service.py
    ├── test_ods_service.py
    └── test_routes.py
```

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/mcorpusb/sanvicente-diagnosis-ods.git
cd sanvicente-diagnosis-ods
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el fichero `.env` y rellena:

| Variable | Descripción |
|---|---|
| `GEMINI_API_KEY` | Clave de API de Google AI Studio (https://aistudio.google.com/app/apikey) |
| `SPREADSHEET_ID` | ID de la hoja de Google Sheets donde se guardan los diagnósticos |
| `SHEET_NAME` | Nombre de la pestaña dentro del documento (por defecto: `Diagnosticos`) |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Ruta al JSON de la cuenta de servicio de Google Cloud |
| `SECRET_KEY` | Clave secreta para Flask (genera con `python -c "import secrets; print(secrets.token_hex())"`) |

### 4. Configurar Google Sheets (cuenta de servicio)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto.
2. Activa las APIs: **Google Sheets API** y **Google Drive API**.
3. Crea una **Cuenta de Servicio** y descarga el fichero JSON de credenciales.
4. Guarda el fichero como `service_account.json` en la raíz del proyecto (está en `.gitignore`).
5. Comparte la hoja de Google Sheets con el correo de la cuenta de servicio (dar permisos de **Editor**).

### 5. Iniciar la aplicación

```bash
python main.py
```

Abre el navegador en: **http://localhost:5000**

---

## Ejecutar los tests

```bash
python -m pytest tests/ -v
```

---

## API REST

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Dashboard principal |
| `POST` | `/api/diagnose` | Crear un nuevo diagnóstico (JSON) |
| `GET` | `/api/records` | Obtener todos los registros (JSON) |
| `GET` | `/api/export/ods` | Descargar todos los registros en formato ODS |

### Ejemplo: POST `/api/diagnose`

```json
{
  "vehicle_id": "1234 ABC",
  "make": "Toyota",
  "model": "Corolla",
  "year": 2019,
  "mileage": 95000,
  "fault_codes": "P0301, P0420",
  "symptoms": "Tirones en aceleración, consumo elevado",
  "technician": "María García"
}
```

---

## Departamentos implicados (FP interdepartamental)

| Departamento | Aportación |
|---|---|
| **Electromecánica de Vehículos** | Conocimiento técnico de códigos OBD-II y diagnóstico |
| **Informática** | Desarrollo de la aplicación web y APIs |
| **Administración** | Uso de hojas de cálculo y exportación ODS |

---

## Licencia

MIT — Proyecto educativo IES San Vicente