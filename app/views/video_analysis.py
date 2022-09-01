import os

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetchVideoComments, rejectComments
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
    if "channel_data" not in request.session:
        return RedirectResponse(request.url_for("home"))
    
    # fetch comments for given video id and form pandas dataframe
    analysis_obj = VideoAnalysis()
    
    try:
        comment_itr = fetchVideoComments(request.session["credentials"], video_id)
        
        # get every batch of comments by iterating over async generator object and append to dataframe
        async for comment_dict in comment_itr:
            analysis_obj.appendComments(comment_dict)
        
    except QuotaExceededError: # request quota is exceeded
        return HTMLResponse("Cannot connect to youtube right now. Please comeback in a while.")
    
    except AccessTokenExpiredError: # get fresh access token using refresh token
        request.session["redirect_url"] = str(request.url)
        return RedirectResponse(request.url_for("refresh_access_token"))
    
    except EntityNotFoundError: # no comments found
        has_comments = False
    
    else:
        has_comments = True

        # make predictions and necessary graphs
        analysis_obj.classifyComments()
        analysis_obj.createWordCloud(video_id)
        analysis_obj.createClassificationGraph(video_id)
        
        # get toxic comment ids and store in session for accessing if user chooses to reject them
        toxic_ids = analysis_obj.getToxicIds()
        request.session["channel_data"]["video_data"][video_id]["toxic_ids"] = toxic_ids
    
    context_dict = {
        "request": request,
        "channel_details": request.session["channel_data"]["channel_details"],
        "video": request.session["channel_data"]["video_data"][video_id],
        "video_id": video_id,
        "has_comments": has_comments
    }
    
    return templates.TemplateResponse("video_analysis.html", context = context_dict)


@analysis_view.delete("/delete-graphs/{video_id}")
async def delete_graphs(video_id: str):
    """Deletes created graphs when user exits the analysis page.

    Args:
        video_id (str): Video id corressponding to which we need to delete the graphs.
    """
    
    if os.path.exists(f"static/images/word_cloud_{video_id}.png"):
        os.remove(f"static/images/word_cloud_{video_id}.png")
        
    if os.path.exists(f"static/images/classification_graph_{video_id}.png"):
        os.remove(f"static/images/classification_graph_{video_id}.png")
        
    return Response(status_code = 200)
        

@analysis_view.get("/reject-comments/{video_id}")
async def reject_comments(request: Request, video_id: str):
    """Sets moderation status of the identified toxic comment ids as 'rejected' so that they aren't displayed.

    Args:
        request (Request): A Request object containing request data sent from client side.
        video_id (str): Video id corresponding to which analysis to be done.

    Returns:
        RedirectResponse: Redirects to analysis view where updated comments summary and classification graph will be displayed post toxic comment deletion.
    """
    
    # check if required data is present in session or someone has hit this url directly
    if "toxic_ids" not in request.session["channel_data"]["video_data"][video_id]:
        return RedirectResponse(request.url_for("video_analysis", video_id = video_id))
    
    toxic_ids = request.session["channel_data"]["video_data"][video_id]["toxic_ids"]
    
    try:
        await rejectComments(request.session["credentials"], toxic_ids)
    
    except QuotaExceededError: # request quota is exceeded
        return HTMLResponse("Cannot connect to youtube right now. Please comeback in a while..")
    
    except AccessTokenExpiredError: # get fresh access token using refresh token
        request.session["redirect_url"] = str(request.url)
        return RedirectResponse(request.url_for("refresh_access_token"))
    
    # delete toxic ids from session to prevent not found error if url hit directly
    del request.session["channel_data"]["video_data"][video_id]["toxic_ids"]
    
    return RedirectResponse(request.url_for("video_analysis", video_id = video_id))