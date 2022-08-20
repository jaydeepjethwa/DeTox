from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from config import credentials_to_dict

API_SERVICE_NAME, API_VERSION = "youtube", "v3"

yt_router = APIRouter()


@yt_router.get("/fetch_channel_data")
async def fetch_channel_data(request: Request):
    
    credentials, youtube = get_creds_and_yt_obj(request)
    
    # get channel data from yt account
    try:
        channel_resource = youtube.channels().list(
            mine = True, 
            part = 'snippet,contentDetails,statistics'
        ).execute()
    except:
        return HTMLResponse("There was an issue fetching data from youtube. Please comeback in a while.")
    
    try: # if there are no items, no channel associated with the account exist, else store data
        channel_data = {
            "name": channel_resource["items"][0]["snippet"]["title"],
            "logo_url": channel_resource["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
            "stats": channel_resource["items"][0]["statistics"]
        }
    except:
        return HTMLResponse(f"Please <a href={request.url_for('authorize')}>authorize</a> with a valid youtube channel.")
    
    request.session["credentials"] = credentials_to_dict(credentials)
    request.session["channel_data"] = {}
    request.session["channel_data"]["channel_desc"] = channel_data
    
    return RedirectResponse(request.url_for("fetch_video_data"))


@yt_router.get("/fetch_video_data")
async def fetch_video_data(request: Request):
    credentials, youtube = get_creds_and_yt_obj(request)
    
    try: # get latest 3 videos from channel
        video_resource = youtube.search().list(
            part = "snippet",
            forMine = True,
            maxResults = 3,
            order = "date",
            type = "video"
        ).execute()
        
        # extract video ids from video resource
        video_ids = ",".join(resource["id"]["videoId"] for resource in video_resource["items"])
        
        video_details = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids
        ).execute()
    except:
        return HTMLResponse("There was an issue fetching data from youtube. Please comeback in a while.")
    
    # save video data in session for faster access, minimizing api quota
    video_data = []
    
    for data in video_details["items"]:
        video_data.append({
            "title": data["snippet"]["title"],
            "views": data["statistics"]["viewCount"],
            "likes": data["statistics"]["likeCount"],
            "comments": data["statistics"]["commentCount"],
            "description": data["snippet"]["description"][:100],
            "thumbnail_url": data["snippet"]["thumbnails"]["medium"]["url"]
        })
    
    request.session["credentials"] = credentials_to_dict(credentials)
    request.session["channel_data"]["video_data"] = video_data
    
    return RedirectResponse(request.url_for("home"))


# creates credential and youtube request obj and returns
def get_creds_and_yt_obj(request: Request):
    # loading credentials from session for youtube api
    credentials = Credentials(**request.session["credentials"])
    
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
    
    return credentials, youtube