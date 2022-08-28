import os

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
        video_id (str): Video id corresponding to which analysis to be done.

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
        comment_itr = fetch_video_comments(request.session["credentials"], video_id)
        
        # get every batch of comments by iterating over async generator object and append to dataframe
        async for data in comment_itr:
            request.session["credentials"] = data["credentials"]
            await analysis_obj.append_comments(data["comment_dict"])
        
    except QuotaExceededError: # request quota is exceeded
        return HTMLResponse("There was an issue in fetching data from youtube. Please comeback in a while.")
    
    except EntityNotFoundError: # no comments found
        has_comments = False
    
    else:
        has_comments = True

        # make predictions and necessary graphs
        await analysis_obj.classifyComments()
        await analysis_obj.createWordCloud(video_id)
        await analysis_obj.createClassificationGraph(video_id)
        # await analysis_obj.getToxicIds()
    
    context_dict = {
        "request": request,
        "channel_details": request.session["channel_data"]["channel_details"],
        "video": request.session["channel_data"]["video_data"][video_id],
        "video_id": video_id,
        "has_comments": has_comments
    }
    
    return templates.TemplateResponse("video_analysis.html", context = context_dict)


@analysis_view.post("/{video_id}")
async def delete_graphs(video_id: str):
    """Deletes created graphs when user exits the analysis page.

    Args:
        video_id (str): Video id corressponding to which we need to delete the graphs.
    """
    
    if os.path.exists(f"static/images/word_cloud_{video_id}.png"):
        os.remove(f"static/images/word_cloud_{video_id}.png")
        
    if os.path.exists(f"static/images/classification_graph_{video_id}.png"):
        os.remove(f"static/images/classification_graph_{video_id}.png")