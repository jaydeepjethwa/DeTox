import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from machine_learning import predict

class VideoAnalysis:
    """Performs video analysis i.e. comments classification and generating respective plots."""
    
    def __init__(self) -> None:
        """Constructor for the class. Initializes comments and predictions dataframes"""
        
        self.comments_df = pd.DataFrame(columns = ["id", "comment_text"])
        self.predictions = pd.DataFrame()
        
    
    def appendComments(self, comment_dict: dict) -> None:
        """Appends comments dict received from api call to the comments DataFrame.

        Args:
            comment_dict (dict): Dictionary containing comment id and comment text.
        """
        
        self.comments_df = pd.concat([self.comments_df, pd.DataFrame(comment_dict)], ignore_index = True)
    
    
    def classifyComments(self) -> None:
        """Classifies the comments for comments DataFrame."""
         
        self.predictions = predict(self.comments_df)
        
    
    def getToxicIds(self) -> list:
        """Identifies comment ids which have toxicity in them and returns their list.

        Returns:
            list: Comment Ids of toxic comments.
        """
        
        toxic_ids = self.predictions[self.predictions.isin([1]).any(axis=1)]["id"].to_list()
        return toxic_ids
    
    
    def createWordCloud(self, video_id: str) -> None:
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
        

    def createClassificationGraph(self, video_id: str) -> None:
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