import nltk
import re
import requests
import sqlite3
import openai
import praw
import numpy as np
import tensorflow as tf
from tensorflow import keras
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from sklearn.model_selection import train_test_split
from textblob import TextBlob
from collections import Counter
import pickle
import time
from openai import OpenAI
import boto3
nltk.download('punkt')
import tweepy
from flask import Flask, request, jsonify
from datetime import datetime
from typing import List, Dict
import base64
import os
from dotenv import load_dotenv
import json
from typing import Optional
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from fastapi import UploadFile, File, HTTPException
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel




from config import refresh_youtube_token, refresh_reddit_token 

# Load .env file
load_dotenv()


# Load credentials from your JSON file
def get_youtube_credentials():
    with open("youtube_credentials.json", "r") as f:
        creds_data = json.load(f)

    return Credentials(
        token=None,
        refresh_token=refresh_youtube_token(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )





from collections import Counter
import re
import praw
from googleapiclient.discovery import build
import uuid 

nltk.download("punkt")


# ---------- APP ----------
app = FastAPI(title="Social Media Engagement Booster")


# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (You can specify ["http://localhost:5173"] for specific origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Initialize Comprehend client
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')  # Use the region you have configured

# Define the request body using Pydantic
class SuggestionRequest(BaseModel):
    hashtags: List[str]
    subreddit: str = 'popular'  # Default value for subreddit


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table('SocialMediaPosts')  # Replace with your table name



# DynamoDB setup
# DynamoDB client
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION", "ap-southeast-1"),  # Malaysia/Singapore region
)


s3_client = boto3.client("s3")  # creds & region auto-loaded from aws configure
S3_BUCKET_NAME = "mejuicybucket"

# ---------- API KEYS ----------

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")


# Youtube API Credietial
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
YOUTUBE_client_id = os.getenv("YOUTUBE_client_id")
YOUTUBE_client_secret = os.getenv("YOUTUBE_client_secret")
YOUTUBE_refresh_token = os.getenv("YOUTUBE_refresh_token")
YOUTUBE_access_token = os.getenv("YOUTUBE_access_token")
# Path to the JSON file you downloaded from Google Cloud Console
CLIENT_SECRET_FILE = "D:\Coding shit\Hackaton\client_secrects.json"

#instagram API
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
Meta_ACCESS_TOKEN = os.getenv("Meta_ACCESS_TOKEN")




# ---------- DATABASE ----------

# Initialize Reddit API with PRAW
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

# ---------- MODELS ----------
class TrendRequest(BaseModel):
    query: str

class GenerateRequest(BaseModel):
    trend: str

class TrendRequest(BaseModel):
    mode: str = "trending"  # "search" or "trending"
    query: str | None = None
    subreddit: str = "all"
    time: str = "day"  # only used for "top"
    limit: int = 10

# ✅ Request model for creating a post
class AutoPostRequest(BaseModel):
    platform: str   # instagram, reddit, youtube
    post_id: str    # IG media id / Reddit submission id / YouTube video id
    content: Dict   # {caption, hashtags, media_url...}
    status: str     # posted, failed
    metrics: Optional[Dict] = None

class PostRequest(BaseModel):
    platforms: List[str]     # e.g. ["instagram", "youtube"]
    content: Dict            # your post details {caption, hashtags, media_url}
    scheduled_time: Optional[str] = None  # optional if you plan to add scheduling
# ---------- HELPERS ----------




def extract_keywords(text_list):
    """Simple keyword extraction from list of texts"""
    words = []
    for txt in text_list:
        tokens = nltk.word_tokenize(txt.lower())
        tokens = [re.sub(r"\W+", "", t) for t in tokens if t.isalpha()]
        words.extend(tokens)
    return Counter(words).most_common(10)



#------------Aws s3 --------------

# Initialize AWS S3 client
s3 = boto3.client('s3', region_name='ap-southeast-1')  # Replace with your region

# Upload file to S3
def upload_to_s3(file_path, bucket_name, object_name):
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"File uploaded to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Error uploading file: {e}")

# Example usage
upload_to_s3("trend_predict_model.h5", "your-s3-bucket", "models/trend_predict_model.h5")

