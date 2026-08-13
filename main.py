import base64
import os
import sqlite3
import uuid

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="TagMePet")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "app", "static")
templates_dir = os.path.join(BASE_DIR, "app", "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

DB_FILE = os.path.join(BASE_DIR, "tagmepet.db")

print("=" * 50)
print("DIAGNOSTICO SQLITE")
print("BASE_DIR:", BASE_DIR)
print("Directorio actual:", os.getcwd())
print("Ruta absoluta DB:", os.path.abspath(DB_FILE))
print("Existe antes de conectar:", os.path.exists(DB_FILE))
print("=" * 50)


def init_sqlite_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (
            pet_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            especie TEXT NOT NULL,
            raza TEXT,
            edad TEXT,
            contacto TEXT NOT NULL,
            contacto_secundario TEXT,
            direccion TEXT,
            comportamiento TEXT,
            salud TEXT,
            notas TEXT,
            estado TEXT DEFAULT 'seguro',
            foto_url TEXT
        )
    """)
    columnas_extra = [
        ("contacto_secundario", "TEXT"),
        ("comportamiento", "TEXT"),
        ("salud", "TEXT"),
    ]
    for col, col_type in columnas_extra:
        try:
            cursor.execute(f"ALTER TABLE mascotas ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

    print("=" * 50)
    print("Base creada o abierta correctamente.")
    print("Existe despues de crearla:", os.path.exists(DB_FILE))
    if os.path.exists(DB_FILE):
        print("Tamano:", os.path.getsize(DB_FILE), "bytes")
    print("=" * 50)


init_sqlite_db()


class GPSLocation(BaseModel):
    latitud: float
    longitud: float
    mapa_url: str


@app.get("/")
async def inicio():
    return RedirectResponse(url="/registro")


@app.get("/p/dante", response_class=HTMLResponse)
@app.get("/p/dante/", response_class=HTMLResponse)
@app.get("/p/dante123", response_class=HTMLResponse)
async def ver_dante(request: Request):
    return templates.TemplateResponse(request=request, name="dante.html")


@app.get("/p/negra", response_class=HTMLResponse)
@app.get("/p/negra/", response_class=HTMLResponse)
async def ver_negra(request: Request):
    return templates.TemplateResponse(request=request, name="negra.html")


@app.get("/p/boris", response_class=HTMLResponse)
@app.get("/p/boris/", response_class=HTMLResponse)
async def ver_boris(request: Request):
    return templates.TemplateResponse(request=request, name="gato.html")


@app.post("/api/notificar-gps")
async def notificar_gps(datos: GPSLocation):
    destinatarios = ["abygailfierro191@gmail.com", "friskpapa@gmail.com"]
    cuerpo = f"""
    Hola,
    Alguien ha presionado el boton de compartir ubicacion en la placa de Dante.
    Coordenadas: {datos.latitud}, {datos.longitud}
    Ver en Google Maps: {datos.mapa_url}
    """
    try:
        for correo in destinatarios:
            print(f"NOTIFICACION PARA: {correo}\n{cuerpo}")
        return {"status": "ok", "mensaje": "Notificacion enviada"}
    except Exception as e:
        return JSONResponse(
            {"status": "error", "detalle": str(e)}, status_code=500
        )


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
    contacto_secundario: str = Form(""),
    direccion: str = Form("No proporcionada"),
    comportamiento: str = Form(""),
    salud: str = Form(""),
    notas: str = Form(""),
    estado: str = Form("seguro"),
    foto: UploadFile = File(None),
    foto_url: str = Form(""),
):
    codigo_unico = f"{nombre.lower().replace(' ', '')}-{str(uuid.uuid4())[:4]}"

    final_foto_src = ""
    if foto and foto.filename:
        contenido = await foto.read()
        if len(contenido) > 0:
            base64_img = base64.b64encode(contenido).decode("utf-8")
            content_type = (
                foto.content_type if foto.content_type else "image/jpeg"
            )
            final_foto_src = f"data:{content_type};base64,{base64_img}"
    elif foto_url and foto_url.strip() != "":
        final_foto_src = foto_url.strip()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        query = """
            INSERT INTO mascotas 
            (pet_id, nombre, especie, raza, edad, contacto, contacto_secundario, direccion, comportamiento, salud, notas, estado, foto_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query,
            (
                codigo_unico,
                nombre.strip(),
                especie.strip(),
                raza.strip(),
                edad.strip(),
                contacto.strip(),
                contacto_secundario.strip(),
                direccion.strip(),
                comportamiento.strip(),
                salud.strip(),
                notas.strip(),
                estado.lower().strip(),
                final_foto_src,
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        return JSONResponse(
            {"status": "error", "detalle": str(e)}, status_code=500
        )

    return JSONResponse({
        "status": "ok",
        "mensaje": "Mascota registrada con exito",
        "pet_id": codigo_unico,
        "url": f"/p/{codigo_unico}",
    })


@app.get("/p/{pet_id}", response_class=HTMLResponse)
async def ver_mascota_registrada(request: Request, pet_id: str):
    mascota = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mascotas WHERE pet_id = ?", (pet_id,))
        row = cursor.fetchone()
        if row:
            mascota = dict(row)
        conn.close()
    except Exception as e:
        return HTMLResponse(
            content=f"<h2>Error de conexion con la base de datos: {str(e)}</h2>",
            status_code=500,
        )

    if not mascota:
        return HTMLResponse(
            content="<h2>Mascota no encontrada</h2>", status_code=404
        )

    tel1_raw = mascota.get("contacto") or ""
    tel1_limpio = tel1_raw.replace(" ", "").replace("-", "").replace("+", "")

    tel2_raw = mascota.get("contacto_secundario") or ""
    tel2_limpio = tel2_raw.replace(" ", "").replace("-", "").replace("+", "")

    estado_val = str(mascota.get("estado", "")).lower().strip()
    es_perdido = "perdido" in estado_val

    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context={
            "mascota": mascota,
            "tel1_limpio": tel1_limpio,
            "tel2_limpio": tel2_limpio,
            "es_perdido": es_perdido,
        },
    )


@app.get("/descargar-db")
async def descargar_base_de_datos():
    return FileResponse(DB_FILE, filename="tagmepet.db")