import nltk
import re
import requests
import sqlite3
import openai
import praw
import numpy as np
import tensorflow as tf
from tensorflow import keras
from fastapi import FastAPI
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



from collections import Counter
import re
import praw
from googleapiclient.discovery import build
import uuid 

nltk.download("punkt")


# ---------- APP ----------
app = FastAPI(title="Social Media Engagement Booster")
# Initialize Comprehend client
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')  # Use the region you have configured

# Define the request body using Pydantic
class SuggestionRequest(BaseModel):
    hashtags: List[str]
    subreddit: str = 'popular'  # Default value for subreddit


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table('SocialMediaPosts')  # Replace with your table name


# ---------- API KEYS ----------
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF0J4QEAAAAA3Vcg3gFT3JVo9eUM1W%2BACImEw24%3Dh0i3h3Tlyrw9XkQHa905sknhnRiKe2DiMAQl5TQSF2hlbq4vYq"
openai.api_key = "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"

client = OpenAI(api_key="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")

# Reddit API credentials
REDDIT_CLIENT_ID = "fmrNc2_P8mncY-u5s6JQJA"
REDDIT_CLIENT_SECRET = "lm1aGVBLsD2LoRGsBHqShYVLjXIfIA"
REDDIT_USER_AGENT = "social-media-engagement-booster:v1.0 (by /u/Whol3yShe3t)"

# Youtube API Credietial
YOUTUBE_API_KEY = 'AIzaSyDV4_vepluDtFe9pNRTCf6yQioCDTl9akA'
YOUTUBE_CHANNEL_ID = 'UCkNBKR-21a9Ly9zjRtU6d1Q'

FACEBOOK_ACCESS_TOKEN = 'your_facebook_access_token'
FACEBOOK_PAGE_ID = 'your_facebook_page_id'

#instagram API
INSTAGRAM_ACCESS_TOKEN = 'IGAAKEl50wlcxBZAE5NVGdfSVpZATm5NMl92Mkl1NzhZAY2dkNGtJRUt5OGg2bjVJbXp0NmxWczhvdzdIdWxOVTlBYjgwbHJlZAzgzVTNIVHZAXaEQ1SktBUW0zR0NVUjBnUWZAPSUNueXFLb2JSdGoxT0pSbFpFOVZAXYWRiOWpFeGZA0MAZDZD'
INSTAGRAM_USER_ID = '17841460374471491'

# Set up Twitter API credentials
auth = tweepy.OAuthHandler('HIoZKhcM3OTyP3iFP0OwD6MDg', 'Ql6XNRLPcqisINd6xpoKpaCgPZNNq8SxxrxdZE2KeukYbJxwPG')
auth.set_access_token('782405483265036288-oeoXB99BqUdbgktvWI0CJmZWDDQcrf7', 'VIP1kTWvmHIPdf2IUGKx3nWM8JbGIGO90JVvqwNm9PsXs')
api = tweepy.API(auth)



# ---------- DATABASE ----------
conn = sqlite3.connect("engagement.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trend TEXT,
    suggested_post TEXT,
    prediction TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

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

# ---------- HELPERS ----------
def fetch_twitter_trending(woeid: int = 1, limit: int = 10):
    """Fetch trending topics from Twitter using Tweepy."""
    try:
        trends = api.get_place_trends(id=woeid)
        trending_topics = []
        for trend in trends[0]['trends'][:limit]:
            trending_topics.append({
                "name": trend['name'],
                "tweet_volume": trend['tweet_volume'],
                "url": trend['url']
            })
        return trending_topics
    except tweepy.errors.TweepyException as e:
        print(f"Error fetching trends: {e}")
        return []



def extract_keywords(text_list):
    """Simple keyword extraction from list of texts"""
    words = []
    for txt in text_list:
        tokens = nltk.word_tokenize(txt.lower())
        tokens = [re.sub(r"\W+", "", t) for t in tokens if t.isalpha()]
        words.extend(tokens)
    return Counter(words).most_common(10)

def save_generated_post(trend, suggested_post, prediction, sentiment_score):
    """Save generated post data to DynamoDB"""
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4()),  # Generate unique ID
            'trend': trend,
            'suggested_post': suggested_post,
            'prediction': prediction,
            'sentiment_score': sentiment_score
        }
    )
    return response

