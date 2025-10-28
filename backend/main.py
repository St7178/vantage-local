from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import buscar_servidor, calcular_costo_aws, calcular_costo_vantage

app = FastAPI(title="Vantage Local API")

# Permitir frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/servers/{vm_name}")
def obtener_servidor(vm_name: str):
    server = buscar_servidor(vm_name)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
    return server

@app.get("/servers/{vm_name}/quote")
def cotizar_servidor(vm_name: str):
    server = buscar_servidor(vm_name)
    if not server:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
    costo = calcular_costo_aws(server)
    return {"server": vm_name, "detalles": costo}
