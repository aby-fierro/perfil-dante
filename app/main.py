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
    
    telefono_limpio = mascota['contacto'].replace(' ', '').replace('-', '')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{mascota['nombre']} - TagMePet</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0fdfa; padding: 20px 12px; display: flex; justify-content: center; margin: 0; }}
            .card {{ background: white; padding: 24px; border-radius: 20px; max-width: 450px; width: 100%; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); border: 1px solid #ccfbf1; }}
            .header {{ background: #0d9488; color: white; padding: 14px; border-radius: 12px; text-align: center; margin-bottom: 18px; font-weight: bold; font-size: 0.95rem; }}
            h1 {{ margin: 0 0 12px 0; color: #0f172a; font-size: 1.8rem; }}
            p {{ margin: 8px 0; color: #334155; line-height: 1.5; font-size: 0.95rem; }}
            .label {{ font-weight: bold; color: #0f766e; display: block; margin-top: 10px; }}
            .btn-group {{ margin-top: 20px; display: flex; flex-direction: column; gap: 10px; }}
            .btn {{ display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 0.95rem; border: none; cursor: pointer; }}
            .btn-wa {{ background-color: #25d366; color: white; }}
            .btn-call {{ background-color: #2563eb; color: white; }}
            .btn-gps {{ background-color: #dc2626; color: white; width: 100%; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">🐾 Estado Seguro / Registrado en TagMePet</div>
            <h1>🐾 {mascota['nombre']}</h1>
            
            <p><span class="label">Especie y Raza:</span> {mascota['especie']} ({mascota['raza']})</p>
            <p><span class="label">Edad:</span> {mascota['edad']}</p>
            <p><span class="label">📍 Colonia / Dirección:</span> {mascota['direccion']}</p>
            <p><span class="label">⚠️ Comportamiento y Salud:</span> {mascota['notas']}</p>
            
            <div class="btn-group">
                <p><span class="label">¿Lo encontraste o lo viste?</span></p>
                <a href="https://wa.me/{telefono_limpio}" class="btn btn-wa">💬 Enviar WhatsApp</a>
                <a href="tel:{telefono_limpio}" class="btn btn-call">📞 Llamar Directo</a>
                <button onclick="compartirUbicacion()" class="btn btn-gps">📍 Compartir mi Ubicación GPS</button>
            </div>
        </div>

        <script>
            function compartirUbicacion() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(function(position) {{
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const mapaUrl = `https://www.google.com/maps?q=${{lat}},${{lon}}`;
                        
                        fetch('/api/notificar-gps', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ latitud: lat, longitud: lon, mapa_url: mapaUrl }})
                        }}).then(res => {{
                            alert('Ubicación compartida con los dueños correctamente.');
                        }});
                    }});
                }} else {{
                    alert('La geolocalización no está soportada por este navegador.');
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)