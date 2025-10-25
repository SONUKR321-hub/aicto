# Deployment Guide

This guide covers deploying the YouTube-to-Instagram agent to various platforms for continuous operation.

## Table of Contents
- [VPS Deployment (Ubuntu/Debian)](#vps-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Process Management](#process-management)

---

## VPS Deployment (Ubuntu/Debian)

### 1. Initial Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Clone repository
git clone <your-repo-url>
cd <repo-name>

# Run quick start
chmod +x quick_start.sh
./quick_start.sh
```

### 2. Configure Environment

```bash
# Edit .env
nano .env

# Edit config.yaml
nano config.yaml
```

### 3. Test the Agent

```bash
# Activate virtual environment
source venv/bin/activate

# Test run
python main.py --test

# Single post
python main.py
```

### 4. Run as Background Service

Create a systemd service for automatic startup and management.

Create `/etc/systemd/system/youtube-instagram-agent.service`:

```ini
[Unit]
Description=YouTube to Instagram Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/agent
Environment="PATH=/path/to/your/agent/venv/bin"
ExecStart=/path/to/your/agent/venv/bin/python main.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable youtube-instagram-agent
sudo systemctl start youtube-instagram-agent

# Check status
sudo systemctl status youtube-instagram-agent

# View logs
sudo journalctl -u youtube-instagram-agent -f
```

---

## Docker Deployment

### 1. Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/videos data/edited logs

# Run agent
CMD ["python", "main.py", "--daemon"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  agent:
    build: .
    container_name: youtube-instagram-agent
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config.yaml:/app/config.yaml
    environment:
      - TZ=UTC
```

### 3. Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Cloud Platforms

### AWS EC2

1. **Launch Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.small or larger
   - Storage: 20GB+

2. **Connect and Setup**:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Follow VPS deployment steps above**

4. **Setup CloudWatch** (optional):
   - Configure CloudWatch logs for monitoring
   - Set up alarms for failures

### Google Cloud Platform (GCP)

1. **Create Compute Engine Instance**:
   - Machine type: e2-small or larger
   - Boot disk: Ubuntu 22.04 LTS, 20GB
   - Allow HTTP/HTTPS traffic

2. **Connect via SSH** and follow VPS setup

3. **Setup Cloud Logging** (optional)

### DigitalOcean

1. **Create Droplet**:
   - Image: Ubuntu 22.04 LTS
   - Plan: Basic, $6/month or higher
   - Add SSH key

2. **Connect and setup** as per VPS guide

3. **Setup monitoring** in DigitalOcean dashboard

### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "worker: python main.py --daemon" > Procfile

# Create heroku app
heroku create your-app-name

# Add buildpacks
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add --index 2 heroku/python

# Set environment variables
heroku config:set INSTAGRAM_USERNAME=your_username
heroku config:set INSTAGRAM_PASSWORD=your_password
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

---

## Process Management

### Using Screen (Simple)

```bash
# Start screen session
screen -S instagram-agent

# Activate venv and run
source venv/bin/activate
python main.py --daemon

# Detach: Press Ctrl+A then D

# Reattach
screen -r instagram-agent

# List sessions
screen -ls
```

### Using tmux

```bash
# Start tmux session
tmux new -s agent

# Run agent
source venv/bin/activate
python main.py --daemon

# Detach: Press Ctrl+B then D

# Reattach
tmux attach -t agent
```

### Using Supervisor

Install supervisor:
```bash
sudo apt install supervisor
```

Create `/etc/supervisor/conf.d/youtube-instagram-agent.conf`:

```ini
[program:youtube-instagram-agent]
command=/path/to/venv/bin/python /path/to/main.py --daemon
directory=/path/to/agent
user=your-username
autostart=true
autorestart=true
stderr_logfile=/var/log/youtube-instagram-agent.err.log
stdout_logfile=/var/log/youtube-instagram-agent.out.log
```

Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start youtube-instagram-agent
```

---

## Monitoring & Maintenance

### Log Rotation

Create `/etc/logrotate.d/youtube-instagram-agent`:

```
/path/to/agent/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
```

### Disk Space Management

Add to crontab:
```bash
# Clean old videos daily at 3 AM
0 3 * * * find /path/to/agent/data/videos -type f -mtime +7 -delete
0 3 * * * find /path/to/agent/data/edited -type f -mtime +7 -delete
```

### Health Checks

Create a simple health check script `health_check.sh`:

```bash
#!/bin/bash
if ! pgrep -f "main.py --daemon" > /dev/null; then
    echo "Agent not running! Restarting..."
    cd /path/to/agent
    source venv/bin/activate
    python main.py --daemon &
fi
```

Add to crontab:
```bash
*/5 * * * * /path/to/health_check.sh
```

### Backup

Backup important data:
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup-$DATE.tar.gz data/database.db config.yaml .env
```

---

## Security Best Practices

1. **Use Environment Variables**: Never commit credentials
2. **Firewall**: Configure UFW or cloud firewall
3. **SSH Keys**: Disable password authentication
4. **Updates**: Keep system and dependencies updated
5. **Monitoring**: Set up alerts for failures
6. **Backups**: Regular database backups
7. **Rate Limits**: Respect Instagram API limits
8. **2FA**: Use strong authentication

---

## Troubleshooting Deployment

### Service Won't Start
```bash
# Check service status
sudo systemctl status youtube-instagram-agent

# Check logs
sudo journalctl -u youtube-instagram-agent -n 50

# Check file permissions
ls -la /path/to/agent
```

### Out of Memory
- Increase swap space
- Upgrade to larger instance
- Reduce concurrent operations

### FFmpeg Errors
```bash
# Reinstall FFmpeg
sudo apt remove ffmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

### Instagram Login Issues
- Check credentials
- Try different IP (Instagram may block VPS IPs)
- Use residential proxy
- Implement delay between requests

---

## Scaling

For multiple Instagram accounts:

1. Create separate config files: `config_account1.yaml`, `config_account2.yaml`
2. Run multiple instances with different configs
3. Use separate virtual environments or Docker containers
4. Implement queuing system for high volume

---

## Cost Estimates

**VPS (DigitalOcean/AWS/GCP)**:
- Basic: $5-10/month
- Recommended: $12-20/month

**Cloud Functions**:
- Very low usage: Free tier
- Regular use: $5-15/month

**Additional Costs**:
- OpenAI API: $5-20/month (depending on usage)
- Storage: Usually included
- Bandwidth: Usually sufficient in basic plans

---

For more help, consult the main README.md and SETUP.md files.
