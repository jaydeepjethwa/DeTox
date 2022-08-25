import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import templates
from auth import auth_router
from views import home_view, analysis_view

from machine_learning import load_tokeninzer, load_model


# allowing http urls for testing TO BE REMOVED WHILE DEPLOYING
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# initializing fastapi app, adding static files directory and session middelware for session management
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key = os.getenv("session_secret"))


# load machine learning model on startup to reduce time in making first request
@app.on_event("startup")
def startup_event():
    load_tokeninzer()
    load_model()


# landing page of the web-app
@app.get("/", tags=["Landing Page"])
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


# adding various routes to the app
app.include_router(auth_router, tags=["Google OAuth 2.0"], prefix="/auth")
app.include_router(home_view, tags=["Home"], prefix="/home")
app.include_router(analysis_view, tags=["Video Analysis"], prefix="/video-analysis")