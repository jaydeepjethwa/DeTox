from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow

from . import credentials_to_dict


# setting up OAuth 2.0 variables
# file conaining OAuth 2.0 client application details
CLIENT_SECRETS_FILE = "client_secret.json"

# specify OAuth 2.0 access scopes for read/modify account data
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


# router for authorization urls
auth_router = APIRouter()


@auth_router.get("/")
async def authorize(request: Request):
    """Initializes authorization process.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to google authentication url.
    """
    
    # flow object to manage OAuth 2.0 Authorization Grant Flow steps
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
           CLIENT_SECRETS_FILE, 
           scopes = SCOPES
           )
    
    # setting redirect uri 
    flow.redirect_uri = request.url_for("oauth2callback")
    
    authorization_url, state = flow.authorization_url(
                               access_type = "offline", # enables refreshing access token without re-prompting user
                               include_granted_scopes = "true"
                               )
    
    # storing the state so that callback can verify the auth server response
    request.session["state"] = state
    
    return RedirectResponse(authorization_url)


@auth_router.get("/oauth2callback")
async def oauth2callback(request: Request):
    """Redirect Uniform Resource Identifier (URI), called after authorization process. Verifes the authorization state and stores the credentials in session storage.

    Args:
        request (Request): A Request object containing request data sent from client side.

    Returns:
        RedirectResponse: Redirects to home page.
    """
    
    # specifying state in callback so that it can verify authorization response
    state = request.session["state"]
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
           CLIENT_SECRETS_FILE, 
           scopes = SCOPES,
           state = state
           )
    
    flow.redirect_uri = request.url_for("oauth2callback")
    
    # fetching OAuth 2.0 tokens
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)
    
    # storing credentials in the session
    credentials = flow.credentials
    request.session["credentials"] = credentials_to_dict(credentials)
    
    return RedirectResponse(request.url_for("home"))
  

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
        return HTMLResponse(f"You need to <a href={request.url_for('authorize')}>authorize</a> before testing the code to revoke credentials.")
    
    # get credentials from session and create google Credentials class
    credentials = google.oauth2.credentials.Credentials(**request.session["credentials"])
    
    # revoke accesss
    response = requests.post("https://oauth2.googleapis.com/revoke",
        params = {"token": credentials.token},
        headers = {"content-type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200: # if success clear the session i.e. logout
        return RedirectResponse(request.url_for("logout"))
    else:
        return RedirectResponse(request.url_for("home"))
    

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