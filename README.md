# DeTox

A web-app that detects toxicity (curse, insult, threat, hate, etc.) in
YouTube comments and deletes them.

### Contents:
- <b>notebooks</b> - Jupyter Notebooks containing exploratory data analysis, training and evaluation part of the machine learning model.
- <b>app</b> - Implementation of the web-app which connects youtube account, displays channel data and analyzes video (latest 3) comments.

### Dataset:
- [Toxic Comment Classification Challenge - Kaggle](https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge/data)

### Summary of Implementation:

- Performed exploratory data analysis on the data such as finding no. of instances per class, finding null values, determining max len for the comment.
- Divided the data into train and test set by using stratified sampling technique to maintain class ratio in both set.
- Fine-tuned the BERT model using PyTorch and Hugging Face transformers libraries and evaluated its performance and saved the model.
- Developed a web-app that connects with youtube and allows accessing and deleting comments using FastAPI Framework.
- Used Google OAuth 2.0 and YouTube Data API to authorize and get access to youtube channel data.
- Integrated the trained ML model with the web app to classify comments of selected video.
- Created various views (web-pages) that helps user to navigate through the web-app.

### Web-App Screenshots:
<div>
  <h4>Landing Page:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/landing_page.png"><br>
  <h4>Home Page:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/home_page.png"><br>
  <h4>Video Analysis Page:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/video_analysis_page.png">
</div>
