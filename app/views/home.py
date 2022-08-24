from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetch_channel_data, fetch_video_data

from config import templates

home_view = APIRouter()

# home page of the web-app
@home_view.get("/")
async def home(request: Request):
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    # check if required data is already loaded in session if yes, get it from there else fetch from YT
    if "channel_data" not in request.session:
        request.session["channel_data"] = {}
        # try:
        # fetch channel details
        channel_response = await fetch_channel_data(request.session["credentials"])
        request.session["channel_data"]["channel_details"] = channel_response["channel_details"]
        request.session["credentials"] = channel_response["credentials"] # storing updated credentials
        
        # fetch video data
        video_response = await fetch_video_data(request.session["credentials"])
        request.session["channel_data"]["video_data"] = video_response["video_data"]
        request.session["credentials"] = video_response["credentials"]
            
        # except HTTPException(status_code = 503):
        #     return HTMLResponse("There was an issue in fetching data from youtube. Please comeback in a while.")
        
        # except HTTPException(status_code = 404):
        #     return HTMLResponse(f"<a href={request.url_for('revoke')}>Revoke access</a> for this account and <a href={request.url_for('authorize')}>authorize</a> with a valid youtube channel. ")
    
    channel_details = request.session["channel_data"]["channel_details"]
    video_data = request.session["channel_data"]["video_data"]
        
    context_dict = {
        "request": request,
        "channel_details": channel_details,
        "video_data": video_data
    }
    
    return templates.TemplateResponse("home.html", context = context_dict)