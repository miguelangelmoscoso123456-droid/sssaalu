from fastapi import FastAPI, HTTPException
import uvicorn
import os

app = FastAPI(title="Essalud API", description="API para consultar datos de Essalud", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "API Essalud funcionando correctamente",
        "status": "ok",
        "endpoints": [
            "/essalud/dni/{dni}",
            "/essalud/nombres/{nombres}",
            "/essalud/planilla/{planilla}",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}

@app.get("/essalud/dni/{dni}")
async def get_by_dni(dni: str):
    """Consulta por número de documento (DNI)"""
    return {
        "message": "Endpoint funcionando",
        "dni": dni,
        "note": "Datos no cargados aún - descargando en segundo plano"
    }

@app.get("/essalud/nombres/{nombres}")
async def get_by_nombres(nombres: str):
    """Consulta por nombres (búsqueda parcial)"""
    return {
        "message": "Endpoint funcionando",
        "nombres": nombres,
        "note": "Datos no cargados aún - descargando en segundo plano"
    }

@app.get("/essalud/planilla/{planilla}")
async def get_by_planilla(planilla: str):
    """Consulta por número de planilla"""
    return {
        "message": "Endpoint funcionando",
        "planilla": planilla,
        "note": "Datos no cargados aún - descargando en segundo plano"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Essalud API on port {port}")
    print(f"Environment PORT: {os.environ.get('PORT', 'not set')}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
