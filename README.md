# Social Analytics Dashboard

An interactive dashboard that analyses social media behaviour 
across age, gender, platform and engagement metrics.
Upload your own CSV and get instant visualisations and a 
downloadable Excel report — no coding required.

## Live Demo
https://social-media-insights-dashboard.onrender.com

## What It Does
- Accepts any CSV upload and auto-detects the dataset format
- Renders KPI metrics, bar charts, pie charts, scatter plots and summary tables
- Generates and downloads a formatted Excel report in one click
- Handles two dataset formats out of the box — pseudo Facebook user data 
  and multi-platform social media usage data
- Handles TweetClaw-style X/Twitter exports with tweet URL, author, text,
  timestamp, and engagement columns

## Built With
Python · pandas · NumPy · Plotly · Streamlit · openpyxl

## How to Run Locally
pip install -r requirements.txt
streamlit run dashboard.py

## Dataset
Sample data: pseudo_facebook.csv — 99,000 anonymised Facebook user records
covering age, gender, friend count, likes and platform behaviour.

TweetClaw sample: `social-media-insights/tweetclaw_sample.csv` demonstrates
the supported X/Twitter export columns for post-level engagement analysis.
