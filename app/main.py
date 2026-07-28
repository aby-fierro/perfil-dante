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
    
    # Renderiza la ficha pública de la mascota registrada de forma dinámica
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{mascota['nombre']} - TagMePet</title>
        <style>
            body {{ font-family: sans-serif; background: #f0fdfa; padding: 20px; display: flex; justify-content: center; }}
            .card {{ background: white; padding: 24px; border-radius: 16px; max-width: 450px; width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #ccfbf1; }}
            .header {{ background: #0d9488; color: white; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 16px; font-weight: bold; }}
            h1 {{ margin: 0 0 10px 0; color: #0f172a; }}
            p {{ margin: 6px 0; color: #334155; line-height: 1.4; }}
            .label {{ font-weight: bold; color: #0f766e; }}
            .btn {{ display: block; background: #2563eb; color: white; text-align: center; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 16px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">🚨 Mascota Registrada en TagMePet 🚨</div>
            <h1>🐾 {mascota['nombre']}</h1>
            <p><span class="label">Especie:</span> {mascota['especie']}</p>
            <p><span class="label">Raza/Tipo:</span> {mascota['raza']}</p>
            <p><span class="label">Edad:</span> {mascota['edad']}</p>
            <p><span class="label">📍 Colonia / Dirección:</span> {mascota['direccion']}</p>
            <p><span class="label">⚠️ Comportamiento y Salud:</span> {mascota['notas']}</p>
            <p><span class="label">📞 Teléfono de Contacto:</span> {mascota['contacto']}</p>
            
            <a href="https://wa.me/{mascota['contacto'].replace(' ', '')}" class="btn">💬 Contactar por WhatsApp</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)