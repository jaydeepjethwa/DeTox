from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from library.yt_data import fetch_channel_data, fetch_videos, fetch_video_data

from config import templates

home_view = APIRouter()

# home page of the web-app
@home_view.get("/")
async def home(request: Request):
    
    # if not authorized, auhthorize first
    if "credentials" not in request.session:
        return RedirectResponse(request.url_for("authorize"))
    
    # get channel data from yt account
    channel_resource = await fetch_channel_data(request)
    
    channel_data = {
        "name": channel_resource["items"][0]["snippet"]["title"],
        "logo_url": channel_resource["items"][0]["snippet"]["thumbnails"]["medium"]["url"],
        "stats": channel_resource["items"][0]["statistics"]
    }
    
    # get video data from yt account
    video_resource = await fetch_videos(request)
    
    video_details = await fetch_video_data(request, video_resource)
    # print(video_data)
    
    video_data = {
        "title": [],
        "views": [],
        "likes": [],
        "comments": [],
        "description": [],
        "thumbnail_url": []
    }
    
    for data in video_details["items"]:
        video_data["title"].append(data["snippet"]["title"])
        video_data["description"].append(data["snippet"]["description"])
        video_data["thumbnail_url"].append(data["snippet"]["thumbnails"]["medium"]["url"])
        video_data["views"].append(data["statistics"]["viewCount"])
        video_data["likes"].append(data["statistics"]["likeCount"])
        video_data["comments"].append(data["statistics"]["commentCount"])
    
    
    context_dict = {
        "request": request,
        "channel_data": channel_data,
        "video_data": video_data
    }
    
    return templates.TemplateResponse("home.html", context=context_dict)