from fastapi import HTTPException

from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from config import credentials_to_dict

API_SERVICE_NAME, API_VERSION = "youtube", "v3"


# fetches channel data for authorized user
async def fetch_channel_data(credentials: dict) -> dict:
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    # get channel data from yt account
    # try:
    channel_resource = youtube.channels().list(
        mine = True, 
        part = 'snippet,contentDetails,statistics'
    ).execute()
    # except Exception:
    #     raise HTTPException(status_code = 503)
    
    # try: # if there are no items, no channel associated with the account exist, else store data
    channel_details = {
        "name": channel_resource["items"][0]["snippet"]["title"],
        "logo_url": channel_resource["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
        "stats": channel_resource["items"][0]["statistics"]
    }
    # except Exception:
    #     raise HTTPException(status_code = 404)
    
    # saving updated credentials and channel data in session storage for faster access and minimizing quota usage
    data = {
        "credentials": credentials_to_dict(credentials),
        "channel_details": channel_details
    }
    
    return data


# fetch video data for authorized yt channel
async def fetch_video_data(credentials: dict) -> dict:
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    # try: # get latest 3 videos from channel
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
    # except Exception:
    #     raise HTTPException(status_code = 503)
    
    # save video data in session for faster access, minimizing api quota
    video_data = {}
    
    for data in video_details["items"]:
        video_data[data["id"]] = {
            "id": data["id"],
            "title": data["snippet"]["title"],
            "views": data["statistics"]["viewCount"],
            "likes": data["statistics"]["likeCount"],
            "comments": data["statistics"]["commentCount"],
            "description": data["snippet"]["description"][:100],
            "thumbnail_url": data["snippet"]["thumbnails"]["medium"]["url"]
        }
    
    data = {
        "credentials": credentials_to_dict(credentials),
        "video_data": video_data
    }
    
    return data


# fetch comment threads for given id and if given, pagetoken
async def fetch_video_comments(credentials: dict, video_id: str, pageToken: str = "") -> dict:
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    # try:
    comment_threads = youtube.commentThreads().list(
        part = "snippet",
        maxResults = 100,
        pageToken = pageToken,
        videoId = video_id
    ).execute()
    # except Exception:
    #     raise HTTPException(status_code = 503)
    
    data = {
        "credentials": credentials_to_dict(credentials),
        "comment_threads": comment_threads
    }
    
    return data


# creates credential and youtube request obj and returns
def get_creds_and_yt_obj(credentials: dict) -> tuple:
    # loading credentials from session for youtube api
    credentials = Credentials(**credentials)
    
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
    
    return credentials, youtube