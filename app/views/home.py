from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

import google.oauth2.credentials
import googleapiclient.discovery

from config import templates, credentials_to_dict

home_view = APIRouter()


# home age of the web-app
@home_view.get("/")
def home(request: Request):
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    
    # loading credentials from session for youtube api
    credentials = google.oauth2.credentials.Credentials(**request.session["credentials"])
    
    API_SERVICE_NAME, API_VERSION = "youtube", "v3"
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    channel = youtube.channels().list(mine=True, part='snippet').execute()

    # Save credentials back to session in case access token was refreshed.
    request.session["credentials"] = credentials_to_dict(credentials)
    
    # check if logged in account has youtube channel, temporarily logging out
    if channel["pageInfo"]["totalResults"] == 0:
        return RedirectResponse(request.url_for("logout"))
    
    context_dict = {
        "request": request,
        "channel_name": channel["items"][0]["snippet"]["title"]
    }
    
    return templates.TemplateResponse("home.html", context=context_dict)