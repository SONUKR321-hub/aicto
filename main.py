"""Main entry point for YouTube-to-Instagram Agent"""

import argparse
import logging
import sys
import time
from pathlib import Path
from colorlog import ColoredFormatter
from agent.config import Config
from agent.youtube_scraper import YouTubeScraper
from agent.video_editor import VideoEditor
from agent.caption_generator import CaptionGenerator
from agent.instagram_poster import InstagramPoster
from agent.analytics import Analytics
from agent.scheduler import Scheduler

def setup_logging(log_level: str = "INFO"):
    """Setup colored logging"""
    log_format = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler('logs/agent.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)

class YouTubeToInstagramAgent:
    """Main agent class"""
    
    def __init__(self, config_path: str = "config.yaml", test_mode: bool = False):
        self.config = Config(config_path)
        self.test_mode = test_mode
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scraper = YouTubeScraper(self.config)
        self.editor = VideoEditor(self.config)
        self.caption_gen = CaptionGenerator(self.config)
        self.poster = InstagramPoster(self.config) if not test_mode else None
        self.analytics = Analytics(self.config)
        self.scheduler = Scheduler(self.config)
        
        self.logger.info("YouTube-to-Instagram Agent initialized")
    
    def run_once(self):
        """Run the agent once (find, process, and post one video)"""
        self.logger.info("=== Running agent once ===")
        
        try:
            # Step 1: Search for videos
            self.logger.info("Step 1: Searching for videos on YouTube")
            keywords = self.config.get('content.youtube_source_keywords', [])
            max_results = self.config.get('youtube.max_videos_to_check', 50)
            
            videos = self.scraper.search_videos(keywords, max_results)
            
            if not videos:
                self.logger.warning("No suitable videos found")
                return False
            
            # Check if video was already posted
            video = self._get_unposted_video(videos)
            if not video:
                self.logger.warning("No new videos to post (all already posted)")
                return False
            
            self.logger.info(f"Selected video: {video['title']}")
            
            # Step 2: Download video
            self.logger.info("Step 2: Downloading video")
            video_path = self.scraper.download_video(video)
            
            if not video_path:
                self.logger.error("Failed to download video")
                return False
            
            # Step 3: Edit video
            self.logger.info("Step 3: Processing video")
            edited_path = self.editor.process_video(video_path, video['id'])
            
            if not edited_path:
                self.logger.error("Failed to process video")
                return False
            
            # Step 4: Generate caption
            self.logger.info("Step 4: Generating caption")
            caption_data = self.caption_gen.generate_caption(video)
            caption = caption_data['full_caption']
            
            self.logger.info(f"Generated caption: {caption[:100]}...")
            
            # Step 5: Post to Instagram (if not test mode)
            if self.test_mode:
                self.logger.info("TEST MODE: Skipping Instagram posting")
                self.logger.info(f"Video ready: {edited_path}")
                self.logger.info(f"Caption: {caption}")
                return True
            
            self.logger.info("Step 5: Posting to Instagram")
            post_type = self.config.get('instagram.post_type', 'reel')
            
            if post_type == 'reel':
                post_info = self.poster.post_reel(edited_path, caption)
            else:
                post_info = self.poster.post_video(edited_path, caption)
            
            if not post_info:
                self.logger.error("Failed to post to Instagram")
                return False
            
            # Step 6: Track analytics
            self.logger.info("Step 6: Tracking post")
            self.analytics.track_post({
                'video_id': video['id'],
                'instagram_media_id': post_info['id'],
                'instagram_code': post_info['code'],
                'instagram_url': post_info['url'],
                'youtube_title': video['title'],
                'youtube_url': video['url'],
                'caption': caption_data['caption'],
                'hashtags': caption_data['hashtags'],
                'category': self.config.get('content.category'),
            })
            
            self.logger.info(f"✅ Post successful! URL: {post_info['url']}")
            
            # Cleanup if configured
            if self.config.get('advanced.cleanup_downloads', True):
                self._cleanup_files(video_path, edited_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in run_once: {e}", exc_info=True)
            return False
    
    def run_daemon(self):
        """Run the agent as a daemon with scheduled posting"""
        self.logger.info("=== Starting agent in daemon mode ===")
        
        if self.test_mode:
            self.logger.warning("Test mode enabled - posts will not be made to Instagram")
        
        # Schedule regular posts
        self.scheduler.schedule_posts(self.run_once)
        
        # Schedule analytics updates
        self.scheduler.schedule_analytics_update(self.update_analytics)
        
        # Start scheduler
        self.scheduler.start()
        
        self.logger.info("Agent is running. Press Ctrl+C to stop.")
        self.logger.info(f"Scheduled jobs: {self.scheduler.get_scheduled_jobs()}")
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Stopping agent...")
            self.scheduler.stop()
            self.analytics.close()
    
    def update_analytics(self):
        """Update analytics for recent posts"""
        self.logger.info("Updating analytics...")
        
        try:
            if self.test_mode:
                return
            
            # Get recent posts (last 10)
            posts = self.analytics.get_all_posts(limit=10)
            
            for post in posts:
                media_id = post.get('instagram_media_id')
                if not media_id:
                    continue
                
                # Get current metrics
                metrics = self.poster.get_media_info(media_id)
                
                if metrics:
                    self.analytics.update_post_metrics(post['video_id'], metrics)
            
            # Print statistics
            stats = self.analytics.get_statistics()
            self.logger.info(f"Analytics: {stats}")
            
        except Exception as e:
            self.logger.error(f"Error updating analytics: {e}")
    
    def show_stats(self):
        """Show analytics statistics"""
        print("\n=== Analytics Statistics ===\n")
        
        stats = self.analytics.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print("\n=== Best Performing Posts ===\n")
        best_posts = self.analytics.get_best_performing_posts(5)
        for i, post in enumerate(best_posts, 1):
            print(f"{i}. {post['youtube_title']}")
            print(f"   Engagement: {post['engagement_rate']:.2f}%")
            print(f"   Likes: {post['likes']}, Comments: {post['comments']}, Views: {post['views']}")
            print(f"   URL: {post['instagram_url']}\n")
        
        if self.config.get('analytics.optimization.enabled', True):
            print("=== Optimization Insights ===\n")
            
            best_times = self.analytics.get_best_posting_times()
            if best_times:
                print(f"Best posting times: {', '.join(best_times)}")
            
            best_hashtags = self.analytics.get_best_hashtags(10)
            if best_hashtags:
                print(f"Best hashtags: {' '.join(best_hashtags)}")
    
    def _get_unposted_video(self, videos: list) -> dict:
        """Get first video that hasn't been posted yet"""
        for video in videos:
            if not self.analytics.get_post(video['id']):
                return video
        return None
    
    def _cleanup_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if file_path and Path(file_path).exists():
                    Path(file_path).unlink()
                    self.logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {file_path}: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="YouTube-to-Instagram Auto Poster Agent")
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode')
    parser.add_argument('--test', action='store_true', help='Test mode (no posting)')
    parser.add_argument('--stats', action='store_true', help='Show analytics statistics')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("🤖 YouTube-to-Instagram Auto Poster Agent")
    logger.info("=" * 50)
    
    try:
        # Initialize agent
        agent = YouTubeToInstagramAgent(args.config, test_mode=args.test)
        
        # Validate configuration
        if not agent.config.validate():
            logger.error("Configuration validation failed. Please check your config.yaml and .env files.")
            sys.exit(1)
        
        # Show stats
        if args.stats:
            agent.show_stats()
            sys.exit(0)
        
        # Run agent
        if args.daemon:
            agent.run_daemon()
        else:
            success = agent.run_once()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("\nAgent stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
