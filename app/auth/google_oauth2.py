import os
from dotenv import load_dotenv

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

import httpx

from exceptions import *


# getting OAuth 2.0 secret variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPE = os.getenv("SCOPE")
REDIRECT_URI = os.getenv("REDIRECT_URIS")
STATE = os.getenv("STATE")

# router for authorization urls
auth_router = APIRouter()


@auth_router.get("/oauth2callback")
async def oauth2callback(request: Request, state: str = None, code: str = None):
    """Authorization Uniform Resource Identifier (URI). Seeks authorization from user via google oauth2.0 and retrieves the access token for future yt api calls.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to google authorization page and post verification to home page.
    """
    
    if code == None:
        auth_uri = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&access_type=offline&state={STATE}"
        
        return RedirectResponse(auth_uri)
        
    else:
        # ensure that authorization request was called from our application
        if STATE != state:
            return HTMLResponse(f"Invalid state parameter. Please visit the <a href={request.url_for('landing')}>web-app</a> to complete the authorization.")
        
        # retrieve access token
        auth_code = code
        data = {
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post("https://oauth2.googleapis.com/token", data = data)
        
        request.session["credentials"] = response.json()
        
        return RedirectResponse(request.url_for("home"))
    

@auth_router.get("/refresh-access-token")
async def refresh_access_token(request: Request):
    """Gets new access token using refresh token.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to page from which request was originated.
    """
    
    data = {
        "client_id": CLIENT_ID, 
        "client_secret": CLIENT_SECRET,
        "refresh_token": request.session["credentials"]["refresh_token"],
        "grant_type": "refresh_token"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post("https://oauth2.googleapis.com/token", data = data)
    
    if response.status_code == 400: # apps access to yt account has been revoked
        return HTMLResponse(f"Web-app's access to your youtube account has been revoked. Please <a href={request.url_for('oauth2callback')}>authorize</a> to continue using the service.")
    
    credentials = response.json()
    request.session["credentials"]["access_token"] = credentials["access_token"]
    request.session["credentials"]["expires_in"] = credentials["expires_in"]
    
    redirect_url = request.session["redirect_url"]
    
    return RedirectResponse(redirect_url)
    

@auth_router.get("/revoke")
async def revoke(request: Request):
    """Revokes YouTube account access from the web-app.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to logout page for clearing data in session and if failed to revoke redirects back to home page.
    """
    
    # if not logged in login first
    if "credentials" not in request.session:
        return HTMLResponse(f"You need to <a href={request.url_for('oauth2callback')}>authorize</a> first before revoking the credentials.")
    
    # get credentials from session
    credentials = request.session["credentials"]
    
    # revoke accesss
    async with httpx.AsyncClient() as client:
        response = await client.post("https://oauth2.googleapis.com/revoke",
            params = {"token": credentials["access_token"]},
            headers = {"content-type": "application/x-www-form-urlencoded"}
        )
    
    # fails when quota exceeds or access token expires
    if response.status_code == 403:
        return HTMLResponse("Cannot connect to youtube right now. Please comeback in a while.")
    
    elif response.status_code == 401:
        request.session["redirect_url"] = str(request.url)
        return RedirectResponse(request.url_for("refresh_access_token"))
    
    return RedirectResponse(request.url_for("logout"))
    

@auth_router.get("/logout")
async def logout(request: Request):
    """Logs out the authenticated user by clearing out the session storage.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to landing page.
    """
    
    request.session.clear()
    
    return RedirectResponse(request.url_for("landing"))