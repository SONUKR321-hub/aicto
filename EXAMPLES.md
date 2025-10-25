# Usage Examples

This document provides practical examples of how to use the YouTube-to-Instagram agent.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Configuration Examples](#configuration-examples)
- [Automation Scenarios](#automation-scenarios)
- [Custom Workflows](#custom-workflows)

---

## Basic Usage

### Example 1: Motivational Content

**Goal**: Post daily motivational shorts to Instagram

**config.yaml**:
```yaml
content:
  category: "Motivational"
  youtube_source_keywords:
    - "motivational shorts"
    - "daily motivation"
    - "motivation 2024"
  language: "English"
  video_length_limit: 60

schedule:
  frequency: "daily"
  post_times:
    - "07:00"  # Morning motivation
  timezone: "America/New_York"

caption:
  style: "inspiring"
  custom_hashtags:
    - "#motivation"
    - "#dailymotivation"
    - "#inspire"
```

**Run**:
```bash
python main.py --daemon
```

---

### Example 2: Tech News Channel

**Goal**: Share latest AI/tech news twice daily

**config.yaml**:
```yaml
content:
  category: "Tech"
  youtube_source_keywords:
    - "AI news"
    - "tech updates 2024"
    - "artificial intelligence"
  language: "English"
  video_length_limit: 90

schedule:
  frequency: "twice_daily"
  post_times:
    - "09:00"  # Morning
    - "18:00"  # Evening
  timezone: "UTC"

caption:
  style: "informative"
  include_emojis: true
  custom_hashtags:
    - "#tech"
    - "#ai"
    - "#technology"
    - "#innovation"
```

---

### Example 3: Movie Scenes/Comedy

**Goal**: Post funny movie scenes and comedy clips

**config.yaml**:
```yaml
content:
  category: "Comedy"
  youtube_source_keywords:
    - "funny movie scenes"
    - "comedy shorts"
    - "hilarious moments"
  language: "English"
  video_length_limit: 45

youtube:
  min_views: 50000  # Higher threshold for comedy
  min_likes_ratio: 0.95

schedule:
  frequency: "daily"
  post_times:
    - "20:00"  # Evening entertainment
  timezone: "America/Los_Angeles"

caption:
  style: "casual"
  include_emojis: true
  call_to_action: true

editing:
  watermark:
    enabled: true
    text: "@yourcomedypage"
    position: "bottom-right"
```

---

## Configuration Examples

### High-Quality Content Filter

For selective, high-quality content:

```yaml
youtube:
  search_timeframe: "this_week"
  min_views: 100000
  min_likes_ratio: 0.95
  max_videos_to_check: 100

content:
  video_length_limit: 60
  min_video_length: 20

safety:
  skip_copyrighted: true
  content_filter: true
  nsfw_filter: true
  manual_approval: true  # Review before posting
```

### Fast-Paced Posting

For frequent content updates:

```yaml
schedule:
  frequency: "daily"
  post_times:
    - "08:00"
    - "12:00"
    - "17:00"
    - "21:00"
  timezone: "UTC"

youtube:
  min_views: 5000  # Lower threshold
  max_videos_to_check: 200

advanced:
  cleanup_downloads: true
  max_storage_gb: 5
```

### Custom Branding

Add your own intro and watermark:

```yaml
editing:
  watermark:
    enabled: true
    text: "@YourBrand"
    position: "bottom-right"
    opacity: 0.8
  
  intro_outro:
    enabled: true
    intro_path: "assets/intro.mp4"
    outro_path: "assets/outro.mp4"
  
  subtitle_style:
    font_size: 45
    font_color: "yellow"
    stroke_color: "black"
    stroke_width: 3
```

---

## Automation Scenarios

### Scenario 1: Test New Keywords

**Goal**: Test different keywords without posting

```bash
# Run in test mode
python main.py --test

# Check what content would be selected
# Review logs/agent.log to see what videos were found

# Adjust config.yaml based on results
# Run test again until satisfied
```

### Scenario 2: Backup Strategy

**Goal**: Backup posts before cleanup

```python
# Create backup script: backup.py
from agent.config import Config
from agent.analytics import Analytics

config = Config()
analytics = Analytics(config)

# Export analytics
analytics.export_data("backups/analytics_backup.json")
print("Backup complete!")
```

Run daily:
```bash
python backup.py
```

### Scenario 3: Multi-Account Management

**Goal**: Manage multiple Instagram accounts

Create separate configs:

**config_motivational.yaml**:
```yaml
content:
  category: "Motivational"
instagram:
  account: "@motivational_account"
```

**config_tech.yaml**:
```yaml
content:
  category: "Tech"
instagram:
  account: "@tech_account"
```

Create separate .env files or use different environment variables.

Run separate instances:
```bash
# Terminal 1
python main.py --config config_motivational.yaml --daemon

# Terminal 2
python main.py --config config_tech.yaml --daemon
```

### Scenario 4: Analytics-Driven Optimization

**Goal**: Use analytics to improve performance

```bash
# Check current stats
python main.py --stats

# Example output analysis:
# - Best posting time: 7 PM
# - Best hashtags: #motivation, #success
# - Avg engagement: 5.2%

# Update config.yaml based on insights
schedule:
  post_times:
    - "19:00"  # Use best time

caption:
  custom_hashtags:
    - "#motivation"
    - "#success"
    # ... use best performing hashtags
```

---

## Custom Workflows

### Workflow 1: Manual Approval Queue

Enable manual review before posting:

1. Set in config.yaml:
```yaml
safety:
  manual_approval: true
```

2. Create approval script `approve.py`:
```python
import os
from pathlib import Path

def review_pending():
    pending_dir = Path("data/edited")
    videos = list(pending_dir.glob("*_edited.mp4"))
    
    for video in videos:
        print(f"\n=== Review: {video.name} ===")
        # Open video for review
        os.system(f"xdg-open {video}")  # Linux
        # os.system(f"open {video}")    # macOS
        
        choice = input("Approve? (y/n): ")
        if choice.lower() == 'y':
            # Mark for posting
            video.rename(video.with_suffix('.approved.mp4'))
        else:
            # Skip
            video.rename(video.with_suffix('.rejected.mp4'))

if __name__ == "__main__":
    review_pending()
```

### Workflow 2: Scheduled Analytics Reports

Create weekly report script `weekly_report.py`:

```python
from agent.config import Config
from agent.analytics import Analytics
from datetime import datetime

config = Config()
analytics = Analytics(config)

print(f"\n=== Weekly Report - {datetime.now().strftime('%Y-%m-%d')} ===\n")

stats = analytics.get_statistics()
print("Overall Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")

print("\nTop 5 Posts:")
top_posts = analytics.get_best_performing_posts(5)
for i, post in enumerate(top_posts, 1):
    print(f"{i}. {post['youtube_title']}")
    print(f"   Engagement: {post['engagement_rate']:.2f}%")
    print(f"   {post['instagram_url']}\n")

print("\nBest Posting Times:")
best_times = analytics.get_best_posting_times()
print(f"  {', '.join(best_times)}")

print("\nBest Hashtags:")
best_tags = analytics.get_best_hashtags(10)
print(f"  {' '.join(best_tags)}")
```

Schedule with cron:
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/agent && /path/to/venv/bin/python weekly_report.py > reports/weekly_$(date +\%Y\%m\%d).txt
```

### Workflow 3: Content Calendar

Plan posts in advance:

```python
# content_calendar.py
from datetime import datetime, timedelta
from agent.scheduler import Scheduler
from agent.config import Config

config = Config()
scheduler = Scheduler(config)

# Schedule specific posts
posts = [
    {"time": "2024-03-01 09:00", "keywords": ["morning motivation"]},
    {"time": "2024-03-01 19:00", "keywords": ["evening inspiration"]},
    {"time": "2024-03-02 09:00", "keywords": ["success stories"]},
]

for post in posts:
    post_time = datetime.strptime(post['time'], '%Y-%m-%d %H:%M')
    # Create custom post function with keywords
    scheduler.schedule_one_time_post(lambda: run_with_keywords(post['keywords']), post_time)

scheduler.start()
```

### Workflow 4: A/B Testing Captions

Test different caption styles:

```python
# ab_test.py
import random
from agent.caption_generator import CaptionGenerator

config = Config()
caption_gen = CaptionGenerator(config)

styles = ['inspiring', 'casual', 'informative']

def generate_test_caption(video_info):
    style = random.choice(styles)
    config.config_data['caption']['style'] = style
    
    caption = caption_gen.generate_caption(video_info)
    caption['caption'] += f"\n\n[Test: {style}]"
    
    return caption
```

Track which style performs best in analytics.

---

## Advanced Tips

### Tip 1: Category-Specific Keywords

Create comprehensive keyword lists:

```yaml
content:
  youtube_source_keywords:
    # General
    - "motivation shorts 2024"
    # Specific niches
    - "entrepreneur motivation"
    - "fitness motivation"
    - "study motivation"
    # Trending
    - "viral motivation"
    # Creators
    - "motivation compilation"
```

### Tip 2: Time-Based Posting

Match content to time of day:

```python
# smart_scheduler.py
from datetime import datetime

def get_appropriate_keywords():
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        return ["morning motivation", "start your day"]
    elif 12 <= hour < 17:
        return ["midday inspiration", "keep going"]
    elif 17 <= hour < 22:
        return ["evening motivation", "end your day strong"]
    else:
        return ["night motivation", "tomorrow planning"]
```

### Tip 3: Engagement Boosting

Optimize for maximum engagement:

```yaml
caption:
  call_to_action: true
  include_emojis: true
  hashtag_count: 30  # Use maximum
  
# Use questions in captions to encourage comments
# Example: "What motivates you? 💪"
```

### Tip 4: Content Refresh

Avoid posting same content:

```python
# Track posted video IDs
posted_ids = set()

def is_posted(video_id):
    return video_id in posted_ids

# Before posting, check if already posted
# Skip if duplicate
```

---

## Common Patterns

### Pattern: Quality Over Quantity
- Higher view thresholds
- Manual approval
- Longer videos (30-60s)
- Custom editing

### Pattern: Viral Content Hunter
- Recent uploads only
- High engagement threshold
- Trending keywords
- Fast posting

### Pattern: Niche Authority
- Specific keywords
- Consistent schedule
- Custom branding
- Educational content

---

For more examples and support, visit the GitHub repository or check the documentation.
