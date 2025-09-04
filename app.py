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
    url = "https://drive.usercontent.google.com/download?id=1Ix1bGOI3SZeN3RWbkwRWIQhp5-lwiSbX&export=download&authuser=0&confirm=t&uuid=24bccadc-2398-44c9-9bfe-fbac8de47573&at=AN8xHorWwCrlVg0hsh--dvAleN21%3A1756948900144"
    output_file = "Peru_social_security_Essalud.txt"
    
    try:
        if not os.path.exists(output_file):
            print("Descargando datos desde Google Drive...")
            print(f"URL: {url}")
            
            # Usar gdown con el enlace directo público
            try:
                gdown.download(url, output_file, quiet=False)
                print("Datos descargados exitosamente con gdown")
            except Exception as gdown_error:
                print(f"Gdown falló: {gdown_error}")
                print("Intentando con requests...")
                
                # Fallback con requests
                import requests
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print("Datos descargados exitosamente con requests")
        else:
            print("Archivo de datos ya existe, usando archivo local")
        
        # Verificar que el archivo no sea HTML
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                if first_line.startswith('<!DOCTYPE') or first_line.startswith('<html'):
                    print("ERROR: El archivo descargado es HTML, no CSV. El enlace requiere autenticación.")
                    os.remove(output_file)  # Eliminar archivo HTML
                    return False
        
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
        if not download_data_from_drive():
            print("No se pudieron descargar los datos, continuando sin datos")
            df_essalud = None
            return True
            
        # Leer el archivo CSV con configuración para manejar inconsistencias
        if os.path.exists('Peru_social_security_Essalud.txt'):
            print("Cargando datos en memoria...")
            try:
                # Configuración más robusta para archivos grandes
                df_essalud = pd.read_csv(
                    'Peru_social_security_Essalud.txt', 
                    on_bad_lines='skip',
                    encoding='utf-8',
                    sep=',',
                    quotechar='"',
                    skipinitialspace=True,
                    engine='python',  # Usar motor Python más permisivo
                    nrows=100000  # Limitar a 100k registros inicialmente
                )
                
                print(f"Datos cargados: {len(df_essalud)} registros")
                print(f"Columnas disponibles: {list(df_essalud.columns)}")
                
                # Verificar que las columnas sean válidas
                if len(df_essalud.columns) < 5:
                    print("ERROR: Muy pocas columnas detectadas, posible problema con el archivo")
                    df_essalud = None
                    return True
                    
            except Exception as csv_error:
                print(f"Error al cargar CSV: {csv_error}")
                print("Intentando configuración alternativa...")
                try:
                    # Configuración alternativa más permisiva
                    df_essalud = pd.read_csv(
                        'Peru_social_security_Essalud.txt', 
                        on_bad_lines='skip',
                        encoding='utf-8',
                        sep=',',
                        quotechar='"',
                        skipinitialspace=True,
                        engine='python',
                        nrows=50000  # Limitar aún más
                    )
                    print(f"Datos cargados con configuración alternativa: {len(df_essalud)} registros")
                    print(f"Columnas disponibles: {list(df_essalud.columns)}")
                except Exception as alt_error:
                    print(f"Error con configuración alternativa: {alt_error}")
                    print("No se pudieron cargar los datos")
                    df_essalud = None
                    return True
        else:
            print("Archivo de datos no encontrado, API funcionará sin datos")
            df_essalud = None
            return True
        return True
    except Exception as e:
        print(f"Error general al cargar los datos: {e}")
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
    
    # Verificar si existe la columna 'documento'
    if 'documento' not in df_essalud.columns:
        # Buscar columnas que puedan contener el DNI
        possible_dni_columns = [col for col in df_essalud.columns if 'documento' in col.lower() or 'dni' in col.lower()]
        if not possible_dni_columns:
            raise HTTPException(status_code=500, detail=f"Columna 'documento' no encontrada. Columnas disponibles: {list(df_essalud.columns)}")
        # Usar la primera columna que contenga 'documento' o 'dni'
        dni_column = possible_dni_columns[0]
    else:
        dni_column = 'documento'
    
    # Buscar por documento (convertir a string para comparación)
    result = df_essalud[df_essalud[dni_column].astype(str) == str(dni)]
    
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
    """Consulta por nombres (búsqueda parcial y completa)"""
    if df_essalud is None:
        raise HTTPException(status_code=503, detail="Datos no cargados aún")
    
    # Buscar columnas de nombres
    name_columns = []
    for col in df_essalud.columns:
        if any(name in col.lower() for name in ['nombre', 'paterno', 'materno', 'apellido']):
            name_columns.append(col)
    
    if not name_columns:
        raise HTTPException(status_code=500, detail=f"Columnas de nombres no encontradas. Columnas disponibles: {list(df_essalud.columns)}")
    
    # Limpiar y preparar el término de búsqueda
    nombres_clean = nombres.replace('_', ' ').replace('-', ' ').strip().upper()
    search_terms = [term.strip() for term in nombres_clean.split() if term.strip()]
    
    # Búsqueda mejorada: buscar cada término en cualquier columna de nombres
    conditions = []
    
    for term in search_terms:
        term_conditions = []
        for col in name_columns:
            term_conditions.append(df_essalud[col].str.upper().str.contains(term, na=False))
        # Al menos una columna debe contener este término
        conditions.append(pd.concat(term_conditions, axis=1).any(axis=1))
    
    # Todos los términos deben estar presentes
    if conditions:
        result = df_essalud[pd.concat(conditions, axis=1).all(axis=1)]
    else:
        result = df_essalud.iloc[0:0]  # DataFrame vacío
    
    if result.empty:
        # Si no encuentra con búsqueda completa, intentar búsqueda parcial
        nombres_upper = nombres_clean
        partial_conditions = []
        for col in name_columns:
            partial_conditions.append(df_essalud[col].str.upper().str.contains(nombres_upper, na=False))
        
        result = df_essalud[pd.concat(partial_conditions, axis=1).any(axis=1)]
    
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
    
    # Buscar columna de planilla
    planilla_columns = [col for col in df_essalud.columns if 'planilla' in col.lower()]
    if not planilla_columns:
        raise HTTPException(status_code=500, detail=f"Columna 'planilla' no encontrada. Columnas disponibles: {list(df_essalud.columns)}")
    
    planilla_column = planilla_columns[0]
    
    # Buscar por planilla (convertir a string para comparación)
    result = df_essalud[df_essalud[planilla_column].astype(str) == str(planilla)]
    
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

@app.get("/essalud/info")
async def get_info():
    """Información sobre el estado de la API"""
    info = {
        "status": "API funcionando",
        "data_loaded": df_essalud is not None,
        "total_records": len(df_essalud) if df_essalud is not None else 0,
        "message": "Archivo de Google Drive configurado correctamente",
        "endpoints": [
            "/essalud/dni/{dni} - Búsqueda por DNI",
            "/essalud/nombres/{nombres} - Búsqueda por nombres",
            "/essalud/planilla/{planilla} - Búsqueda por planilla",
            "/essalud/stats - Estadísticas de la base de datos",
            "/essalud/info - Información de la API"
        ]
    }
    
    if df_essalud is not None:
        info["columns"] = list(df_essalud.columns)
        info["sample_data"] = df_essalud.head(1).to_dict('records')[0] if len(df_essalud) > 0 else None
    
    return info

# La aplicación se ejecuta desde main.py
