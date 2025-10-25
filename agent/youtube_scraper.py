"""YouTube video scraping and downloading"""

import os
import re
import yt_dlp
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """Handles YouTube video discovery and downloading"""
    
    def __init__(self, config):
        self.config = config
        self.download_path = Path("data/videos")
        self.download_path.mkdir(parents=True, exist_ok=True)
        
    def search_videos(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """
        Search for videos on YouTube based on keywords
        Returns list of video metadata
        """
        logger.info(f"Searching YouTube for keywords: {keywords}")
        
        videos = []
        timeframe = self.config.get('youtube.search_timeframe', 'this_week')
        min_views = self.config.get('youtube.min_views', 10000)
        
        for keyword in keywords:
            try:
                search_results = self._search_youtube(keyword, max_results, timeframe)
                filtered_videos = self._filter_videos(search_results, min_views)
                videos.extend(filtered_videos)
            except Exception as e:
                logger.error(f"Error searching for keyword '{keyword}': {e}")
        
        # Sort by engagement score
        videos.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
        
        logger.info(f"Found {len(videos)} suitable videos")
        return videos[:max_results]
    
    def _search_youtube(self, keyword: str, max_results: int, timeframe: str) -> List[Dict]:
        """Perform YouTube search using yt-dlp"""
        
        # Map timeframe to yt-dlp filters
        timeframe_map = {
            'today': 'today',
            'this_week': 'week',
            'this_month': 'month',
            '7 days': 'week',
        }
        
        search_query = f"ytsearch{max_results}:{keyword}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                result = ydl.extract_info(search_query, download=False)
                if 'entries' in result:
                    return [self._extract_video_info(entry) for entry in result['entries'] if entry]
            except Exception as e:
                logger.error(f"Error extracting info: {e}")
                return []
        
        return []
    
    def _extract_video_info(self, entry: Dict) -> Dict:
        """Extract relevant video information"""
        return {
            'id': entry.get('id'),
            'title': entry.get('title'),
            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
            'duration': entry.get('duration', 0),
            'view_count': entry.get('view_count', 0),
            'like_count': entry.get('like_count', 0),
            'channel': entry.get('channel') or entry.get('uploader'),
            'upload_date': entry.get('upload_date'),
            'thumbnail': entry.get('thumbnail'),
            'description': entry.get('description', ''),
        }
    
    def _filter_videos(self, videos: List[Dict], min_views: int) -> List[Dict]:
        """Filter videos based on criteria"""
        filtered = []
        max_length = self.config.get('content.video_length_limit', 60)
        min_length = self.config.get('content.min_video_length', 10)
        min_likes_ratio = self.config.get('youtube.min_likes_ratio', 0.9)
        
        for video in videos:
            duration = video.get('duration', 0)
            views = video.get('view_count', 0)
            likes = video.get('like_count', 0)
            
            # Filter by duration
            if duration < min_length or duration > max_length:
                continue
            
            # Filter by views
            if views < min_views:
                continue
            
            # Calculate engagement score
            engagement_score = likes / max(views, 1)
            video['engagement_score'] = engagement_score
            
            # Filter by engagement
            if engagement_score < (min_likes_ratio / 100):
                continue
            
            # Check for potential copyright issues
            if self._check_copyright_indicators(video):
                logger.warning(f"Skipping video due to copyright indicators: {video['title']}")
                continue
            
            filtered.append(video)
        
        return filtered
    
    def _check_copyright_indicators(self, video: Dict) -> bool:
        """Check for common copyright indicators in video metadata"""
        if not self.config.get_env('enable_copyright_check', True):
            return False
        
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        
        copyright_keywords = [
            'official music video',
            'official video',
            'vevo',
            'full movie',
            'full episode',
            'hd movie',
            'soundtrack',
        ]
        
        for keyword in copyright_keywords:
            if keyword in title or keyword in description:
                return True
        
        return False
    
    def download_video(self, video: Dict) -> Optional[str]:
        """
        Download a video from YouTube
        Returns path to downloaded file or None if failed
        """
        video_id = video['id']
        logger.info(f"Downloading video: {video['title']} ({video_id})")
        
        output_path = self.download_path / f"{video_id}.mp4"
        
        if output_path.exists():
            logger.info(f"Video already downloaded: {output_path}")
            return str(output_path)
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(self.download_path / f'{video_id}.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video['url']])
            
            # Find the downloaded file
            downloaded_files = list(self.download_path.glob(f"{video_id}.*"))
            if downloaded_files:
                return str(downloaded_files[0])
            else:
                logger.error(f"Downloaded file not found for video {video_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video {video_id}: {e}")
            return None
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """Get detailed information about a specific video"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return self._extract_video_info(info)
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
