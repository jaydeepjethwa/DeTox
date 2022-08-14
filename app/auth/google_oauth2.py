from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse

import requests
from config import credentials_to_dict

import google.oauth2.credentials
import google_auth_oauthlib.flow


# setting up OAuth 2.0 variables
# file conaining OAuth 2.0 client application details
CLIENT_SECRETS_FILE = "client_secret.json"

# specify OAuth 2.0 access scopes for read/modify account data
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


# router for authorization urls
auth_router = APIRouter()


# creating flow object and initiating authorization process
@auth_router.get("/")
async def authorize(request: Request):
    # flow instance to manage OAuth 2.0 Authorization Grant Flow steps
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


# redirect uri after user authorizes, stores credentials in session
@auth_router.get("/oauth2callback")
async def oauth2callback(request: Request):
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
  
  
# revoke permissions granted by the user
@auth_router.get("/revoke")
@auth_router.post("/revoke")
async def revoke(request: Request):
    # get credentials from session and create google Credentials class
    credentials = google.oauth2.credentials.Credentials(**request.session["credentials"])
    
    # revoke accesss
    revoke = requests.post("https://oauth2.googleapis.com/revoke",
                          params = {"token": credentials.token},
                          headers = {"content-type": "application/x-www-form-urlencoded"} 
                          )
    
    if revoke.status_code == 200: # if success clear the session i.e. logout
        return RedirectResponse(request.url_for("logout"))
    else:
        return RedirectResponse(request.url_for("home"))
    

# logging out user
@auth_router.get("/logout")
async def logout(request: Request):
    # clearing session data for logging out
    del request.session["credentials"]
    
    return RedirectResponse(request.url_for("landing"))