# 🤖 YouTube-to-Instagram Auto Poster Agent

A fully autonomous AI agent that automatically finds, downloads, edits, and posts trending YouTube videos to your Instagram channel with optimized captions, hashtags, and formatting.

## 🌟 Features

- **Intelligent YouTube Scraping**: Automatically finds trending videos in your chosen category
- **Smart Video Editing**: Converts videos to Instagram Reels format (9:16), adds subtitles, watermarks
- **AI-Powered Captions**: Generates engaging captions with relevant hashtags using AI
- **Automated Scheduling**: Posts content at optimal times for maximum engagement
- **Analytics Tracking**: Monitors performance and optimizes future content selection
- **Safety Compliance**: Filters out copyrighted and inappropriate content

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- Instagram account credentials
- OpenAI or Anthropic API key (for caption generation)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-name>

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

1. Edit `config.yaml` to set your preferences:
   - Video category/keywords
   - Posting schedule
   - Instagram account details
   - Video editing preferences

2. Set up your `.env` file with:
   - Instagram credentials
   - API keys
   - Optional: Proxy settings

### Usage

```bash
# Run the agent
python main.py

# Run in daemon mode (continuous operation)
python main.py --daemon

# Test mode (download and process without posting)
python main.py --test
```

## 📁 Project Structure

```
.
├── agent/                  # Core agent modules
│   ├── youtube_scraper.py  # YouTube video discovery and download
│   ├── video_editor.py     # Video processing and optimization
│   ├── caption_generator.py # AI caption and hashtag generation
│   ├── instagram_poster.py # Instagram API integration
│   ├── scheduler.py        # Post scheduling logic
│   ├── analytics.py        # Performance tracking
│   └── config.py           # Configuration management
├── data/                   # Data storage
│   ├── videos/            # Downloaded videos
│   ├── edited/            # Processed videos
│   └── database.db        # SQLite database
├── logs/                  # Application logs
├── config.yaml            # Main configuration file
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment template
├── requirements.txt       # Python dependencies
└── main.py               # Entry point
```

## ⚙️ Configuration Options

### config.yaml

```yaml
category: "Motivational"  # Video niche
post_frequency: "1 post daily at 7 PM"
youtube_source_keywords:
  - "motivation shorts"
  - "motivational speeches"
instagram_account: "@lostmoment8"
video_length_limit: 60  # seconds
language: "English"
caption_style: "inspiring"  # casual/informative/inspiring
```

## 🔐 Safety & Compliance

- Automatically skips copyrighted content
- Filters NSFW and inappropriate material
- Credits original creators when applicable
- Complies with Instagram community guidelines
- Respects rate limits and API quotas

## 📊 Analytics

The agent tracks:
- Post performance (likes, comments, reach)
- Best performing content types
- Optimal posting times
- Engagement trends

## 🛠️ Advanced Features

- **Custom Intro/Outro**: Add your branding to videos
- **Multiple Accounts**: Manage multiple Instagram profiles
- **Content Queue**: Manual approval before posting
- **Backup & Recovery**: Automatic data backup
- **Webhook Notifications**: Get alerts on Discord/Slack

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for educational and automation purposes. Ensure you have the right to repost content and comply with YouTube's Terms of Service and Instagram's API policies. Always respect copyright and give credit to original creators.

## 🆘 Support

For issues or questions, please open a GitHub issue or contact the maintainer.
