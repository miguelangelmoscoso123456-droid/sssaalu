from fastapi import FastAPI, HTTPException
import uvicorn
import os
import pandas as pd
import gdown
from contextlib import asynccontextmanager
from typing import Optional

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
            print(f"URL: {url}")
            gdown.download(url, output_file, quiet=False)
            print("Datos descargados exitosamente")
        else:
            print("Archivo de datos ya existe, usando archivo local")
        return True
    except Exception as e:
        print(f"Error al descargar los datos: {e}")
        print("Continuando sin datos...")
        return False

def load_data():
    """Carga los datos del archivo CSV"""
    global df_essalud
    try:
        # Primero intentar descargar los datos
        download_data_from_drive()
            
        # Leer el archivo CSV con configuración para evitar warnings
        if os.path.exists('Peru_social_security_Essalud.txt'):
            print("Cargando datos en memoria...")
            df_essalud = pd.read_csv('Peru_social_security_Essalud.txt', low_memory=False)
            print(f"Datos cargados: {len(df_essalud)} registros")
        else:
            print("Archivo de datos no encontrado, API funcionará sin datos")
            df_essalud = None
        return True
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        print("API funcionará sin datos")
        df_essalud = None
        return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    # Startup
    print("Iniciando aplicación Essalud API...")
    load_data()
    print("Aplicación iniciada correctamente")
    yield
    # Shutdown (si necesitas limpiar algo)

app = FastAPI(
    title="Essalud API", 
    description="API para consultar datos de Essalud", 
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "API Essalud funcionando correctamente",
        "status": "ok",
        "data_loaded": df_essalud is not None,
        "total_records": len(df_essalud) if df_essalud is not None else 0,
        "endpoints": [
            "/essalud/dni/{dni}",
            "/essalud/nombres/{nombres}",
            "/essalud/planilla/{planilla}",
            "/health",
            "/essalud/stats"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "message": "API funcionando correctamente",
        "data_loaded": df_essalud is not None,
        "total_records": len(df_essalud) if df_essalud is not None else 0
    }

@app.get("/essalud/dni/{dni}")
async def get_by_dni(dni: str):
    """Consulta por número de documento (DNI)"""
    if df_essalud is None:
        raise HTTPException(status_code=503, detail="Datos no cargados aún")
    
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
        raise HTTPException(status_code=503, detail="Datos no cargados aún")
    
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
        raise HTTPException(status_code=503, detail="Datos no cargados aún")
    
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
        raise HTTPException(status_code=503, detail="Datos no cargados aún")
    
    stats = {
        "total_registros": len(df_essalud),
        "departamentos": df_essalud['Departamento'].value_counts().to_dict(),
        "situacion": df_essalud['Situacion'].value_counts().to_dict(),
        "sexo": df_essalud['Sexo'].value_counts().to_dict()
    }
    
    return stats

# La aplicación se ejecuta desde main.py
