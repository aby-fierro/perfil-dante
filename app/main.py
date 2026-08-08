from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/p/boris", response_class=HTMLResponse)
@app.get("/p/boris/", response_class=HTMLResponse)
async def ver_boris(request: Request):
    return templates.TemplateResponse(request=request, name="gato.html")
