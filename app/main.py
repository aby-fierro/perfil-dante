from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid

app = FastAPI(title="TagMePet")

mascotas_db = {}

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class GPSLocation(BaseModel):
    latitud: float
    longitud: float
    mapa_url: str

@app.get("/", response_class=HTMLResponse)
@app.get("/p/dante", response_class=HTMLResponse)
@app.get("/p/dante123", response_class=HTMLResponse)
async def ver_dante(request: Request):
    return templates.TemplateResponse(request=request, name="dante.html")

@app.post("/api/notificar-gps")
async def notificar_gps(datos: GPSLocation):
    destinatarios = [
        "abygailfierro191@gmail.com",
        "friskpapa@gmail.com"
    ]
    
    asunto = "🚨 ¡ALERTA DE GPS! Alguien presionó la ubicación de Dante"
    cuerpo = f"""
    Hola,
    
    Alguien ha presionado el botón de compartir ubicación en la placa de Dante.
    
    Coordenadas: {datos.latitud}, {datos.longitud}
    Ver en Google Maps: {datos.mapa_url}
    """
    
    try:
        for correo in destinatarios:
            print(f"NOTIFICACIÓN DE CORREO GENERADA PARA: {correo}\n{cuerpo}")
            
        return {"status": "ok", "mensaje": "Notificaciones procesadas correctamente"}
    except Exception as e:
        return {"status": "error", "detalle": str(e)}, 500

@app.get("/registro", response_class=HTMLResponse)
async def ver_registro(request: Request):
    return templates.TemplateResponse(request=request, name="registro.html")

@app.post("/api/registrar-mascota")
async def registrar_mascota(
    nombre: str = Form(...),
    especie: str = Form(...),
    raza: str = Form("No especificada"),
    edad: str = Form("No especificada"),
    contacto: str = Form(...),
    direccion: str = Form("No proporcionada"),
    notas: str = Form("Sin notas adicionales")
):

    codigo_unico = f"{nombre.lower().replace(' ', '')}-{str(uuid.uuid4())[:4]}"
    
    mascotas_db[codigo_unico] = {
        "id": codigo_unico,
        "nombre": nombre,
        "especie": especie,
        "raza": raza,
        "edad": edad,
        "contacto": contacto,
        "direccion": direccion,
        "notas": notas
    }
    
    return JSONResponse({
        "status": "ok",
        "mensaje": "Mascota registrada con éxito",
        "pet_id": codigo_unico,
        "url": f"/p/{codigo_unico}"
    })

@app.get("/p/{pet_id}", response_class=HTMLResponse)
async def ver_mascota_registrada(request: Request, pet_id: str):
    mascota = mascotas_db.get(pet_id)
    if not mascota:
        return HTMLResponse(content="<h2>Mascota no encontrada o ID inválido</h2>", status_code=404)
    
    return templates.TemplateResponse(request=request, name="gato.html", context={"mascota": mascota})