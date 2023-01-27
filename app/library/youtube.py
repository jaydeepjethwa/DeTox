import os

import httpx

from exceptions import *

# clint secret key for sending requests to yt api
KEY = os.getenv("CLIENT_SECRET")


async def fetchChannelData(credentials: dict) -> dict:
    """Fetches youtube channel data for authorized google account.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.

    Raises:
        QuotaExceededError: If request quota is utilized.
        AccessTokenExpiredError: If access token in authorization header has expired.
        EntityNotFoundError: If youtube channel for authorized account doesn't exist.

    Returns:
        dict: Channel details of logged in user.
    """
    
    request_uri = "https://www.googleapis.com/youtube/v3/channels"
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Accept": "application/json"
    }
    
    params = {
        "mine": "true",
        "part": "snippet,contentDetails,statistics",
        "key": KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(request_uri, params = params, headers = headers)
    
    # fails when quota exceeds or access token expires
    if response.status_code == 403:
        raise QuotaExceededError("Request quota exceeded for the day.")
    
    elif response.status_code == 401:
        raise AccessTokenExpiredError("Current access token expired, get a fresh one.")
    
    channel_resource = response.json()
    
    # check if channel exists
    if "items" not in channel_resource:
        raise EntityNotFoundError("channel", "Authorized goole account doesn't have a youtube channel.")
    
    # extract required channel details
    channel_details = {
        "name": channel_resource["items"][0]["snippet"]["title"],
        "logo_url": channel_resource["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
        "stats": channel_resource["items"][0]["statistics"]
    }
    
    return channel_details


async def fetchVideoData(credentials: dict) -> dict:
    """Fetches video data for logged in youtube channel.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.

    Raises:
        QuotaExceededError: If request quota is utilized.
        AccessTokenExpiredError: If access token in authorization header has expired.
        EntityNotFoundError: If videos for logged in channel doesn't exist.

    Returns:
        dict: Video data for latest 3 videos of the user.
    """
    
    request_uri = "https://www.googleapis.com/youtube/v3/search"
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Accept": "application/json"
    }

    params = {
        "part": "snippet",
        "forMine": "true",
        "maxResults": 3,    # get latest 3 videos from channel
        "order": "date",
        "type": "video",
        "key": KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(request_uri, params = params, headers = headers)
    
    # fails when quota exceeds or access token expires
    if response.status_code == 403:
        raise QuotaExceededError("Request quota exceeded for the day.")
    
    elif response.status_code == 401:
        raise AccessTokenExpiredError("Current access token expired, get a fresh one.")
    
    video_resource = response.json()
    
    # if no videos uploaded
    if "items" not in video_resource or len(video_resource["items"]) == 0:
        raise EntityNotFoundError("video", "Authorized youtube account haven't uploaded videos.")
    
    # extract video ids from video resource
    video_ids = ",".join(resource["id"]["videoId"] for resource in video_resource["items"])
    
    # get video data from obtained video ids
    request_uri = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_ids,
        "key": KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(request_uri, params = params, headers = headers)
    
    # fails when quota exceeds or access token expires
    if response.status_code == 403:
        raise QuotaExceededError("Request quota exceeded for the day.")
    
    elif response.status_code == 401:
        raise AccessTokenExpiredError("Current access token expired, get a fresh one.")
    
    video_details = response.json()
    
    # extract required video data
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
    
    return video_data


async def fetchVideoComments(credentials: dict, video_id: str):
    """Generator function fetches comments for given youtube video id.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.
        video_id (str): Video id corresponding to which fetch comments.

    Raises:
        QuotaExceededError: If request quota is utilized.
        AccessTokenExpiredError: If access token in authorization header has expired.
        EntityNotFoundError: If comments for given video id doesn't exist.

    Returns:
        AsyncGenerator: An async generator object which can be iterated over to get dict containing comments data for specified video.
    """
    
    pageToken = ""
    
    request_uri = "https://www.googleapis.com/youtube/v3/commentThreads"
    
    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Accept": "application/json"
    }
    
    # yt api allows fetching only 100 comments at a time hence repeat to fetch all comments
    while True:
        params = {
            "part": "snippet",
            "maxResults": 100,
            "pageToken": pageToken,
            "video_id": video_id,
            "key": KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(request_uri, params = params, headers = headers)
        
        # fails when quota exceeds or access token expires
        if response.status_code == 403:
            raise QuotaExceededError("Request quota exceeded for the day.")
        
        elif response.status_code == 401:
            raise AccessTokenExpiredError("Current access token expired, get a fresh one.")
        
        comment_threads = response.json()
        
        # if there are no comments posted
        if "items" not in comment_threads or len(comment_threads["items"]) == 0:
            raise EntityNotFoundError("comment_thread", "Selected video doesn't have any comments")
        
        comment_dict = {"id": [], "comment_text": []}
        for comment in comment_threads["items"]:
            comment_dict["id"].append(comment['snippet']['topLevelComment']['id'])
            comment_dict["comment_text"].append(comment['snippet']['topLevelComment']['snippet']['textDisplay'])
        
        # send data to analysis view and go to next iteration if possible
        yield comment_dict
        
        if "nextPageToken" in comment_threads:
            pageToken = comment_threads["nextPageToken"]
        else:
            break
        
        
async def rejectComments(credentials: dict, toxic_ids: list) -> None:
    """Set moderation status of toxic comment ids provided as 'rejected'.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.
        toxic_ids (list): List of ids of comments which are identified as toxic.

    Raises:
        QuotaExceededError: If request quota is utilized.
        AccessTokenExpiredError: If access token in authorization header has expired.
    """
    
    request_uri = "https://www.googleapis.com/youtube/v3/comments/setModerationStatus"

    headers = {
        "Authorization": f"Bearer {credentials['access_token']}",
        "Accept": "application/json"
    }
    
    params = {
        "id": ",".join(id for id in toxic_ids),
        "moderationStatus": "rejected",
        "key": KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(request_uri, params = params, headers = headers)
    
    # fails when quota exceeds or access token expires
    if response.status_code == 403:
        raise QuotaExceededError("Request quota exceeded for the day.")
    
    elif response.status_code == 401:
        raise AccessTokenExpiredError("Current access token expired, get a fresh one.")