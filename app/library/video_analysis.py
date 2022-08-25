from turtle import color
from machine_learning import data_loader, predict, pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

class VideoAnalysis:
    
    def __init__(self):
        self.comments_df = pd.DataFrame(columns = ["id", "comment_text"])
        self.predictions = None
        
    
    async def append_comments(self, comment_dict: dict) -> None:
        self.comments_df = pd.concat([self.comments_df, pd.DataFrame.from_records([comment_dict])], ignore_index = True)
    
    
    async def classifyComments(self) -> pd.DataFrame:
        inference_loader = data_loader(self.comments_df)
        self.predictions = await predict(inference_loader)
        return self.predictions
    
    
    async def createWordCloud(self) -> None:
        text = self.comments_df.comment_text.values
        
        comments_cloud = WordCloud(
                                font_path='arial',
                                stopwords=STOPWORDS,
                                background_color='white',
                                collocations=False,
                                width=2500,
                                height=1800).generate(" ".join(text))
        
        comments_cloud.to_file("static/images/word_cloud.png")
        

    async def createClassificationGraph(self) -> None:
        columns = self.predictions.columns[1:]
        class_counts = [self.predictions[self.predictions[column] == 1].shape[0] for column in columns]
        
        plt.bar(columns, class_counts, color = "crimson", width = 0.8)
        plt.xlabel("Class")
        plt.ylabel("Comments count")
        plt.savefig("static/images/classification_graph.png", bbox_inches = 'tight', transparent = True)