def download_from_s3(bucket_name, object_name, download_path):
    try:
        s3.download_file(bucket_name, object_name, download_path)
        print(f"File downloaded to {download_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

sagemaker_runtime = boto3.client('runtime.sagemaker')

def get_predictions_from_sagemaker(endpoint_name, data):
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=data
    )
    result = response['Body'].read().decode('utf-8')
    return result

#------------------------------------------------------------------


# Helper function to fetch Reddit data
def fetch_reddit_data(query: str , limit=10):
    url = f"https://www.reddit.com/search.json?q={query}&limit={limit}"
    res = requests.get(url, headers={"User-agent": "engagement-bot"})
    return res.json()


def upload_to_s3(file_path, filename):
    """Upload file to S3 and return URL"""
    s3_client.upload_file(file_path, S3_BUCKET_NAME, filename)
    url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"
    return url


def save_post_history(platform, post_id, content, status):
    """Save post history into DynamoDB"""
    item = {
        "platform": platform,
        "post_id": post_id,
        "status": status,
        "content": json.dumps(content),   # store content as JSON string
        "timestamp": datetime.utcnow().isoformat() 
    }
    table.put_item(Item=item)
    print(f"✅ Saved post history for {platform} (ID: {post_id})")

def fetch_reddit_trending(subreddit="all", time="day", limit=10):
    # Hot posts
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    # Or swap with top: 
    # url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time}&limit={limit}"
    res = requests.get(url, headers={"User-agent": "engagement-bot"})
    return res.json()


def get_sentiment(text):
    """Analyze sentiment using Amazon Comprehend"""
    response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    sentiment = response['Sentiment']
    sentiment_scores = response['SentimentScore']
    return sentiment, sentiment_scores














