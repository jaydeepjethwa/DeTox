from google.oauth2.credentials import Credentials
import googleapiclient.discovery

from exceptions import *

from auth import credentials_to_dict

API_SERVICE_NAME, API_VERSION = "youtube", "v3"


async def fetch_channel_data(credentials: dict) -> dict:
    """Fetches youtube channel data for authorized google account.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.

    Raises:
        QuotaExceededError: If request quota is utilized.
        EntityNotFoundError: If youtube channel for authorized account doesn't exist.

    Returns:
        dict: Contains updated credentials dict and channel details dict.
    """
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    # get channel data from yt account
    try:
        channel_resource = youtube.channels().list(
            mine = True, 
            part = 'snippet,contentDetails,statistics'
        ).execute()
        
    except: # fails when quota exceeds
        raise QuotaExceededError("Request quota exceeded for the day.")
    
    # check if channel exists
    if "items" not in channel_resource:
        raise EntityNotFoundError("channel", "Authorized goole account doesn't have a youtube channel.")
    
    # extract channel details
    channel_details = {
        "name": channel_resource["items"][0]["snippet"]["title"],
        "logo_url": channel_resource["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
        "stats": channel_resource["items"][0]["statistics"]
    }
    
    # return updated credentials and channel details
    data = {
        "credentials": credentials_to_dict(credentials),
        "channel_details": channel_details
    }
    
    return data


async def fetch_video_data(credentials: dict) -> dict:
    """Fetches video data for logged in youtube channel.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.

    Raises:
        QuotaExceededError: If request quota is utilized.
        EntityNotFoundError: If videos for logged in channel doesn't exist.

    Returns:
        dict: Contains updated credentials dict and video data dict.
    """
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    # get latest 3 videos from channel
    try:
        video_resource = youtube.search().list(
            part = "snippet",
            forMine = True,
            maxResults = 3,
            order = "date",
            type = "video"
        ).execute()
        
    except: # fails when quota exceeds
        raise QuotaExceededError("Request quota exceeded for the day.")
        
    # if no videos uploaded
    if "items" not in video_resource or len(video_resource["items"]) == 0:
        raise EntityNotFoundError("video", "Authorized youtube account haven't uploaded videos.")
    
    # extract video ids from video resource
    video_ids = ",".join(resource["id"]["videoId"] for resource in video_resource["items"])
    
    # get video data from obtained video ids
    try:
        video_details = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids
        ).execute()
        
    except: # fails when quota exceeds
        raise QuotaExceededError("Request quota exceeded for the day.")
    
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
    
    # return updated credentials and video data
    data = {
        "credentials": credentials_to_dict(credentials),
        "video_data": video_data
    }
    
    return data


async def fetch_video_comments(credentials: dict, video_id: str, pageToken: str = "") -> dict:
    """Fetches comments for given youtube video id.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.
        video_id (str): Video id corresponding to which fetch comments.
        pageToken (str, optional): Indicates point from which to fetch comments. Defaults to "".

    Raises:
        QuotaExceededError: If request quota is utilized.
        EntityNotFoundError: If comments for given video id doesn't exist.

    Returns:
        dict: Contains updated credentials dict and comment threads dict.
    """
    
    credentials, youtube = get_creds_and_yt_obj(credentials)
    
    try:
        comment_threads = youtube.commentThreads().list(
            part = "snippet",
            maxResults = 100,
            pageToken = pageToken,
            videoId = video_id
        ).execute()
        
    except:
        raise QuotaExceededError("Request quota exceeded for the day")
    
    # if there are no comments posted
    if "items" not in comment_threads or len(comment_threads["items"]) == 0:
        raise EntityNotFoundError("comment_thread", "Selected video doesn't have any comments")
    
    # return updated credentials and comments
    data = {
        "credentials": credentials_to_dict(credentials),
        "comment_threads": comment_threads
    }
    
    return data


def get_creds_and_yt_obj(credentials: dict) -> tuple:
    """Creates credential and youtube request objects.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.

    Returns:
        tuple: updated credentials and youtube objects used to communicate with youtube data api.
    """
    
    credentials = Credentials(**credentials)
    
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
    
    return credentials, youtube