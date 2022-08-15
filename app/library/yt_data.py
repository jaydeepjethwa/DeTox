from fastapi import Request

import google.oauth2.credentials
import googleapiclient.discovery

from config import credentials_to_dict


API_SERVICE_NAME, API_VERSION = "youtube", "v3"

# fetch channel data for signed in user
async def fetch_channel_data(request: Request):
    # loading credentials from session for youtube api
    credentials = google.oauth2.credentials.Credentials(**request.session["credentials"])
    
    # Save credentials back to session in case access token was refreshed.
    request.session["credentials"] = credentials_to_dict(credentials)
    
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    channel_data = youtube.channels().list(mine=True, part='snippet,contentDetails,statistics').execute()
    
    return channel_data