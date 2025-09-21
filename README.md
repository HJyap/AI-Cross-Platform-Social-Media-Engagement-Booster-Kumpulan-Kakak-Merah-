# Social Media Engagement Booster

This is an API that helps manage and boost social media engagement by fetching and posting statistics across platforms like **Instagram**, **Reddit**, and **YouTube**. It uses machine learning models for trend prediction and sentiment analysis.

---

## Table of Contents
- [Installation](#installation)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Contributors](#contributors)

---

## Installation

### Prerequisites
1. **Python 3.7+**
2. **AWS Credentials** for services such as S3, DynamoDB, and Comprehend.
3. **Google Cloud Credentials** for YouTube API integration.
4. **Instagram Meta API Token** for Instagram insights and posting.

---

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository
Install dependencies using pip:

 ```bash

pip install -r requirements.txt
Set up your environment variables. Create a .env file and set the required API credentials:
 ```
 ```ini

REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_USER_ID=your_instagram_user_id
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CHANNEL_ID=your_youtube_channel_id
 ```
Run the FastAPI server:

 ```bash

uvicorn main:app --reload
 ```
### Features
Instagram Engagement Insights: Fetch likes, comments, shares, reach, and other insights for Instagram posts.

#Reddit Engagement Stats#: Fetch Reddit posts and their engagement stats (upvotes, comments, score).

#YouTube Video Stats#: Fetch views, likes, comments, and shares for YouTube videos.

#Auto-Posting#: Automatically post content to Instagram, Reddit, or YouTube with the provided content details.

#Best Posting Time Suggestion#: Suggest the best time to post based on the engagement statistics for Instagram, Reddit, and YouTube.

#AWS S3 Upload#: Upload media files (images/videos) to an AWS S3 bucket.

## API Endpoints
### 1. Instagram Stats
GET /instagram-stats
Fetch Instagram post insights (likes, comments, shares).

GET /instagram
Fetch Instagram media insights.

### 2. Reddit Stats
GET /reddit
Fetch Reddit engagement stats (upvotes, comments, score).

### 3. YouTube Stats
GET /youtube
Fetch YouTube video stats (views, likes, comments).

### 4. Auto-Post
POST /auto_post
Automatically post content to Instagram, Reddit, or YouTube.

Request Body:

```json

{
  "platforms": ["instagram", "youtube"],
  "content": {
    "caption": "Check out this cool post!",
    "hashtags": ["#awesome", "#cool"],
    "media_url": "https://example.com/media.jpg"
  }
}
```
Response:

```json
Copy code
{
  "status": "done",
  "results": {
    "instagram": { "success": true, "post_id": "123456" },
    "youtube": { "success": true, "post_id": "abcdef" }
  }
}
```
### 5. Suggest Best Time to Post
POST /suggest_time
Suggest the best time to post on Instagram, Reddit, and YouTube based on hashtags and subreddit.

Request Body:

```json
Copy code
{
  "hashtags": ["#tech", "#AI"],
  "subreddit": "popular"
}
```
### 6. Upload Media to S3
```POST /upload```
Upload media to S3 and return the URL.

```Request: File upload.```

### 7. Social Media Statistics
```GET /social_media_statistics```
Fetch aggregated statistics for Instagram, Reddit, and YouTube.

Usage
Once the server is running, you can access the API through:

```Swagger UI → http://localhost:8000/docs

ReDoc UI → http://localhost:8000/redoc
```

You can interact with each of the endpoints using tools like Postman or curl.

For example, to fetch Instagram insights:

```

curl -X GET http://localhost:8000/instagram-stats
```
## Contributors
Leong Jun Chuen