def fetch_instagram_insights():
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media"
    params = {
        "fields": "id,caption,media_type,media_url,timestamp",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    # Make the request
    response = requests.get(url, params=params)
    
    # Log the response status code and content
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Data: {response.text}")

    data = response.json()

    media_insights = []

    # Check if 'data' exists in the response
    if "data" not in data:
        print("No 'data' field found in the response.")
        return media_insights  # Return empty if no data

    # Loop through each post to fetch insights
    for post in data.get("data", []):
        media_id = post["id"]
        media_type = post.get("media_type")

        # Pick metrics based on media type
        if media_type in ["IMAGE", "VIDEO"]:
            metrics = "views,reach,likes,comments,saved,shares,total_interactions"
        elif media_type == "REELS":
            metrics = "plays,reach,likes,comments,saved,shares,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
        elif media_type == "STORY":
            metrics = "impressions,reach,navigation,profile_activity"
        else:
            metrics = "reach"  # fallback minimal metric

        insights_url = f"https://graph.instagram.com/{media_id}/insights"
        insights_params = {
            "metric": metrics,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        
        # Fetch insights for each post
        insights_data = requests.get(insights_url, params=insights_params).json()

        # Log the insights response for debugging
        print(f"Insights Response for Media ID {media_id}: {insights_data}")
        
        # Flatten insights into {metric_name: value}
        metrics_dict = {}
        if "data" in insights_data:
            for item in insights_data["data"]:
                if "values" in item and len(item["values"]) > 0:
                    metrics_dict[item["name"]] = item["values"][0].get("value", 0)

        # Extract hashtags from caption
        caption = post.get("caption", "")
        hashtags = re.findall(r"#\w+", caption)

        media_insights.append({
            "media_id": media_id,
            "caption": caption,
            "media_type": media_type,
            "media_url": post.get("media_url"),
            "timestamp": post.get("timestamp"),
            "insights": metrics_dict,   # cleaned metrics only
            "hashtags_used": hashtags,
            "hashtag_count": len(hashtags)
        })

    return media_insights





def fetch_reddit_engagement(subreddit_name="all", limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=limit)

    post_insights = []

    for post in posts:
        # Extract hashtags (words with # in title/selftext)
        hashtags = re.findall(r"#\w+", post.title + " " + (post.selftext or ""))

        post_insights.append({
            "post_id": post.id,
            "title": post.title,
            "subreddit": post.subreddit.display_name,
            "author": str(post.author),
            "url": post.url,
            "created_utc": post.created_utc,
            "score": post.score,
            "upvotes": post.ups,
            "num_comments": post.num_comments,
            "is_video": post.is_video,
            "hashtags_used": hashtags,
            "hashtag_count": len(hashtags)
        })

    return post_insights

def fetch_youtube_video_stats():
    """Fetch YouTube video statistics (views, likes, comments, shares, and titles)"""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # Fetch videos from the channel
    video_stats = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="id,snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            order="date",
            maxResults=5,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            # ✅ Ensure the result is a video (not channel/playlist)
            if item["id"]["kind"] != "youtube#video":
                continue

            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]  # Extract video title

            # Fetch detailed stats for each video
            video_request = youtube.videos().list(part="statistics", id=video_id)
            video_response = video_request.execute()

            if not video_response["items"]:
                continue  # skip if video details are missing

            video = video_response["items"][0]
            stats = video.get("statistics", {})

            video_stats.append({
                "video_id": video_id,
                "title": video_title,  # Include video title
                "views": stats.get("viewCount", 0),
                "likes": stats.get("likeCount", 0),
                "comments": stats.get("commentCount", 0),
                # ⚠️ YouTube API doesn't return "shareCount" anymore
                "shares": stats.get("shareCount", None)
            })

        # Check if there's another page of results
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break  # No more pages, exit the loop

    return video_stats


#----------------BEst timeing-------------------------------------
@app.post('/suggest_time')
async def suggest_time(request: SuggestionRequest):
    hashtags = request.hashtags  # Access the hashtags directly
    subreddit = request.subreddit
    
    if not hashtags:
        return {"error": "Please provide hashtags."}
    
    best_times = get_best_posting_times_for_platforms(hashtags, subreddit)
    return best_times

def get_best_posting_times_for_platforms(hashtags: List[str], subreddit: str):
    # Fetch best posting times for Instagram hashtags
    instagram_best_times = {}
    for hashtag in hashtags:
        peak_hour, engagement = fetch_instagram_hashtag_posts(hashtag)
        instagram_best_times[hashtag] = {'peak_hour': peak_hour, 'engagement': engagement}
    
    # Fetch best posting time for Reddit
    reddit_peak_hour, reddit_engagement = fetch_reddit_trending_best_posting_time(subreddit)
    
    # Fetch best posting time for YouTube
    youtube_peak_hour, youtube_engagement = fetch_youtube_trending_best_posting_time()
    
    return {
        'Instagram': instagram_best_times,
        'Reddit': {'peak_hour': reddit_peak_hour, 'engagement': reddit_engagement},
        'YouTube': {'peak_hour': youtube_peak_hour, 'engagement': youtube_engagement}
    }

def fetch_youtube_trending_best_posting_time():
    """Fetch the best time to post based on YouTube trending videos' engagement."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # Get trending videos (you can adjust the location or region)
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode="US",  # Adjust region as needed
        maxResults=50
    )
    response = request.execute()

    time_engagement = {}

    for video in response.get("items", []):
        # Extract creation time and engagement details
        created_time = video['snippet']['publishedAt']
        
        # Safely get viewCount, and fallback to 0 if not found
        engagement = int(video['statistics'].get('viewCount', 0))  # Use get() to avoid KeyError
        hour_of_day = int(created_time[11:13])

        if hour_of_day not in time_engagement:
            time_engagement[hour_of_day] = 0
        time_engagement[hour_of_day] += engagement
    
    # Determine peak engagement hour
    peak_hour = max(time_engagement, key=time_engagement.get, default=None)
    return peak_hour, time_engagement.get(peak_hour, 0)  # Use get() for default 0 if peak_hour is None

def fetch_reddit_trending_best_posting_time(subreddit):
    """Fetch the best time to post based on Reddit trending posts' engagement."""
    headers = {'User-Agent': 'BestPostingTimeBot'}
    url = f'https://www.reddit.com/r/{subreddit}/top.json?limit=100'
    
    response = requests.get(url, headers=headers)
    posts = response.json()['data']['children']
    
    time_engagement = {}

    for post in posts:
        created_utc = post['data']['created_utc']
        post_time = datetime.utcfromtimestamp(created_utc)
        hour_of_day = post_time.hour
        
        engagement = post['data']['ups'] + post['data']['num_comments']
        
        if hour_of_day not in time_engagement:
            time_engagement[hour_of_day] = 0
        time_engagement[hour_of_day] += engagement
    
    peak_hour = max(time_engagement, key=time_engagement.get)
    return peak_hour, time_engagement[peak_hour]



def fetch_instagram_hashtag_posts(hashtag, access_token = Meta_ACCESS_TOKEN):
    """Fetch Instagram posts for a trending hashtag and analyze engagement"""
    
    # First, search for the hashtag ID
    hashtag_search_url = f'https://graph.facebook.com/v12.0/ig_hashtag_search'
    hashtag_search_params = {
        'user_id': INSTAGRAM_USER_ID,
        'q': hashtag,
        'access_token': Meta_ACCESS_TOKEN
    }

    hashtag_search_response = requests.get(hashtag_search_url, params=hashtag_search_params)

    # Check if the hashtag search request was successful
    if hashtag_search_response.status_code != 200:
        print(f"Error in hashtag search: {hashtag_search_response.status_code}, {hashtag_search_response.text}")
        return None, 0

    hashtag_data = hashtag_search_response.json()

    if 'data' not in hashtag_data or len(hashtag_data['data']) == 0:
        print("No data found for the hashtag.")
        return None, 0  # Return None if no data found
    
    hashtag_id = hashtag_data['data'][0]['id']  # Extract hashtag ID

    # Fetch top media posts for the hashtag
    posts_url = f'https://graph.instagram.com/{hashtag_id}/top_media'
    posts_params = {
        'access_token': Meta_ACCESS_TOKEN,
        'fields': 'id,caption,media_type,like_count,comments_count,timestamp',
        'limit': 100  # Fetch up to 100 posts
    }

    posts_response = requests.get(posts_url, params=posts_params)

    # Check if the posts data is valid
    if posts_response.status_code != 200:
        print(f"Error fetching posts: {posts_response.status_code}, {posts_response.text}")
        return None, 0  # Return None if there’s an issue with the post request
    
    posts_data = posts_response.json()

    # Prepare a dictionary to store time-based engagement data
    time_engagement = {}

    for post in posts_data.get('data', []):
        created_time = post['timestamp']
        engagement = post['like_count'] + post['comments_count']
        hour_of_day = int(created_time[11:13])  # Extract the hour part from timestamp
        
        if hour_of_day not in time_engagement:
            time_engagement[hour_of_day] = 0
        time_engagement[hour_of_day] += engagement
    
    # Return peak hour and its total engagement
    if time_engagement:
        peak_hour = max(time_engagement, key=time_engagement.get)  # Get the hour with highest engagement
        return peak_hour, time_engagement[peak_hour]
    else:
        print("No posts data found for the hashtag.")
        return None, 0

#-------------AUto Post---------------------



# Function to upload media (image or video) to Instagram
def upload_media_to_instagram(media_url, caption, access_token, user_id):
    url = f"https://graph.instagram.com/{user_id}/media"
    
    # Payload to upload the media (image/video)
    payload = {
        "image_url": media_url,  # Image URL to upload
        "caption": caption,      # Caption for the post
        "access_token": INSTAGRAM_ACCESS_TOKEN  # Access token
    }
    
    # Send the request to upload media as JSON
    response = requests.post(url, json=payload).json()
    
    # Debug: Print the response to ensure the media upload was successful
    print(f"Upload response: {response}")
    
    if "id" in response:
        media_id = response["id"]  # Media ID returned from Instagram
        print(f"Media uploaded successfully! Media ID: {media_id}")
        return media_id
    else:
        error_message = response.get('error', 'Unknown error')
        print(f"Error uploading media: {error_message}")
        raise HTTPException(status_code=400, detail=f"Error uploading media: {error_message}")

# Function to publish the uploaded media as a post
def publish_post(media_id, access_token, user_id):
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media_publish"
    
    # Payload to publish the media
    payload = {
        "creation_id": media_id,  # Media ID to be published
        "access_token": INSTAGRAM_ACCESS_TOKEN   # Access token
    }
    
    # Send request to publish the media
    response = requests.post(url, json=payload).json()
    
    # Debug: Print the response to check if the post was published successfully
    print(f"Publish response: {response}")
    
    if "id" in response:
        post_id = response["id"]  # Return post_id after successful publish
        print(f"Post published successfully! Post ID: {post_id}")
        return post_id
    else:
        error_message = response.get('error', 'Unknown error')
        print(f"Error publishing post: {error_message}")
        raise HTTPException(status_code=400, detail=f"Error publishing post: {error_message}")

# Function to handle dynamic content such as media_url and caption
def auto_post_instagram(content, access_token = INSTAGRAM_ACCESS_TOKEN , user_id = INSTAGRAM_USER_ID):
    # Step 1: Upload the media
    media_id = upload_media_to_instagram(content["media_url"], content["caption"], INSTAGRAM_ACCESS_TOKEN , INSTAGRAM_USER_ID)

    # If media upload fails, return an error
    if media_id is None:
        return {"success": False, "message": "Failed to upload media"}

    # Step 2: Publish the uploaded media as a post
    post_id = publish_post(media_id, INSTAGRAM_ACCESS_TOKEN , INSTAGRAM_USER_ID)

    # Return success with the post ID
    return {"success": True, "post_id": post_id}



# Define the function for posting to Reddit
import praw

def auto_post_reddit(content):
    try:
        # Initialize the Reddit API with your credentials
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD
        )

        # Get the subreddit to post to (default is "test")
        subreddit_name = content.get("subreddit", "test")  # Use 'test' if no subreddit is provided

        # Extract content for the post
        media_url = content.get("media_url")
        text = content.get("text", "")
        caption = content.get("caption", "")

        # Check if media_url is provided (e.g., for an image or video post)
        if media_url and text:
            # Submit a post with both a URL and text content
            submission = reddit.subreddit(subreddit_name).submit(
                title=caption,
                url=media_url,  # Submit the media URL (image/video)
                selftext=text    # Include text if provided
            )
        elif media_url:
            # Submit a post with only a media URL (image/video)
            submission = reddit.subreddit(subreddit_name).submit(
                title=caption,
                url=media_url  # Only URL is provided, no text
            )
        elif text:
            # Submit a text-only post
            submission = reddit.subreddit(subreddit_name).submit(
                title=caption,
                selftext=text  # Only text is provided, no media URL
            )
        else:
            # If neither media_url nor text is provided, raise an error
            raise ValueError("Either 'selftext' or 'url' must be provided in the content.")

        # Return success with post ID
        return {"success": True, "platform": "reddit", "post_id": submission.id}

    except Exception as e:
        # Handle errors (e.g., invalid subreddit, missing content, etc.)
        return {"success": False, "error": str(e)}



