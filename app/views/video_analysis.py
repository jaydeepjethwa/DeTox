from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetch_video_comments
from library.video_analysis import VideoAnalysis

from exceptions import *

from config import templates

analysis_view = APIRouter()

@analysis_view.get("/{video_id}")
async def video_analysis(request: Request, video_id: str):
    """Video Analysis page of the web-app.

    Args:
        request (Request): A Request object containing request data sent from client side.
        video_id (str): Video id for corresponding to which analysis to be done.

    Returns:
        RedirectResponse: Redirects to home page where user authorizes first if not authorized.
        HTMLResponse: If an exception occurs, generic page stating the exception is displayed.
        TemplateResponse: Analysis page with context-dict containing necessary data.
    """
    
    # check if required data is present in session or someone has hit this url directly
    if "credentials" and "channel_data" not in request.session:
        return RedirectResponse(request.url_for("home"))
    
    # fetch comments for given video id and form pandas dataframe
    analysis_obj = VideoAnalysis()
    
    try:
        credentials = await make_comments_dataframe(request.session["credentials"], video_id, analysis_obj)
        
    except QuotaExceededError: # request quota is exceeded
        return HTMLResponse("There was an issue in fetching data from youtube. Please comeback in a while.")
    
    except EntityNotFoundError: # no comments found
        has_comments = False
    
    else:
        has_comments = True
        request.session["credentials"] = credentials # store updated credentials in session

        # make predictions and necessary graphs
        preds = await analysis_obj.classifyComments()
        await analysis_obj.createWordCloud(video_id)
        await analysis_obj.createClassificationGraph(video_id)
    
    context_dict = {
        "request": request,
        "channel_details": request.session["channel_data"]["channel_details"],
        "video": request.session["channel_data"]["video_data"][video_id],
        "has_comments": has_comments
    }
    
    return templates.TemplateResponse("video_analysis.html", context = context_dict)


async def make_comments_dataframe(credentials: dict, video_id: str, analysis_obj: VideoAnalysis) -> dict:
    """Helper function that fetches comments from youtube and stores them as dataframe in analysis class.

    Args:
        credentials (dict): Authorization credentials for accessing channel data.
        video_id (str): Video id corresponding to which fetch comments.
        analysis_obj (VideoAnalysis): Video Analysis object for selected video.

    Returns:
        dict: Credentials dict containing updated values.
    """
    
    comment_response = await fetch_video_comments(credentials, video_id)
    
    # api allows fetching only 100 comments at a time hence repeat to fetch all comments
    while comment_response:
        
        credentials = comment_response["credentials"]
        comment_threads = comment_response["comment_threads"]
        
        comment_dict = {"id": [], "comment_text": []}
        for comment in comment_threads["items"]:
            comment_dict["id"].append(comment['snippet']['topLevelComment']['id'])
            comment_dict["comment_text"].append(comment['snippet']['topLevelComment']['snippet']['textDisplay'])
        
        # append the fetched comments to dataframe
        await analysis_obj.append_comments(comment_dict)
            
        if "nextPageToken" in comment_threads:
            pageToken = comment_threads["nextPageToken"]
            comment_response = await fetch_video_comments(credentials, video_id, pageToken)
        else:
            break
        
    return credentials