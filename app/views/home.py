from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetch_channel_data, fetch_video_data

from exceptions import *

from config import templates

home_view = APIRouter()

@home_view.get("/")
async def home(request: Request):
    """Home page of the web-app.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectReponse: If user is not authorized, redirect to authorize. 
        HTMLResponse: If an exception occurs, generic page stating the exception is displayed.
        TemplateResponse: Home page with context-dict containing necessary data.
    """
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    # check if required data is already loaded in session if yes, get it from there else fetch from YT
    if "channel_data" not in request.session:
        request.session["channel_data"] = {}
        try:
            # fetch channel details
            channel_response = await fetch_channel_data(request.session["credentials"])
            request.session["channel_data"]["channel_details"] = channel_response["channel_details"]
            request.session["credentials"] = channel_response["credentials"] # storing updated credentials
            
            # fetch video data
            video_response = await fetch_video_data(request.session["credentials"])
            request.session["channel_data"]["video_data"] = video_response["video_data"]
            request.session["credentials"] = video_response["credentials"]
            
        except QuotaExceededError: # request quota is exceeded
            return HTMLResponse("There was an issue in fetching data from youtube. Please comeback in a while.")
        
        except EntityNotFoundError as entity_error: # no channel or videos not found
            if entity_error.entity == "channel":
                return HTMLResponse(f"<a href={request.url_for('revoke')}>Revoke access</a> for this account and authorize with a valid youtube channel.")
            
            elif entity_error.entity == "video":
                request.session["channel_data"]["video_data"] = {}
    
    channel_details = request.session["channel_data"]["channel_details"]
    video_data = request.session["channel_data"]["video_data"]
        
    context_dict = {
        "request": request,
        "channel_details": channel_details,
        "video_data": video_data
    }
    
    return templates.TemplateResponse("home.html", context = context_dict)