def auto_post_youtube(content):
    creds = get_youtube_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": content["caption"],
                "description": " ".join(content.get("hashtags", []))
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(content["media_url"], chunksize=-1, resumable=True)
    )

    response = request.execute()
    video_id = response.get("id")

    save_post_history("youtube", video_id, content, "posted")

    return {"success": True, "post_id": video_id}



#------------------GAther ACcount DAta--------------




def check_instagram_followers(access_token = "IGAAKEl50wlcxBZAE5NVGdfSVpZATm5NMl92Mkl1NzhZAY2dkNGtJRUt5OGg2bjVJbXp0NmxWczhvdzdIdWxOVTlBYjgwbHJlZAzgzVTNIVHZAXaEQ1SktBUW0zR0NVUjBnUWZAPSUNueXFLb2JSdGoxT0pSbFpFOVZAXYWRiOWpFeGZA0MAZDZD", ig_user_id = "17841460374471491"):
    resp = requests.get(
        f"https://graph.facebook.com/v18.0/{ig_user_id}",
        params={"fields": "followers_count", "access_token": access_token}
    )
    return resp.json().get("followers_count")

def check_youtube_subscribers(access_token):
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "statistics", "mine": "true", "access_token": access_token}
    )
    return resp.json()["items"][0]["statistics"]["subscriberCount"]

