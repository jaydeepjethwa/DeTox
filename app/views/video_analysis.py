from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse

from library.youtube import fetch_video_comments
from library.video_analysis import VideoAnalysis

from config import templates

analysis_view = APIRouter()

@analysis_view.get("/{video_id}")
async def video_analysis(request: Request, video_id: str):
    
    # check if required data is present in session or someone has hit this url directly
    if "credentials" and "channel_data" not in request.session:
        return RedirectResponse(request.url_for("home"))
    
    # fetch comments for given video id and form pandas dataframe
    analysis_obj = VideoAnalysis()
    
    credentials = await make_comments_dataframe(request.session["credentials"], video_id, analysis_obj)
    request.session["credentials"] = credentials
    
    preds = await analysis_obj.classifyComments()
    await analysis_obj.createWordCloud(video_id)
    await analysis_obj.createClassificationGraph(video_id)
    # print(preds)
    # try:
    
        
    # except HTTPException(status_code = 503):
    #         return HTMLResponse("There was an issue in fetching data from youtube. Please comeback in a while.")
    
    context_dict = {
        "request": request,
        "channel_details": request.session["channel_data"]["channel_details"],
        "video": request.session["channel_data"]["video_data"][video_id],
    }
    
    return templates.TemplateResponse("video_analysis.html", context = context_dict)


# api allows fetching only 100 comments at a time hence repeat to fetch all comments
async def make_comments_dataframe(credentials, video_id, analysis_obj):
    
    comment_response = await fetch_video_comments(credentials, video_id)
    
    while comment_response:
        
        credentials = comment_response["credentials"]
        comment_threads = comment_response["comment_threads"]
        
        for comment in comment_threads["items"]:
            await analysis_obj.append_comments(
                {
                    "id": comment['snippet']['topLevelComment']['id'], 
                    "comment_text": comment['snippet']['topLevelComment']['snippet']['textDisplay']
                }
            )
            
        if "nextPageToken" in comment_threads:
            pageToken = comment_threads["nextPageToken"]
            comment_response = await fetch_video_comments(credentials, video_id, pageToken)
        else:
            break
        
    return credentials