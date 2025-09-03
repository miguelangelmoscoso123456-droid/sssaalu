# API Essalud

API REST para consultar la base de datos de Essalud del Perú.

## Instalación Local

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python main.py
```

La API estará disponible en: `http://127.0.0.1:8000`

**Nota:** Los datos se descargan automáticamente desde Google Drive en el primer inicio.

## Despliegue en Railway

1. Conecta tu repositorio de GitHub a Railway
2. Railway detectará automáticamente que es una aplicación Python
3. Los datos se descargarán automáticamente desde Google Drive durante el despliegue
4. La API estará disponible en la URL proporcionada por Railway

## Endpoints

### 1. Consulta por DNI
```
GET /essalud/dni/{dni}
```
Ejemplo: `http://127.0.0.1:8000/essalud/dni/00419428`

### 2. Consulta por Nombres
```
GET /essalud/nombres/{nombres}
```
Ejemplo: `http://127.0.0.1:8000/essalud/nombres/ROSA`
- Busca en nombres, apellido paterno y materno
- Búsqueda parcial (case insensitive)

### 3. Consulta por Planilla
```
GET /essalud/planilla/{planilla}
```
Ejemplo: `http://127.0.0.1:8000/essalud/planilla/6498`

### 4. Estadísticas
```
GET /essalud/stats
```
Obtiene estadísticas generales de la base de datos.

## Documentación

Una vez que la API esté ejecutándose, puedes acceder a la documentación interactiva en:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Respuesta de ejemplo

```json
{
  "total": 1,
  "data": [
    {
      "Edad": 65,
      "Sexo": "F",
      "Nacimiento": "12-09-46",
      "Autogenerado": "4609120VGGRR008",
      "Paterno": "VARGAS",
      "Materno": "GUARDIA",
      "Nombres": "ROSA",
      "Tipotrabajador": 5,
      "Ingreso": 910,
      "Tipoasegurado": 3,
      "Alta": 7503,
      "Baja": 0,
      "Situacion": "P",
      "Devengue": 201105,
      "UBIGEO": "230103.0",
      "Tipodocumento": 1.0,
      "documento": "00419428",
      "DomicilioEss": "S/NOMBRE            S/N",
      "UBIGEO2": "230103.0",
      "Departamento": "TACNA",
      "Provincia": "TACNA",
      "Distrito": "CALANA",
      "RUC": "20325722941",
      "E_nombre": "DIRECCION REGIONAL DE EDUCACION TACNA",
      "E_direccion": "A CALANA",
      "E_numero": "-",
      "E_ubigeo": "230103",
      "E_departamento": "TACNA",
      "E_provincia": "TACNA",
      "E_distrito": "CALANA",
      "e_giro": "SERVIC. AUXIL.PARA ADMINIST.PUBLICA.",
      "E_telefono_1": "247179",
      "E_telefono_2": "245686",
      "e_tele1": "",
      "e_tele2": "",
      "FechInicioActivX": "15/4/1989 00:00:00",
      "Top2011": null,
      "Planilla": "6498",
      "TipoFamiliar": "",
      "Hijos": 0,
      "telefonocasa": "52315573.0"
    }
  ]
}
```