def check_reddit_subscribers(access_token, subreddit):
    resp = requests.get(
        f"https://oauth.reddit.com/r/{subreddit}/about",
        headers={"Authorization": f"bearer {access_token}", "User-Agent": "MyApp/0.1"}
    )
    return resp.json()["data"]["subscribers"]

def monitor():
    while True:
        yt_token = refresh_youtube_token()
        reddit_token = refresh_reddit_token()

        ig_followers = check_instagram_followers(INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID)
        yt_subscribers = check_youtube_subscribers(yt_token)
        reddit_subscribers = check_reddit_subscribers(reddit_token, "yoursubreddit")

        print("Instagram followers:", ig_followers)
        print("YouTube subscribers:", yt_subscribers)
        print("Reddit subscribers:", reddit_subscribers)

        time.sleep(3600)  # check every hour


# Fetch Instagram Insights and return aggregated stats (new name)
def get_instagram_stats():
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media"
    params = {
        "fields": "id,caption,media_type,media_url,timestamp",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    total_likes = 0
    total_comments = 0
    total_shares = 0

    if "data" in data:
        for post in data["data"]:
            media_id = post["id"]
            insights_url = f"https://graph.instagram.com/{media_id}/insights"
            insights_params = {
                "metric": "likes,comments,shares",
                "access_token": INSTAGRAM_ACCESS_TOKEN
            }
            
            insights_data = requests.get(insights_url, params=insights_params).json()
            if "data" in insights_data:
                for item in insights_data["data"]:
                    if item["name"] == "likes":
                        total_likes += item["values"][0].get("value", 0)
                    elif item["name"] == "comments":
                        total_comments += item["values"][0].get("value", 0)
                    elif item["name"] == "shares":
                        total_shares += item["values"][0].get("value", 0)

    return {
        "likes": total_likes,
        "comments": total_comments,
        "shares": total_shares
    }

# Fetch Reddit Engagement Data and return aggregated stats (new name)
def get_reddit_engagement_stats(subreddit_name="all", limit=10):
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=limit)

    total_upvotes = 0
    total_comments = 0
    total_score = 0

    for post in posts:
        total_upvotes += post.ups
        total_comments += post.num_comments
        total_score += post.score

    return {
        "upvotes": total_upvotes,
        "comments": total_comments,
        "score": total_score
    }

