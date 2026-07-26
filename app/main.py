from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="TagMePet")

# Archivos estáticos y plantillas HTML
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class GPSLocation(BaseModel):
    latitud: float
    longitud: float
    mapa_url: str

@app.get("/", response_class=HTMLResponse)
@app.get("/p/dante", response_class=HTMLResponse)
@app.get("/p/dante123", response_class=HTMLResponse)
@app.get("/p/{pet_id}", response_class=HTMLResponse)
async def ver_dante(request: Request, pet_id: str = "dante"):
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