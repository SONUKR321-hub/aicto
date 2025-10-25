# Quick Reference Card

## 🚀 Common Commands

```bash
# Setup
./quick_start.sh

# Run Modes
python main.py --test      # Test without posting
python main.py             # Single post
python main.py --daemon    # Continuous operation

# Analytics
python main.py --stats     # View statistics

# Logs
tail -f logs/agent.log     # View live logs

# Docker
docker-compose up -d       # Start in background
docker-compose logs -f     # View logs
docker-compose down        # Stop
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Credentials (Instagram, API keys) |
| `config.yaml` | Main configuration |
| `main.py` | Entry point |
| `agent/*` | Core modules |
| `data/database.db` | Analytics database |
| `logs/agent.log` | Application logs |

---

## ⚙️ Quick Config

### Change Category
```yaml
# config.yaml
content:
  category: "Motivational"  # or "Tech", "Comedy", etc.
```

### Change Schedule
```yaml
# config.yaml
schedule:
  post_times:
    - "07:00"  # 7 AM
    - "19:00"  # 7 PM
```

### Change Caption Style
```yaml
# config.yaml
caption:
  style: "inspiring"  # or "casual", "informative"
```

---

## 🔑 Environment Variables

```bash
# .env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
OPENAI_API_KEY=sk-your-key
# or
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## 📊 Module Overview

| Module | Function |
|--------|----------|
| `youtube_scraper.py` | Find & download videos |
| `video_editor.py` | Edit for Instagram |
| `caption_generator.py` | Create captions |
| `instagram_poster.py` | Post to Instagram |
| `analytics.py` | Track performance |
| `scheduler.py` | Schedule posts |

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| FFmpeg not found | `sudo apt install ffmpeg` |
| Login failed | Check credentials in `.env` |
| No videos found | Adjust keywords or thresholds |
| Import errors | `pip install -r requirements.txt` |

---

## 📈 Quick Analytics

```python
from agent.analytics import Analytics
from agent.config import Config

config = Config()
analytics = Analytics(config)

# Get stats
stats = analytics.get_statistics()
print(f"Total Posts: {stats['total_posts']}")
print(f"Avg Engagement: {stats['avg_engagement_rate']:.2f}%")

# Best posts
best = analytics.get_best_performing_posts(5)
for post in best:
    print(post['youtube_title'])
```

---

## 🔄 Quick Update

```bash
git pull
pip install -r requirements.txt --upgrade
```

---

## 📦 Directory Structure

```
/
├── agent/              # Core modules
├── data/              # Videos & database
├── logs/              # Log files
├── config.yaml        # Configuration
├── .env              # Credentials
├── main.py           # Entry point
└── [docs]            # Documentation
```

---

## 🎯 Workflow

```
Search YouTube → Download → Edit → Generate Caption → Post → Track
```

---

## 💡 Tips

1. **Start with test mode**: `python main.py --test`
2. **Check logs often**: `tail -f logs/agent.log`
3. **Monitor analytics**: `python main.py --stats`
4. **Adjust based on data**: Use best times/hashtags
5. **Clean storage**: Set `cleanup_downloads: true`

---

## 🔗 Quick Links

- **Full Setup**: [SETUP.md](SETUP.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **API Docs**: [API.md](API.md)

---

## 🆘 Getting Help

1. Check documentation
2. Review logs
3. Search existing issues
4. Open new issue with logs

---

## ⚡ Performance Tips

- Use `cleanup_downloads: true` to save space
- Set `max_storage_gb` to limit disk usage
- Adjust `video_length_limit` for faster processing
- Use lower resolution if upload speed is slow

---

## 🎨 Customization

### Add Custom Hashtags
```yaml
caption:
  custom_hashtags:
    - "#yourbrand"
    - "#yourchannel"
```

### Add Watermark
```yaml
editing:
  watermark:
    enabled: true
    text: "@youraccount"
    position: "bottom-right"
```

### Add Intro/Outro
```yaml
editing:
  intro_outro:
    enabled: true
    intro_path: "assets/intro.mp4"
    outro_path: "assets/outro.mp4"
```

---

**For complete documentation, see README.md**
