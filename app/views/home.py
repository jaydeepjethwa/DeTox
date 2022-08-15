from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from library.yt_data import fetch_channel_data

from config import templates

home_view = APIRouter()
from time import time

# home age of the web-app
@home_view.get("/")
async def home(request: Request):
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    
    channel_data = await fetch_channel_data(request)
    print(channel_data)
    
    channel_name = channel_data["items"][0]["snippet"]["title"]
    channel_logo_url = channel_data["items"][0]["snippet"]["thumbnails"]["default"]["url"]
    stats = channel_data["items"][0]["statistics"]
    
    context_dict = {
        "request": request,
        "channel_name": channel_name,
        "channel_logo_url": channel_logo_url,
        "stats": stats
    }
    
    return templates.TemplateResponse("home.html", context=context_dict)