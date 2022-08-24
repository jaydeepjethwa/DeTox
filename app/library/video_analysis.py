from machine_learning import data_loader, predict, pd
from library.youtube import fetch_video_comments

class VideoAnalysis:
    
    def __init__(self):
        self.__comments_df = pd.DataFrame(columns = ["id", "comment_text"])
        
    
    async def append_comments(self, comment_dict: dict) -> None:
        self.__comments_df = pd.concat([self.__comments_df, pd.DataFrame.from_records([comment_dict])], ignore_index = True)
    
    
    async def classifyComments(self):
        inference_loader = data_loader(self.__comments_df)
        preds = await predict(inference_loader)
        return preds
        
    