# Fetch YouTube Video Stats and return aggregated stats (new name)
def get_youtube_stats():
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    total_views = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0

    next_page_token = None
    while True:
        request = youtube.search().list(
            part="id,snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            order="date",
            maxResults=5,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response.get("items", []):
            if item["id"]["kind"] != "youtube#video":
                continue
            video_id = item["id"]["videoId"]
            video_request = youtube.videos().list(part="statistics", id=video_id)
            video_response = video_request.execute()
            stats = video_response["items"][0].get("statistics", {})
            total_views += int(stats.get("viewCount", 0))
            total_likes += int(stats.get("likeCount", 0))
            total_comments += int(stats.get("commentCount", 0))
            total_shares += int(stats.get("shareCount", 0) if "shareCount" in stats else 0)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return {
        "views": total_views,
        "likes": total_likes,
        "comments": total_comments,
        "shares": total_shares
    }

# FastAPI Endpoints using new function names
@app.get("/instagram-stats")
def get_instagram_stats_endpoint():
    insights = get_instagram_stats()
    return {"instagram_stats": insights}

@app.get("/reddit-stats")
def get_reddit_engagement_stats_endpoint(subreddit: str = "all", limit: int = 10):
    insights = get_reddit_engagement_stats(subreddit, limit)
    return {"reddit_engagement_stats": insights}

@app.get("/youtube-stats")
def get_youtube_stats_endpoint():
    stats = get_youtube_stats()
    return {"youtube_video_stats": stats}


# # Endpoint to fetch Instagram data
# @app.get("/instagram_posts")
# def get_instagram_posts():
#     """Fetch posts from Instagram account"""
#     data = fetch_instagram_data()
#     return {"instagram_posts": data}

# ---------- ROUTES ----------
@app.get("/")
def root():
    return {"message": "Social Media Engagement Booster API"}




# Endpoint to fetch Reddit data
@app.post("/reddit")
def get_reddit_trend(req: TrendRequest):
    if req.mode == "search" and req.query:
        data = fetch_reddit_data(req.query, req.limit)
        posts = [
            {"title": c["data"]["title"], "url": c["data"]["url"], "score": c["data"]["score"]}
            for c in data["data"]["children"]
        ]
        return {"mode": "search", "query": req.query, "reddit_posts": posts}

    elif req.mode == "trending":
        data = fetch_reddit_trending(req.subreddit, req.time, req.limit)
        posts = [
            {"title": c["data"]["title"], "url": c["data"]["url"], "score": c["data"]["score"]}
            for c in data["data"]["children"]
        ]
        return {"mode": "trending", "subreddit": req.subreddit, "reddit_posts": posts}

    return {"error": "Invalid request. Provide query for search or mode=trending."}

# @app.get("/instagram")
# def get_instagram_posts():
#     data = fetch_instagram_data()
#     return {"instagram_posts": data}

@app.get("/instagram-stats2")
def get_instagram_stats2():
    # Fetch Instagram insights and return them as JSON
    instagram_stats = fetch_instagram_insights()
    return {"instagram_statistics": instagram_stats}


@app.get("/social_media_statistics")
def get_social_media_statistics():
    # Fetch Instagram statistics (views, clicks, shares)
    instagram_stats = fetch_instagram_insights()


    # Fetch Reddit statistics (upvotes, comments, engagement)
    reddit_stats = fetch_reddit_engagement("some_subreddit")

    # # Fetch YouTube statistics (views, likes, comments, shares)
    youtube_stats = fetch_youtube_video_stats()
    
    return {
        "instagram_statistics": instagram_stats,
        # "facebook_statistics": facebook_stats,
#"reddit_statistics": reddit_stats,
         "youtube_statistics": youtube_stats,
    }




# ✅ Fetch all post history
@app.get("/post_history")
def get_post_history():
    resp = table.scan()
    items = resp.get("Items", [])
    # Convert JSON strings back to dicts
    for item in items:
        item["content"] = json.loads(item["content"])
        item["metrics"] = json.loads(item["metrics"])
    return {"history": items}





# ✅ Update metrics for a post
class MetricsUpdateRequest(BaseModel):
    platform: str
    post_id: str
    metrics: Dict


@app.post("/update_metrics")
def update_metrics(request: MetricsUpdateRequest):
    key = {"id": f"{request.platform}_{request.post_id}"}

    table.update_item(
        Key=key,
        UpdateExpression="set metrics = :m",
        ExpressionAttributeValues={":m": json.dumps(request.metrics)},
    )
    return {"message": f"📈 Metrics updated for {request.platform}_{request.post_id}"}

# ✅ Fetch all post history
@app.get("/post_history")
def get_post_history():
    resp = table.scan()
    items = resp.get("Items", [])
    # Convert JSON strings back to dicts
    for item in items:
        item["content"] = json.loads(item["content"])
        item["metrics"] = json.loads(item["metrics"])
    return {"history": items}



@app.post("/auto_post")
async def auto_post(request: PostRequest):
    data = request.dict()  # Convert the request data to a dictionary
    results = {}

    # Check if Instagram is in the platforms list
    if "instagram" in data["platforms"]:
        print(f"Access Token: {Meta_ACCESS_TOKEN}")
        # Pass content to auto_post_instagram
        results["instagram"] = auto_post_instagram(data["content"])

    if "reddit" in data["platforms"]:
        results["reddit"] = auto_post_reddit(data["content"])

    if "youtube" in data["platforms"]:
        results["youtube"] = auto_post_youtube(data["content"])

    return {"status": "done", "results": results}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"

        # Save locally (for YouTube upload)
        local_path = f"temp_uploads/{unique_filename}"
        os.makedirs("temp_uploads", exist_ok=True)

        with open(local_path, "wb") as f:
            f.write(await file.read())

        # Upload to S3
        s3_client.upload_file(local_path, S3_BUCKET_NAME, unique_filename)
        s3_url = f"https://{S3_BUCKET_NAME}.s3.ap-southeast-1'.amazonaws.com/{unique_filename}"

        return {
            "success": True,
            "s3_url": s3_url,        # for Instagram/Reddit
            "local_path": local_path # for YouTube
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# FastAPI Endpoints
@app.get("/instagram")
def get_instagram_insights():
    insights = fetch_instagram_insights()
    return {"instagram_insights": insights}

@app.get("/reddit")
def get_reddit_engagement(subreddit: str = "all", limit: int = 10):
    insights = fetch_reddit_engagement(subreddit, limit)
    return {"reddit_engagement": insights}

@app.get("/youtube")
def get_youtube_video_stats():
    stats = fetch_youtube_video_stats()
    return {"youtube_video_stats": stats}