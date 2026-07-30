from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=RedirectResponse)
async def inicio():
    return RedirectResponse(url="/registro")

@app.get("/registro", response_class=HTMLResponse)
async def registro(request: Request):
    return templates.TemplateResponse(request=request, name="registro.html")

@app.get("/p/dante", response_class=HTMLResponse)
@app.get("/p/dante/", response_class=HTMLResponse)
async def perfil_dante(request: Request):
    return templates.TemplateResponse(request=request, name="dante.html")
