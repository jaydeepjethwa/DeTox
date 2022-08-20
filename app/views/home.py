from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from config import templates

home_view = APIRouter()

# home page of the web-app
@home_view.get("/")
async def home(request: Request):
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    if "channel_data" not in request.session:
        return RedirectResponse(request.url_for("fetch_channel_data"))
    
    channel_data = request.session["channel_data"]["channel_desc"]
    video_data = request.session["channel_data"]["video_data"]
        
    context_dict = {
        "request": request,
        "channel_data": channel_data,
        "video_data": video_data
    }
    
    return templates.TemplateResponse("home.html", context=context_dict)