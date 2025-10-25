# Contributing Guide

Thank you for your interest in contributing to the YouTube-to-Instagram Agent! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best outcome for the community
- Show empathy towards other contributors

---

## Getting Started

### Prerequisites

- Python 3.8+
- FFmpeg
- Git
- Basic understanding of Python and video processing

### Find an Issue

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to let others know you're working on it

### Or Suggest a Feature

1. Open a new issue
2. Describe the feature and its use case
3. Wait for feedback before starting development

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/repo-name.git
cd repo-name
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

### 4. Configure for Development

```bash
cp .env.example .env
# Edit .env with your test credentials
```

### 5. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

---

## Making Changes

### Project Structure

```
agent/
├── __init__.py           # Module initialization
├── config.py            # Configuration management
├── youtube_scraper.py   # YouTube functionality
├── video_editor.py      # Video processing
├── caption_generator.py # AI caption generation
├── instagram_poster.py  # Instagram posting
├── analytics.py         # Analytics tracking
└── scheduler.py         # Post scheduling
```

### Adding a New Feature

1. **Identify the appropriate module**
   - YouTube-related: `youtube_scraper.py`
   - Editing: `video_editor.py`
   - Captions: `caption_generator.py`
   - Instagram: `instagram_poster.py`
   - Analytics: `analytics.py`
   - Scheduling: `scheduler.py`

2. **Implement the feature**
   - Follow existing patterns
   - Add proper error handling
   - Include logging statements
   - Update docstrings

3. **Update configuration if needed**
   - Add new config options to `config.yaml`
   - Document in README.md

4. **Update documentation**
   - Update relevant .md files
   - Add examples if applicable

### Example: Adding a New Video Effect

```python
# In agent/video_editor.py

def add_blur_effect(self, clip: VideoFileClip, blur_amount: float = 2.0) -> VideoFileClip:
    """
    Add blur effect to video
    
    Args:
        clip: Input video clip
        blur_amount: Blur intensity (default: 2.0)
    
    Returns:
        Video clip with blur effect
    """
    try:
        from moviepy.video.fx import all as vfx
        return clip.fx(vfx.blur, blur_amount)
    except Exception as e:
        self.logger.error(f"Error adding blur effect: {e}")
        return clip
```

---

## Testing

### Manual Testing

Before submitting:

1. **Test in test mode**:
```bash
python main.py --test
```

2. **Test single run**:
```bash
python main.py
```

3. **Check logs**:
```bash
tail -f logs/agent.log
```

### Test Different Scenarios

- [ ] Different video categories
- [ ] Various video lengths
- [ ] Different posting times
- [ ] Error handling (invalid credentials, network issues)
- [ ] Edge cases (very short/long videos, special characters)

### Automated Tests (Future)

We plan to add unit tests. When available:

```bash
pytest tests/
```

---

## Submitting Changes

### 1. Commit Your Changes

Follow conventional commit format:

```bash
git add .
git commit -m "feat: add blur effect to video editor"

# Commit types:
# feat: New feature
# fix: Bug fix
# docs: Documentation changes
# style: Code style changes (formatting)
# refactor: Code refactoring
# test: Adding tests
# chore: Maintenance tasks
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:
   - Description of changes
   - Related issue number
   - Testing performed
   - Screenshots if applicable

### 4. PR Review Process

- Maintainers will review your code
- Address any feedback
- Once approved, your PR will be merged

---

## Style Guide

### Python Code Style

Follow PEP 8 with these specifics:

#### Imports

```python
# Standard library
import os
import logging
from pathlib import Path

# Third-party
import requests
from moviepy.editor import VideoFileClip

# Local
from agent.config import Config
```

#### Naming

```python
# Classes: PascalCase
class VideoEditor:
    pass

# Functions/methods: snake_case
def process_video(video_path: str) -> str:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_VIDEO_LENGTH = 60

# Private methods: _leading_underscore
def _internal_helper(self):
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def search_videos(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
    """
    Search for videos on YouTube based on keywords
    
    Args:
        keywords: List of search keywords
        max_results: Maximum number of results to return
    
    Returns:
        List of video metadata dictionaries
    
    Raises:
        ValueError: If keywords list is empty
    """
    pass
```

#### Error Handling

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return None
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Configuration Style

YAML formatting:

```yaml
# Use 2 spaces for indentation
content:
  category: "Motivational"
  youtube_source_keywords:
    - "keyword one"
    - "keyword two"
  
# Comments above the setting
video_length_limit: 60  # Inline comments if needed
```

### Documentation Style

- Use clear, concise language
- Include code examples
- Use proper Markdown formatting
- Add table of contents for long documents

---

## Areas for Contribution

### High Priority

- [ ] Subtitle generation from audio
- [ ] Better copyright detection
- [ ] Multiple AI provider support
- [ ] Video quality improvement
- [ ] Better error recovery

### Feature Ideas

- [ ] Support for other social platforms (TikTok, Facebook)
- [ ] Web dashboard for monitoring
- [ ] Mobile app integration
- [ ] Advanced video effects
- [ ] Content recommendation engine
- [ ] Multi-language support
- [ ] Voice-over generation
- [ ] Automatic thumbnail generation

### Documentation

- [ ] Video tutorials
- [ ] More usage examples
- [ ] Troubleshooting guide expansion
- [ ] Best practices guide
- [ ] API reference improvements

### Infrastructure

- [ ] Unit tests
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] Performance optimization
- [ ] Docker improvements
- [ ] Kubernetes deployment

---

## Getting Help

### Questions

- Open a [Discussion](https://github.com/your-repo/discussions)
- Join our community chat (if available)
- Check existing issues and documentation

### Bugs

1. Check if already reported
2. Provide detailed information:
   - Python version
   - OS and version
   - Steps to reproduce
   - Error messages and logs
   - Expected vs actual behavior

### Feature Requests

1. Search existing issues
2. Describe the use case
3. Provide examples
4. Be open to feedback

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing! 🎉
