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

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import openai
import sqlite3
import nltk
from collections import Counter
import re
import praw

nltk.download("punkt")


# ---------- APP ----------
app = FastAPI(title="Social Media Engagement Booster")
# Initialize Comprehend client
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')  # Use the region you have configured


# ---------- API KEYS ----------
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF0J4QEAAAAA3Vcg3gFT3JVo9eUM1W%2BACImEw24%3Dh0i3h3Tlyrw9XkQHa905sknhnRiKe2DiMAQl5TQSF2hlbq4vYq"
openai.api_key = "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"

client = OpenAI(api_key="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")

# Reddit API credentials
REDDIT_CLIENT_ID = "fmrNc2_P8mncY-u5s6JQJA"
REDDIT_CLIENT_SECRET = "lm1aGVBLsD2LoRGsBHqShYVLjXIfIA"
REDDIT_USER_AGENT = "social-media-engagement-booster:v1.0 (by /u/Whol3yShe3t)"

# Set up Twitter API credentials
auth = tweepy.OAuthHandler('HIoZKhcM3OTyP3iFP0OwD6MDg', 'Ql6XNRLPcqisINd6xpoKpaCgPZNNq8SxxrxdZE2KeukYbJxwPG')
auth.set_access_token('782405483265036288-oeoXB99BqUdbgktvWI0CJmZWDDQcrf7', 'VIP1kTWvmHIPdf2IUGKx3nWM8JbGIGO90JVvqwNm9PsXs')
api = tweepy.API(auth)

# Instagram API credentials
INSTAGRAM_ACCESS_TOKEN = "your_instagram_access_token"
INSTAGRAM_USER_ID = "your_instagram_user_id"

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
    cursor.execute("INSERT INTO posts (trend, suggested_post, prediction, sentiment_score) VALUES (?, ?, ?, ?)",
                   (trend, suggested_post, prediction, sentiment_score))
    conn.commit()

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
