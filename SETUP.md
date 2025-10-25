# Setup Guide

## Prerequisites

### 1. System Requirements

- Python 3.8 or higher
- FFmpeg (for video processing)
- At least 2GB of free disk space

### 2. Install FFmpeg

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

#### Windows:
Download from https://ffmpeg.org/download.html and add to PATH

### 3. Verify FFmpeg Installation
```bash
ffmpeg -version
```

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
OPENAI_API_KEY=sk-your-openai-key
```

### 5. Configure Agent Settings

Edit `config.yaml` to customize:
- Content category and keywords
- Posting schedule
- Video editing preferences
- Caption style
- Hashtags

## Configuration Details

### Content Settings

```yaml
content:
  category: "Motivational"  # Your content niche
  youtube_source_keywords:
    - "motivation shorts"
    - "motivational speeches"
  language: "English"
  video_length_limit: 60  # Max video duration in seconds
```

### Schedule Settings

```yaml
schedule:
  frequency: "daily"
  post_times:
    - "19:00"  # 7 PM
  timezone: "UTC"
```

### Instagram Settings

Make sure to use your actual Instagram account credentials in the `.env` file.

**Important Security Notes:**
- Never commit your `.env` file to version control
- Use a strong, unique password
- Consider using Instagram's API if available for your use case
- Be aware of Instagram's automation policies and rate limits

## First Run

### Test Mode (Recommended First)

Run in test mode to verify everything works without posting:
```bash
python main.py --test
```

This will:
- Search for videos
- Download and process a video
- Generate captions
- **NOT** post to Instagram

### Single Post

Make a single post:
```bash
python main.py
```

### Daemon Mode

Run continuously with scheduled posting:
```bash
python main.py --daemon
```

Press Ctrl+C to stop.

## Troubleshooting

### FFmpeg Not Found
```
Error: FFmpeg not found
Solution: Install FFmpeg and ensure it's in your PATH
```

### Instagram Login Failed
```
Error: Instagram login failed
Solution: 
1. Check your credentials in .env
2. Try logging in manually to verify account isn't locked
3. Check for 2FA (may need to disable or use app-specific password)
4. Wait a few hours if rate limited
```

### No Videos Found
```
Warning: No suitable videos found
Solution:
1. Check your search keywords in config.yaml
2. Adjust video_length_limit and min_views settings
3. Try broader search terms
```

### Video Processing Failed
```
Error: Failed to process video
Solution:
1. Ensure FFmpeg is installed correctly
2. Check video file isn't corrupted
3. Try with a different video
4. Check available disk space
```

### API Key Errors
```
Error: Missing AI API key
Solution:
1. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env
2. Verify the key is valid
3. Check you have API credits
```

## Monitoring

### View Statistics
```bash
python main.py --stats
```

This shows:
- Total posts
- Engagement metrics
- Best performing content
- Optimal posting times
- Best hashtags

### Check Logs
```bash
tail -f logs/agent.log
```

## Best Practices

1. **Start Small**: Begin with test mode and single posts
2. **Monitor Performance**: Check analytics regularly
3. **Adjust Keywords**: Refine based on what content performs well
4. **Respect Rate Limits**: Don't post too frequently
5. **Quality Over Quantity**: Better to post less often with better content
6. **Stay Compliant**: Follow Instagram's Terms of Service
7. **Credit Creators**: Give credit to original content creators when appropriate

## Advanced Usage

### Custom Intro/Outro

1. Create intro/outro videos in 9:16 format
2. Save them in the project directory
3. Update config.yaml:
```yaml
editing:
  intro_outro:
    enabled: true
    intro_path: "path/to/intro.mp4"
    outro_path: "path/to/outro.mp4"
```

### Custom Hashtags

Add your own hashtags that always get included:
```yaml
caption:
  custom_hashtags:
    - "#yourbrand"
    - "#yourchannel"
```

### Manual Approval

Enable manual approval before posting:
```yaml
safety:
  manual_approval: true
```

## Updating

To update the agent:
```bash
git pull
pip install -r requirements.txt --upgrade
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/agent.log`
3. Open a GitHub issue with details and logs
