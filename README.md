# DeTox

A web-app that detects toxicity (curse, insult, threat, hate, etc.) in
YouTube comments and deletes them.

### Contents:
- <b>notebooks</b> - Jupyter Notebooks containing exploratory data analysis, training and evaluation part of the machine learning model.
- <b>app</b> - Implementation of the web-app which connects to youtube account, displays channel data, analyzes latest three video's and deletes (rejects) toxic comments found in them.

### Dataset:
- [Toxic Comment Classification Challenge - Kaggle](https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge/data)

### Summary of Implementation:

- Performed exploratory data analysis on the data such as finding no. of instances per class, finding null values, determining max len for the comment.
- Divided the data into train and test set by using stratified sampling technique to maintain class ratio in both set.
- Fine-tuned the BERT model using PyTorch and Hugging Face transformers libraries, evaluated its performance and saved the model.
- Developed a web-app that connects with youtube, accesses the comments of videos and deletes (rejects) toxic comments using FastAPI Framework.
- Used Google OAuth 2.0 and YouTube Data API to authorize and get access to youtube channel.
- Created various views (web-pages) that helps user to navigate through the web-app.
- Integrated the trained ML model with the web-app to classify and delete comments of the selected video.

### Web-App Screenshots:
<div>
  <h4>Landing Page:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/landing_page.png"><br>
  <h4>Google Authorization Screen:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/auth_screen.png"><br>
  <h4>Home Page:</h4>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/home_page.png"><br>
  <h4>Video Analysis Page:</h4>
  <h5>Before removing toxic comments</h5>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/video_analysis_page_before.png">
  <h5>After removing toxic comments</h5>
  <img src="https://github.com/Jaydeep2401/DeTox/blob/main/app-ui/video_analysis_page_after.png">
</div>
