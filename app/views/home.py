from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetchChannelData, fetchVideoData

from exceptions import *

from config import templates

import asyncio

home_view = APIRouter()

@home_view.get("")
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
        return RedirectResponse(request.url_for("oauth2callback"))
    
    # check if required data is already loaded in session if yes, get it from there else fetch from YT
    if "channel_data" not in request.session:
        credentials = request.session["credentials"]
        request.session["channel_data"] = {}
        try:
            # fetch channel details &  video data and store it in session storage
            channel_details = await fetchChannelData(credentials)
            request.session["channel_data"]["channel_details"] = channel_details

            video_data = await fetchVideoData(credentials)
            request.session["channel_data"]["video_data"] = video_data
            
        except QuotaExceededError: # request quota is exceeded
            return HTMLResponse("Cannot connect to youtube right now. Please comeback in a while.")
        
        except AccessTokenExpiredError: # get fresh access token using refresh token
            request.session["redirect_url"] = str(request.url)
            return RedirectResponse(request.url_for("refresh_access_token"))
        
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


@home_view.get("/refresh-home")
async def refresh_home(request: Request):
    """Clears the channel data stored in session storage.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to home page where updated channel data is fetched.
    """
    
    del request.session["channel_data"]
    
    return RedirectResponse(request.url_for("home"))