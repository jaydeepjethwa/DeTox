from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from settings import templates
from views.home import router as HomeView


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Landing Page"])
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

app.include_router(HomeView, tags=["Home"], prefix="/home")