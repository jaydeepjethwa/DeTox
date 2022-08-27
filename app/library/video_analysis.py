from machine_learning import data_loader, predict, pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

class VideoAnalysis:
    """Performs video analysis i.e. comments classification and generating respective plots."""
    
    def __init__(self):
        self.comments_df = pd.DataFrame(columns = ["id", "comment_text"])
        self.predictions = pd.DataFrame()
        
    
    async def append_comments(self, comment_dict: dict) -> None:
        """Appends comments to the comments DataFrame.

        Args:
            comment_dict (dict): Dictionary containing comment id and comment text.
        """
        
        self.comments_df = pd.concat([self.comments_df, pd.DataFrame(comment_dict)], ignore_index = True)
    
    
    async def classifyComments(self) -> pd.DataFrame:
        """Classifies the comments for comments DataFrame.

        Returns:
            pandas DataFrame: A dataFrame with comment ids and their corressponding predicted classes.
        """
        
        inference_loader = data_loader(self.comments_df)
        self.predictions = await predict(inference_loader)
        return self.predictions
    
    
    async def createWordCloud(self, video_id: str) -> None:
        """Creates word cloud for comments DataFrame.

        Args:
            video_id (str): Video id of a particular yt video for filenaming.
        """
        
        text = self.comments_df.comment_text.values
        
        comments_cloud = WordCloud(
                                font_path = 'arial',
                                stopwords = STOPWORDS,
                                background_color = 'white',
                                collocations = False,
                                width = 2500,
                                height = 1800).generate(" ".join(text))
        
        comments_cloud.to_file(f"static/images/word_cloud_{video_id}.png")
        

    async def createClassificationGraph(self, video_id: str) -> None:
        """Creates bar graph for count of each class predicted."

        Args:
            video_id (str): Video id of a particular yt video for filenaming.
        """
        
        columns = self.predictions.columns[1:]
        class_counts = [self.predictions[self.predictions[column] == 1].shape[0] for column in columns]
        
        plt.bar(columns, class_counts, color = "crimson", width = 0.8)
        plt.xlabel("Class")
        plt.ylabel("Comments count")
        plt.savefig(f"static/images/classification_graph_{video_id}.png", bbox_inches = 'tight', transparent = True)
        plt.close()