"""Instagram posting functionality"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger(__name__)

class InstagramPoster:
    """Handles posting to Instagram"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.session_file = Path("data/instagram_session.json")
        
    def login(self) -> bool:
        """Login to Instagram"""
        username = self.config.instagram_username
        password = self.config.instagram_password
        
        if not username or not password:
            logger.error("Instagram credentials not provided")
            return False
        
        try:
            self.client = Client()
            
            # Try to load session
            if self.session_file.exists():
                logger.info("Loading Instagram session from file")
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(username, password)
                    logger.info("Successfully logged in using saved session")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load session: {e}")
            
            # Fresh login
            logger.info(f"Logging in to Instagram as {username}")
            self.client.login(username, password)
            
            # Save session
            self.client.dump_settings(self.session_file)
            logger.info("Instagram login successful and session saved")
            return True
            
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False
    
    def post_reel(self, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Optional[Dict]:
        """
        Post a video as a Reel
        Returns post information or None if failed
        """
        if not self.client:
            if not self.login():
                return None
        
        try:
            logger.info(f"Posting reel to Instagram: {video_path}")
            
            # Upload reel
            media = self.client.clip_upload(
                Path(video_path),
                caption=caption,
                thumbnail=Path(thumbnail_path) if thumbnail_path else None
            )
            
            post_info = {
                'id': media.id,
                'code': media.code,
                'url': f"https://www.instagram.com/reel/{media.code}/",
                'posted_at': media.taken_at,
            }
            
            logger.info(f"Reel posted successfully: {post_info['url']}")
            return post_info
            
        except LoginRequired as e:
            logger.error("Login required, re-authenticating")
            self.client = None
            if self.login():
                return self.post_reel(video_path, caption, thumbnail_path)
            return None
            
        except Exception as e:
            logger.error(f"Error posting reel: {e}")
            return None
    
    def post_video(self, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Optional[Dict]:
        """
        Post a regular video
        Returns post information or None if failed
        """
        if not self.client:
            if not self.login():
                return None
        
        try:
            logger.info(f"Posting video to Instagram: {video_path}")
            
            # Upload video
            media = self.client.video_upload(
                Path(video_path),
                caption=caption,
                thumbnail=Path(thumbnail_path) if thumbnail_path else None
            )
            
            post_info = {
                'id': media.id,
                'code': media.code,
                'url': f"https://www.instagram.com/p/{media.code}/",
                'posted_at': media.taken_at,
            }
            
            logger.info(f"Video posted successfully: {post_info['url']}")
            return post_info
            
        except LoginRequired as e:
            logger.error("Login required, re-authenticating")
            self.client = None
            if self.login():
                return self.post_video(video_path, caption, thumbnail_path)
            return None
            
        except Exception as e:
            logger.error(f"Error posting video: {e}")
            return None
    
    def get_media_info(self, media_id: str) -> Optional[Dict]:
        """Get information about a posted media"""
        if not self.client:
            if not self.login():
                return None
        
        try:
            media = self.client.media_info(media_id)
            
            return {
                'id': media.id,
                'code': media.code,
                'likes': media.like_count,
                'comments': media.comment_count,
                'views': getattr(media, 'view_count', 0) or getattr(media, 'play_count', 0),
            }
            
        except Exception as e:
            logger.error(f"Error getting media info: {e}")
            return None
    
    def delete_media(self, media_id: str) -> bool:
        """Delete a media post"""
        if not self.client:
            if not self.login():
                return False
        
        try:
            self.client.media_delete(media_id)
            logger.info(f"Media deleted: {media_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.client:
            if not self.login():
                return None
        
        try:
            user_id = self.client.user_id
            user_info = self.client.user_info(user_id)
            
            return {
                'username': user_info.username,
                'full_name': user_info.full_name,
                'followers': user_info.follower_count,
                'following': user_info.following_count,
                'posts': user_info.media_count,
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def logout(self):
        """Logout from Instagram"""
        if self.client:
            try:
                self.client.logout()
                logger.info("Logged out from Instagram")
            except Exception as e:
                logger.error(f"Error logging out: {e}")
