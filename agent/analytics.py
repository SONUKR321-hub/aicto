"""Analytics tracking and optimization"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class Post(Base):
    """Post model for tracking"""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    video_id = Column(String, unique=True)
    instagram_media_id = Column(String)
    instagram_code = Column(String)
    instagram_url = Column(String)
    youtube_title = Column(String)
    youtube_url = Column(String)
    caption = Column(Text)
    hashtags = Column(Text)
    category = Column(String)
    posted_at = Column(DateTime)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime)

class Analytics:
    """Handles analytics tracking and optimization"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = config.database_path
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def track_post(self, post_data: Dict) -> bool:
        """Track a new post"""
        try:
            post = Post(
                video_id=post_data.get('video_id'),
                instagram_media_id=post_data.get('instagram_media_id'),
                instagram_code=post_data.get('instagram_code'),
                instagram_url=post_data.get('instagram_url'),
                youtube_title=post_data.get('youtube_title'),
                youtube_url=post_data.get('youtube_url'),
                caption=post_data.get('caption'),
                hashtags=json.dumps(post_data.get('hashtags', [])),
                category=post_data.get('category'),
                posted_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.session.add(post)
            self.session.commit()
            
            logger.info(f"Post tracked: {post.video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking post: {e}")
            self.session.rollback()
            return False
    
    def update_post_metrics(self, video_id: str, metrics: Dict) -> bool:
        """Update metrics for a post"""
        try:
            post = self.session.query(Post).filter_by(video_id=video_id).first()
            
            if not post:
                logger.warning(f"Post not found: {video_id}")
                return False
            
            post.likes = metrics.get('likes', post.likes)
            post.comments = metrics.get('comments', post.comments)
            post.views = metrics.get('views', post.views)
            
            # Calculate engagement rate
            if post.views > 0:
                post.engagement_rate = (post.likes + post.comments) / post.views * 100
            
            post.last_updated = datetime.now()
            
            self.session.commit()
            
            logger.info(f"Metrics updated for post: {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            self.session.rollback()
            return False
    
    def get_post(self, video_id: str) -> Optional[Dict]:
        """Get post by video ID"""
        try:
            post = self.session.query(Post).filter_by(video_id=video_id).first()
            
            if not post:
                return None
            
            return self._post_to_dict(post)
            
        except Exception as e:
            logger.error(f"Error getting post: {e}")
            return None
    
    def get_all_posts(self, limit: int = 100) -> List[Dict]:
        """Get all posts"""
        try:
            posts = self.session.query(Post).order_by(Post.posted_at.desc()).limit(limit).all()
            return [self._post_to_dict(post) for post in posts]
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return []
    
    def get_best_performing_posts(self, limit: int = 10) -> List[Dict]:
        """Get best performing posts"""
        try:
            posts = self.session.query(Post).order_by(Post.engagement_rate.desc()).limit(limit).all()
            return [self._post_to_dict(post) for post in posts]
        except Exception as e:
            logger.error(f"Error getting best posts: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        try:
            posts = self.session.query(Post).all()
            
            if not posts:
                return {
                    'total_posts': 0,
                    'total_likes': 0,
                    'total_comments': 0,
                    'total_views': 0,
                    'avg_engagement_rate': 0,
                }
            
            total_likes = sum(p.likes for p in posts)
            total_comments = sum(p.comments for p in posts)
            total_views = sum(p.views for p in posts)
            avg_engagement = sum(p.engagement_rate for p in posts) / len(posts)
            
            return {
                'total_posts': len(posts),
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_views': total_views,
                'avg_engagement_rate': avg_engagement,
                'avg_likes_per_post': total_likes / len(posts),
                'avg_comments_per_post': total_comments / len(posts),
                'avg_views_per_post': total_views / len(posts),
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_best_posting_times(self) -> List[str]:
        """Analyze best posting times based on engagement"""
        try:
            posts = self.session.query(Post).filter(Post.engagement_rate > 0).all()
            
            if len(posts) < self.config.get('analytics.optimization.min_posts_for_optimization', 10):
                return []
            
            # Group by hour
            hour_engagement = {}
            for post in posts:
                hour = post.posted_at.hour
                if hour not in hour_engagement:
                    hour_engagement[hour] = []
                hour_engagement[hour].append(post.engagement_rate)
            
            # Calculate average engagement per hour
            hour_avg = {
                hour: sum(rates) / len(rates)
                for hour, rates in hour_engagement.items()
            }
            
            # Sort by engagement
            best_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)
            
            # Return top 3 hours
            return [f"{hour:02d}:00" for hour, _ in best_hours[:3]]
            
        except Exception as e:
            logger.error(f"Error analyzing posting times: {e}")
            return []
    
    def get_best_hashtags(self, limit: int = 10) -> List[str]:
        """Get best performing hashtags"""
        try:
            posts = self.session.query(Post).filter(Post.engagement_rate > 0).all()
            
            if not posts:
                return []
            
            # Count hashtag usage and engagement
            hashtag_data = {}
            for post in posts:
                hashtags = json.loads(post.hashtags)
                for tag in hashtags:
                    if tag not in hashtag_data:
                        hashtag_data[tag] = {'count': 0, 'total_engagement': 0}
                    hashtag_data[tag]['count'] += 1
                    hashtag_data[tag]['total_engagement'] += post.engagement_rate
            
            # Calculate average engagement per hashtag
            hashtag_avg = {
                tag: data['total_engagement'] / data['count']
                for tag, data in hashtag_data.items()
                if data['count'] >= 3  # Minimum 3 uses
            }
            
            # Sort by average engagement
            best_hashtags = sorted(hashtag_avg.items(), key=lambda x: x[1], reverse=True)
            
            return [tag for tag, _ in best_hashtags[:limit]]
            
        except Exception as e:
            logger.error(f"Error analyzing hashtags: {e}")
            return []
    
    def _post_to_dict(self, post: Post) -> Dict:
        """Convert post object to dictionary"""
        return {
            'id': post.id,
            'video_id': post.video_id,
            'instagram_media_id': post.instagram_media_id,
            'instagram_code': post.instagram_code,
            'instagram_url': post.instagram_url,
            'youtube_title': post.youtube_title,
            'youtube_url': post.youtube_url,
            'caption': post.caption,
            'hashtags': json.loads(post.hashtags) if post.hashtags else [],
            'category': post.category,
            'posted_at': post.posted_at.isoformat() if post.posted_at else None,
            'likes': post.likes,
            'comments': post.comments,
            'views': post.views,
            'engagement_rate': post.engagement_rate,
            'last_updated': post.last_updated.isoformat() if post.last_updated else None,
        }
    
    def export_data(self, output_file: str = "data/analytics_export.json"):
        """Export all analytics data"""
        try:
            posts = self.get_all_posts()
            stats = self.get_statistics()
            
            data = {
                'statistics': stats,
                'posts': posts,
                'exported_at': datetime.now().isoformat()
            }
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Analytics data exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False
    
    def close(self):
        """Close database session"""
        self.session.close()
