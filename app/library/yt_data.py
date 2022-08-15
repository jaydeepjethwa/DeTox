from fastapi import Request

from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from config import credentials_to_dict


API_SERVICE_NAME, API_VERSION = "youtube", "v3"


# creates credential and youtube request obj and returns
def get_creds_and_yt_obj(request: Request):
    # loading credentials from session for youtube api
    credentials = Credentials(**request.session["credentials"])
    
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
    
    return credentials, youtube


# Save credentials back to session in case access token was refreshed.
def save_credentials_to_session(request: Request, credentials: Credentials):
    request.session["credentials"] = credentials_to_dict(credentials)


# fetch channel data for signed in user
async def fetch_channel_data(request: Request):
    
    credentials, youtube = get_creds_and_yt_obj(request)
    
    channel_data = youtube.channels().list(
        mine = True, 
        part = 'snippet,contentDetails,statistics'
    ).execute()
    
    save_credentials_to_session(request, credentials)
    
    return channel_data


# fetches latest 3 videos uploaded by logged in user
async def fetch_videos(request: Request):
    
    credentials, youtube = get_creds_and_yt_obj(request)
    
    videos = youtube.search().list(
        part = "snippet",
        forMine = True,
        maxResults = 25,
        order = "date",
        type = "video"
    ).execute()
    
    save_credentials_to_session(request, credentials)
    
    return videos


# fetches video data for given video search resource
async def fetch_video_data(request: Request, video_resource):
    
    credentials, youtube = get_creds_and_yt_obj(request)
    
    # extract video ids from video resource
    video_ids = ",".join(resource["id"]["videoId"] for resource in video_resource["items"])
    
    video_data = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_ids
    ).execute()
    
    save_credentials_to_session(request, credentials)
    
    return video_data
    