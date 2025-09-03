from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import uvicorn
from typing import List, Optional
import os
from contextlib import asynccontextmanager
import requests
import gdown

app = FastAPI(title="Essalud API", description="API para consultar datos de Essalud", version="1.0.0")

# Modelo de datos para la respuesta
class EssaludRecord(BaseModel):
    Edad: int
    Sexo: str
    Nacimiento: str
    Autogenerado: str
    Paterno: str
    Materno: str
    Nombres: str
    Tipotrabajador: int
    Ingreso: int
    Tipoasegurado: int
    Alta: int
    Baja: int
    Situacion: str
    Devengue: int
    UBIGEO: str
    Tipodocumento: float
    documento: str
    DomicilioEss: str
    UBIGEO2: str
    Departamento: str
    Provincia: str
    Distrito: str
    RUC: str
    E_nombre: str
    E_direccion: str
    E_numero: str
    E_ubigeo: str
    E_departamento: str
    E_provincia: str
    E_distrito: str
    e_giro: str
    E_telefono_1: str
    E_telefono_2: str
    e_tele1: str
    e_tele2: str
    FechInicioActivX: str
    Top2011: Optional[float]
    Planilla: str
    TipoFamiliar: str
    Hijos: int
    telefonocasa: Optional[str]

# Variable global para almacenar los datos
df_essalud = None

def download_data_from_drive():
    """Descarga los datos desde Google Drive"""
    file_id = "1Ix1bGOI3SZeN3RWbkwRWIQhp5-lwiSbX"
    url = f"https://drive.google.com/uc?id={file_id}"
    output_file = "Peru_social_security_Essalud.txt"
    
    try:
        if not os.path.exists(output_file):
            print("Descargando datos desde Google Drive...")
            gdown.download(url, output_file, quiet=False)
            print("Datos descargados exitosamente")
        else:
            print("Archivo de datos ya existe, usando archivo local")
        return True
    except Exception as e:
        print(f"Error al descargar los datos: {e}")
        return False

def load_data():
    """Carga los datos del archivo CSV"""
    global df_essalud
    try:
        # Primero intentar descargar los datos
        if not download_data_from_drive():
            return False
            
        # Leer el archivo CSV con configuración para evitar warnings
        df_essalud = pd.read_csv('Peru_social_security_Essalud.txt', low_memory=False)
        print(f"Datos cargados: {len(df_essalud)} registros")
        return True
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Carga los datos al iniciar la aplicación"""
    if not load_data():
        raise Exception("No se pudieron cargar los datos de Essalud")

@app.get("/")
async def root():
    return {"message": "API Essalud - Endpoints disponibles: /essalud/dni/{dni}, /essalud/nombres/{nombres}, /essalud/planilla/{planilla}"}

@app.get("/essalud/dni/{dni}")
async def get_by_dni(dni: str):
    """Consulta por número de documento (DNI)"""
    if df_essalud is None:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    # Buscar por documento (convertir a string para comparación)
    result = df_essalud[df_essalud['documento'].astype(str) == str(dni)]
    
    if result.empty:
        raise HTTPException(status_code=404, detail=f"No se encontró registro con DNI: {dni}")
    
    # Convertir a lista de diccionarios y limpiar valores NaN
    records = result.to_dict('records')
    # Limpiar valores NaN para que sean JSON serializables
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    return {"total": len(records), "data": records}

@app.get("/essalud/nombres/{nombres}")
async def get_by_nombres(nombres: str):
    """Consulta por nombres (búsqueda parcial)"""
    if df_essalud is None:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    # Búsqueda parcial en nombres (case insensitive)
    nombres_upper = nombres.upper()
    result = df_essalud[
        df_essalud['Nombres'].str.upper().str.contains(nombres_upper, na=False) |
        df_essalud['Paterno'].str.upper().str.contains(nombres_upper, na=False) |
        df_essalud['Materno'].str.upper().str.contains(nombres_upper, na=False)
    ]
    
    if result.empty:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros con nombres que contengan: {nombres}")
    
    # Convertir a lista de diccionarios y limpiar valores NaN
    records = result.to_dict('records')
    # Limpiar valores NaN para que sean JSON serializables
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    return {"total": len(records), "data": records}

@app.get("/essalud/planilla/{planilla}")
async def get_by_planilla(planilla: str):
    """Consulta por número de planilla"""
    if df_essalud is None:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    # Buscar por planilla (convertir a string para comparación)
    result = df_essalud[df_essalud['Planilla'].astype(str) == str(planilla)]
    
    if result.empty:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros con planilla: {planilla}")
    
    # Convertir a lista de diccionarios y limpiar valores NaN
    records = result.to_dict('records')
    # Limpiar valores NaN para que sean JSON serializables
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
    return {"total": len(records), "data": records}

@app.get("/essalud/stats")
async def get_stats():
    """Obtiene estadísticas generales de la base de datos"""
    if df_essalud is None:
        raise HTTPException(status_code=500, detail="Datos no cargados")
    
    stats = {
        "total_registros": len(df_essalud),
        "departamentos": df_essalud['Departamento'].value_counts().to_dict(),
        "situacion": df_essalud['Situacion'].value_counts().to_dict(),
        "sexo": df_essalud['Sexo'].value_counts().to_dict()
    }
    
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