#------------Aws s3 --------------

# Initialize AWS S3 client
s3 = boto3.client('s3', region_name='us-west-2')  # Replace with your region

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

# Preprocess function for cleaning and tokenizing text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\W+', ' ', text)  # Remove non-alphabetical characters
    tokens = nltk.word_tokenize(text)  # Tokenize text into words
    return ' '.join(tokens)

# Example of how to preprocess and structure data
def prepare_data(posts):
    # Assuming posts is a list of dictionaries with 'text' and 'label' (0 or 1)
    texts = [preprocess_text(post['text']) for post in posts]
    labels = [post['label'] for post in posts]
    
    return texts, labels

# Save model and tokenizer after training
def save_model(model, tokenizer, model_filename="model.h5", tokenizer_filename="tokenizer.pkl"):
    model.save(model_filename)
    with open(tokenizer_filename, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Load saved model and tokenizer
def load_model_and_tokenizer(model_filename="model.h5", tokenizer_filename="tokenizer.pkl"):
    model = keras.models.load_model(model_filename)
    with open(tokenizer_filename, 'rb') as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer

# Helper function to fetch Reddit data
def fetch_reddit_data(query: str , limit=10):
    url = f"https://www.reddit.com/search.json?q={query}&limit={limit}"
    res = requests.get(url, headers={"User-agent": "engagement-bot"})
    return res.json()


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





# # Helper function to fetch Instagram data
# def fetch_instagram_data():
#     """Fetch Instagram posts from the user's account"""
#     url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media?fields=id,caption,media_type,media_url&access_token={INSTAGRAM_ACCESS_TOKEN}"
#     response = requests.get(url)
#     return response.json().get("data", [])

# ---------- ML MODEL ----------
def build_lstm_model(vocab_size, input_length):
    model = keras.Sequential([
        keras.layers.Embedding(input_dim=vocab_size, output_dim=100, input_length=input_length),
        keras.layers.LSTM(64, return_sequences=True),
        keras.layers.GlobalAveragePooling1D(),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')  # Output layer for binary classification
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def prepare_data_with_embeddings(posts, tokenizer, max_length=100):
    texts, labels = prepare_data(posts)
    sequences = tokenizer.texts_to_sequences(texts)
    data = keras.preprocessing.sequence.pad_sequences(sequences, maxlen=max_length, padding='post')
    return data, np.array(labels)

cache = {}




#testing and trainitn ANN
def train_model(posts):
    texts, labels = prepare_data(posts)
    
    # Tokenize and pad sequences to a fixed length
    tokenizer = keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    data = keras.preprocessing.sequence.pad_sequences(sequences, padding='post')
    
    # Convert labels to numpy array
    labels = np.array(labels)
    
    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(data, labels, test_size=0.2, random_state=42)
    
    # Build the model
    model = build_lstm_model(vocab_size=len(tokenizer.word_index) + 1, input_length=data.shape[1])
    
    # Train the model
    model.fit(X_train, y_train, epochs=5, validation_data=(X_val, y_val))

    model.save("trend_predict_model.h5")
    with open("tokenizer.pkl", "wb") as f:
        pickle.dump(tokenizer, f)

    
    return model, tokenizer

def load_model_and_tokenizer():
    model = keras.models.load_model("trend_predict_model.h5")
    with open('tokenizer.pkl', 'rb') as handle:
        tokenizer = pickle.load(handle)
    return model, tokenizer

# Load ML model once
try:
    model, tokenizer = load_model_and_tokenizer()
except:
    model, tokenizer = None, None





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



def fetch_facebook_insights():
    """Fetch detailed Facebook Page insights (clicks, views, shares)"""
    
    # Fetch Facebook Page posts with insights (engagement, shares, likes, etc.)
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/posts?fields=id,message,shares,likes.summary(true),insights.metric(post_engaged_users,post_clicks,post_impressions)&access_token={FACEBOOK_ACCESS_TOKEN}"
    
    response = requests.get(url)
    data = response.json()

    # Prepare insights for each post
    post_insights = []
    
    for post in data.get("data", []):
        post_id = post["id"]
        message = post.get("message", "")
        shares = post.get("shares", {}).get("count", 0)
        likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
        clicks = next((item['values'][0] for item in post.get("insights", {}).get("data", []) if item['name'] == 'post_clicks'), 0)
        impressions = next((item['values'][0] for item in post.get("insights", {}).get("data", []) if item['name'] == 'post_impressions'), 0)
        engaged_users = next((item['values'][0] for item in post.get("insights", {}).get("data", []) if item['name'] == 'post_engaged_users'), 0)
        
        post_insights.append({
            "post_id": post_id,
            "message": message,
            "shares": shares,
            "likes": likes,
            "clicks": clicks,
            "impressions": impressions,
            "engaged_users": engaged_users
        })
    
    return post_insights

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



def fetch_instagram_hashtag_posts(hashtag, access_token=INSTAGRAM_ACCESS_TOKEN):
    """Fetch Instagram posts for a trending hashtag and analyze engagement"""
    
    # First, search for the hashtag ID
    hashtag_search_url = f'https://graph.instagram.com/v12.0/ig_hashtag_search'
    hashtag_search_params = {
        'user_id': INSTAGRAM_USER_ID,
        'q': hashtag,
        'access_token': access_token
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
        'access_token': access_token,
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

@app.post("/twitter_trending")
def get_twitter_trending(req: TrendRequest):
    """Fetch trending topics from Twitter based on WOEID"""
    woeid = 1154781  # Default WOEID for Malaysia
    
    # Fetch trending topics using the function
    trending_topics = fetch_twitter_trending(woeid, req.limit)
    
    # If no topics are found, return a message
    if not trending_topics:
        return {"message": "No trending topics available at the moment."}
    
    return {"trending_topics": trending_topics}

@app.get("/social_media_statistics")
def get_social_media_statistics():
    # Fetch Instagram statistics (views, clicks, shares)
    instagram_stats = fetch_instagram_insights()

    # # Fetch Facebook statistics (clicks, views, shares)
    # facebook_stats = fetch_facebook_insights()

    # Fetch Reddit statistics (upvotes, comments, engagement)
    #reddit_stats = fetch_reddit_engagement("some_subreddit")

    # # Fetch YouTube statistics (views, likes, comments, shares)
    youtube_stats = fetch_youtube_video_stats()
    
    return {
        "instagram_statistics": instagram_stats,
        # "facebook_statistics": facebook_stats,
        # "reddit_statistics": reddit_stats,
        # "youtube_statistics": youtube_stats,
    }


@app.post("/generate_post")
def generate_post(req: GenerateRequest):
    # Create a prompt as usual
    user_prompt = f"Based on the trend '{req.trend}', create a short, catchy social media post with emojis and hashtags."
    
    # ✅ Use messages instead of prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can use gpt-5 if you have access
        messages=[
            {"role": "system", "content": "You are a social media expert that writes viral posts."},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=100
    )

    # ✅ Extract text correctly (new format)
    post_text = response.choices[0].message.content.strip()
    
    # Run sentiment analysis
    sentiment_score = get_sentiment(post_text)
    
    # No ML prediction yet, so mark as None or "Pending"
    prediction = None  
    
    # Save to DB
    save_generated_post(req.trend, post_text, prediction, sentiment_score)

    return {
        "trend": req.trend, 
        "suggested_post": post_text, 
        "prediction": prediction, 
        "sentiment_score": sentiment_score
    }


@app.post("/predict_trend")
def predict_trend(req: TrendRequest):
    text = preprocess_text(req.query)
    model, tokenizer = load_model_and_tokenizer()
    sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = keras.preprocessing.sequence.pad_sequences(sequence, padding='post', maxlen=100)
    prediction = model.predict(padded_sequence)

    sentiment_score = get_sentiment(req.query)
    trending = 'Yes' if prediction[0][0] > 0.5 else 'No'

    return {
        "query": req.query,
        "predicted_trend": trending,
        "prediction_confidence": prediction[0][0],
        "sentiment_score": sentiment_score
    }

@app.get("/history")
def get_history():
    """Fetch all generated posts from DB"""
    cursor.execute("SELECT * FROM posts ORDER BY id DESC")
    rows = cursor.fetchall()
    return {
        "history": [
            {
                "id": r[0],
                "trend": r[1],
                "suggested_post": r[2],
                "prediction": r[3],
                "sentiment_score": r[4]
            } for r in rows
        ]
    }

from fastapi import FastAPI
import requests


