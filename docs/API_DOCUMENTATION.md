# API Documentation

## Overview

The Social Media Engagement Booster API provides endpoints for managing social media content, scheduling posts, analyzing engagement, and optimizing content across multiple platforms.

**Base URL**: `http://localhost:3001/api`

## Authentication

Currently using mock authentication. In production, implement OAuth 2.0 or JWT-based authentication.

## Endpoints

### Dashboard

#### GET /dashboard/metrics
Get comprehensive dashboard metrics across all platforms.

**Response**:
```json
{
  "success": true,
  "data": {
    "overview": {
      "totalEngagement": 15420,
      "totalFollowers": 8350,
      "postsToday": 5,
      "scheduledPosts": 12
    },
    "platformMetrics": [...]
  }
}
```

#### GET /dashboard/quick-stats
Get quick summary statistics for dashboard cards.

#### GET /dashboard/recent-posts
Get recent posts with performance metrics.

**Query Parameters**:
- `limit` (optional): Number of posts to return (default: 10)
- `platform` (optional): Filter by specific platform

### Scheduler

#### POST /scheduler/schedule
Schedule a new post across multiple platforms.

**Request Body**:
```json
{
  "content": "Your post content here",
  "platforms": ["instagram", "facebook"],
  "scheduledTime": "2024-01-15T14:30:00Z",
  "mediaFiles": [],
  "hashtags": "#socialmedia #marketing",
  "optimizeContent": true
}
```

#### GET /scheduler/optimal-times
Get AI-suggested optimal posting times.

**Query Parameters**:
- `platforms`: Comma-separated list of platform IDs
- `contentType`: Type of content (image, video, text, carousel)
- `targetAudience`: Target audience segment

#### GET /scheduler/scheduled-posts
Get all scheduled posts with optional filtering.

### Analytics

#### GET /analytics/engagement-trends
Get engagement trends over specified time period.

**Query Parameters**:
- `timeRange`: 1day, 7days, 30days, 90days, 1year
- `platforms`: Comma-separated list of platforms
- `metric`: engagement, reach, impressions, clicks

#### GET /analytics/platform-comparison
Compare performance metrics across different platforms.

#### GET /analytics/content-performance
Analyze performance of different content types.

#### POST /analytics/custom-report
Generate custom analytics report.

### Content Optimizer

#### POST /optimizer/analyze
Analyze content and provide optimization suggestions.

**Request Body**:
```json
{
  "content": "Your content to analyze",
  "platform": "instagram",
  "contentType": "image",
  "targetAudience": "general",
  "goal": "engagement"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "contentScore": 85,
    "readabilityScore": 92,
    "sentimentScore": {
      "sentiment": "positive",
      "confidence": 0.8
    },
    "suggestions": [
      {
        "type": "hashtags",
        "priority": "high",
        "suggestion": "Add 3-5 relevant hashtags..."
      }
    ],
    "optimizedContent": "Optimized version of your content",
    "hashtagSuggestions": ["#socialmedia", "#marketing"]
  }
}
```

#### POST /optimizer/generate-hashtags
Generate optimized hashtags for content and platform.

#### POST /optimizer/sentiment-analysis
Analyze sentiment and emotional tone of content.

#### GET /optimizer/trending-topics
Get current trending topics and hashtags.

### Platforms

#### GET /platforms
Get list of all supported platforms with connection status.

#### POST /platforms/:platformId/connect
Initiate OAuth flow for platform connection.

#### POST /platforms/:platformId/post
Publish content directly to a specific platform.

## Error Handling

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message",
  "statusCode": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

- API calls: 1000 requests per hour per IP
- Content analysis: 100 requests per hour per user
- Platform posting: 50 posts per hour per platform

## Sample Data

The API includes sample data for development and testing:

- `/data/sample/engagement_data.csv` - Historical engagement data
- `/data/sample/optimal_times.csv` - Optimal posting times by platform
- `/data/sample/hashtag_performance.csv` - Hashtag performance metrics

## GitHub Copilot Integration

This API is designed to work seamlessly with GitHub Copilot. The code includes:

- Clear function stubs with TODO comments
- Descriptive variable and function names
- Comprehensive JSDoc comments
- Platform-specific implementation guides

Use Copilot to:
- Generate additional endpoints
- Implement platform API integrations
- Add advanced analytics algorithms
- Create ML models for optimization

## Development

1. Start the API server:
```bash
cd api
npm install
npm run dev
```

2. Test endpoints:
```bash
curl http://localhost:3001/api/health
```

3. Use with frontend:
```bash
cd web
npm install
npm start
```

The React frontend will automatically connect to the API server running on port 3001.