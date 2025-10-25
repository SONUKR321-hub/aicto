# API Documentation

This document describes the internal API of the YouTube-to-Instagram agent modules.

## Table of Contents
- [Config Module](#config-module)
- [YouTube Scraper](#youtube-scraper)
- [Video Editor](#video-editor)
- [Caption Generator](#caption-generator)
- [Instagram Poster](#instagram-poster)
- [Analytics](#analytics)
- [Scheduler](#scheduler)

---

## Config Module

### `Config(config_path: str)`

Configuration manager for the agent.

**Methods:**

#### `get(key_path: str, default: Any = None) -> Any`
Get configuration value using dot notation.

```python
config = Config()
category = config.get('content.category')
post_times = config.get('schedule.post_times', ['19:00'])
```

#### `get_env(key: str, default: Any = None) -> Any`
Get environment variable.

```python
username = config.get_env('instagram_username')
```

#### `validate() -> bool`
Validate required configuration.

```python
if not config.validate():
    print("Configuration validation failed")
```

**Properties:**
- `instagram_username`: Instagram username
- `instagram_password`: Instagram password
- `ai_provider`: AI provider ('openai' or 'anthropic')
- `openai_api_key`: OpenAI API key
- `anthropic_api_key`: Anthropic API key
- `database_path`: Path to database

---

## YouTube Scraper

### `YouTubeScraper(config: Config)`

Handles YouTube video discovery and downloading.

**Methods:**

#### `search_videos(keywords: List[str], max_results: int = 50) -> List[Dict]`
Search for videos based on keywords.

```python
scraper = YouTubeScraper(config)
videos = scraper.search_videos(['motivation shorts'], max_results=20)

# Returns list of dicts:
# {
#     'id': 'video_id',
#     'title': 'Video Title',
#     'url': 'https://youtube.com/watch?v=...',
#     'duration': 45,
#     'view_count': 100000,
#     'like_count': 5000,
#     'engagement_score': 0.05,
#     ...
# }
```

#### `download_video(video: Dict) -> Optional[str]`
Download a video from YouTube.

```python
video_path = scraper.download_video(video)
if video_path:
    print(f"Downloaded to: {video_path}")
```

#### `get_video_info(video_url: str) -> Optional[Dict]`
Get detailed information about a specific video.

```python
info = scraper.get_video_info('https://youtube.com/watch?v=...')
```

---

## Video Editor

### `VideoEditor(config: Config)`

Handles video editing and optimization for Instagram Reels.

**Methods:**

#### `process_video(video_path: str, video_id: str) -> Optional[str]`
Process video for Instagram (resize, watermark, etc.).

```python
editor = VideoEditor(config)
edited_path = editor.process_video('input.mp4', 'video123')
```

#### `add_subtitles(video_path: str, subtitles: list) -> Optional[str]`
Add subtitles to video.

```python
subtitles = [
    {'start': 0, 'end': 3, 'text': 'Hello World'},
    {'start': 3, 'end': 6, 'text': 'This is a test'},
]
subtitled_path = editor.add_subtitles(video_path, subtitles)
```

#### `get_video_duration(video_path: str) -> float`
Get video duration in seconds.

```python
duration = editor.get_video_duration('video.mp4')
print(f"Duration: {duration}s")
```

#### `extract_thumbnail(video_path: str, output_path: str = None) -> Optional[str]`
Extract thumbnail from video.

```python
thumb_path = editor.extract_thumbnail('video.mp4')
```

---

## Caption Generator

### `CaptionGenerator(config: Config)`

Generates captions and hashtags using AI.

**Methods:**

#### `generate_caption(video_info: Dict) -> Dict[str, any]`
Generate caption and hashtags for a video.

```python
caption_gen = CaptionGenerator(config)
result = caption_gen.generate_caption(video_info)

# Returns:
# {
#     'caption': 'Main caption text',
#     'hashtags': ['#motivation', '#inspire', ...],
#     'full_caption': 'Caption + hashtags combined'
# }
```

**Example:**

```python
video_info = {
    'title': 'Motivational Speech',
    'description': 'Daily motivation...',
}

result = caption_gen.generate_caption(video_info)
print(result['full_caption'])
```

---

## Instagram Poster

### `InstagramPoster(config: Config)`

Handles posting to Instagram.

**Methods:**

#### `login() -> bool`
Login to Instagram.

```python
poster = InstagramPoster(config)
if poster.login():
    print("Login successful")
```

#### `post_reel(video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Optional[Dict]`
Post a video as a Reel.

```python
post_info = poster.post_reel('video.mp4', 'Check this out! #motivation')

# Returns:
# {
#     'id': 'media_id',
#     'code': 'shortcode',
#     'url': 'https://instagram.com/reel/...',
#     'posted_at': datetime
# }
```

#### `post_video(video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Optional[Dict]`
Post a regular video.

```python
post_info = poster.post_video('video.mp4', 'Caption here')
```

#### `get_media_info(media_id: str) -> Optional[Dict]`
Get information about a posted media.

```python
info = poster.get_media_info('media_id')
# Returns: {'id', 'code', 'likes', 'comments', 'views'}
```

#### `get_account_info() -> Optional[Dict]`
Get account information.

```python
info = poster.get_account_info()
# Returns: {'username', 'full_name', 'followers', 'following', 'posts'}
```

#### `delete_media(media_id: str) -> bool`
Delete a media post.

```python
if poster.delete_media('media_id'):
    print("Deleted successfully")
```

---

## Analytics

### `Analytics(config: Config)`

Handles analytics tracking and optimization.

**Methods:**

#### `track_post(post_data: Dict) -> bool`
Track a new post.

```python
analytics = Analytics(config)
analytics.track_post({
    'video_id': 'video123',
    'instagram_media_id': 'media_id',
    'youtube_title': 'Video Title',
    'caption': 'Caption text',
    'hashtags': ['#tag1', '#tag2'],
    'category': 'Motivational',
})
```

#### `update_post_metrics(video_id: str, metrics: Dict) -> bool`
Update metrics for a post.

```python
analytics.update_post_metrics('video123', {
    'likes': 150,
    'comments': 10,
    'views': 1000
})
```

#### `get_post(video_id: str) -> Optional[Dict]`
Get post by video ID.

```python
post = analytics.get_post('video123')
```

#### `get_all_posts(limit: int = 100) -> List[Dict]`
Get all posts.

```python
posts = analytics.get_all_posts(limit=50)
```

#### `get_best_performing_posts(limit: int = 10) -> List[Dict]`
Get best performing posts.

```python
best = analytics.get_best_performing_posts(5)
```

#### `get_statistics() -> Dict`
Get overall statistics.

```python
stats = analytics.get_statistics()
# Returns: {
#     'total_posts': 50,
#     'total_likes': 5000,
#     'avg_engagement_rate': 5.2,
#     ...
# }
```

#### `get_best_posting_times() -> List[str]`
Analyze best posting times based on engagement.

```python
times = analytics.get_best_posting_times()
# Returns: ['19:00', '09:00', '12:00']
```

#### `get_best_hashtags(limit: int = 10) -> List[str]`
Get best performing hashtags.

```python
tags = analytics.get_best_hashtags(10)
```

#### `export_data(output_file: str = "data/analytics_export.json")`
Export all analytics data.

```python
analytics.export_data('backup.json')
```

---

## Scheduler

### `Scheduler(config: Config)`

Handles scheduling of posts.

**Methods:**

#### `start()`
Start the scheduler.

```python
scheduler = Scheduler(config)
scheduler.start()
```

#### `stop()`
Stop the scheduler.

```python
scheduler.stop()
```

#### `schedule_posts(post_function: Callable)`
Schedule posts based on configuration.

```python
def my_post_function():
    print("Posting...")

scheduler.schedule_posts(my_post_function)
```

#### `schedule_analytics_update(update_function: Callable)`
Schedule periodic analytics updates.

```python
scheduler.schedule_analytics_update(update_analytics)
```

#### `schedule_one_time_post(post_function: Callable, post_time: datetime)`
Schedule a one-time post.

```python
from datetime import datetime, timedelta

post_time = datetime.now() + timedelta(hours=2)
scheduler.schedule_one_time_post(post_function, post_time)
```

#### `get_scheduled_jobs() -> List[dict]`
Get list of scheduled jobs.

```python
jobs = scheduler.get_scheduled_jobs()
for job in jobs:
    print(f"{job['id']}: {job['next_run']}")
```

#### `remove_job(job_id: str)`
Remove a scheduled job.

```python
scheduler.remove_job('daily_post_19_0')
```

#### `is_running() -> bool`
Check if scheduler is running.

```python
if scheduler.is_running():
    print("Scheduler is active")
```

---

## Complete Usage Example

```python
from agent.config import Config
from agent.youtube_scraper import YouTubeScraper
from agent.video_editor import VideoEditor
from agent.caption_generator import CaptionGenerator
from agent.instagram_poster import InstagramPoster
from agent.analytics import Analytics

# Initialize
config = Config()
scraper = YouTubeScraper(config)
editor = VideoEditor(config)
caption_gen = CaptionGenerator(config)
poster = InstagramPoster(config)
analytics = Analytics(config)

# Search and download
videos = scraper.search_videos(['motivation'], max_results=10)
video = videos[0]
video_path = scraper.download_video(video)

# Edit
edited_path = editor.process_video(video_path, video['id'])

# Generate caption
caption_data = caption_gen.generate_caption(video)

# Post
post_info = poster.post_reel(edited_path, caption_data['full_caption'])

# Track
if post_info:
    analytics.track_post({
        'video_id': video['id'],
        'instagram_media_id': post_info['id'],
        'youtube_title': video['title'],
        'caption': caption_data['caption'],
        'hashtags': caption_data['hashtags'],
        'category': config.get('content.category'),
    })

print(f"Posted: {post_info['url']}")
```

---

## Error Handling

All methods return `None` or `False` on error. Check return values:

```python
video_path = scraper.download_video(video)
if video_path is None:
    print("Download failed")
    # Handle error
```

Enable logging to see detailed error messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Thread Safety

The modules are not thread-safe by default. If using multiple threads:

1. Use separate instances per thread
2. Implement proper locking for shared resources
3. Use separate database connections

---

For more information, see the source code in the `agent/` directory.
