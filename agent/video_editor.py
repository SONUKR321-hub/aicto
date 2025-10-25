"""Video editing and optimization for Instagram"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
)
from moviepy.video.fx import resize, crop
from PIL import Image, ImageDraw, ImageFont
import subprocess

logger = logging.getLogger(__name__)

class VideoEditor:
    """Handles video editing and optimization for Instagram Reels"""
    
    def __init__(self, config):
        self.config = config
        self.output_path = Path("data/edited")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def process_video(self, video_path: str, video_id: str) -> Optional[str]:
        """
        Process video for Instagram: resize, add subtitles, watermark
        Returns path to processed video or None if failed
        """
        logger.info(f"Processing video: {video_path}")
        
        try:
            clip = VideoFileClip(video_path)
            
            # Convert to 9:16 aspect ratio
            clip = self._convert_to_reels_format(clip)
            
            # Add watermark
            if self.config.get('editing.watermark.enabled', True):
                clip = self._add_watermark(clip)
            
            # Add intro/outro if configured
            if self.config.get('editing.intro_outro.enabled', False):
                clip = self._add_intro_outro(clip)
            
            # Export video
            output_file = self.output_path / f"{video_id}_edited.mp4"
            self._export_video(clip, output_file)
            
            clip.close()
            
            logger.info(f"Video processed successfully: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None
    
    def _convert_to_reels_format(self, clip: VideoFileClip) -> VideoFileClip:
        """Convert video to Instagram Reels format (9:16)"""
        target_width, target_height = self.config.get('editing.output_resolution', [1080, 1920])
        target_fps = self.config.get('editing.fps', 30)
        
        # Get current dimensions
        current_width, current_height = clip.size
        current_ratio = current_width / current_height
        target_ratio = target_width / target_height
        
        if abs(current_ratio - target_ratio) < 0.01:
            # Already correct ratio, just resize
            clip = clip.resize((target_width, target_height))
        else:
            # Need to crop and resize
            if current_ratio > target_ratio:
                # Video is too wide, crop sides
                new_width = int(current_height * target_ratio)
                x_center = current_width / 2
                x1 = int(x_center - new_width / 2)
                clip = crop(clip, x1=x1, width=new_width)
            else:
                # Video is too tall, crop top/bottom
                new_height = int(current_width / target_ratio)
                y_center = current_height / 2
                y1 = int(y_center - new_height / 2)
                clip = crop(clip, y1=y1, height=new_height)
            
            clip = clip.resize((target_width, target_height))
        
        # Set FPS
        clip = clip.set_fps(target_fps)
        
        return clip
    
    def _add_watermark(self, clip: VideoFileClip) -> VideoFileClip:
        """Add watermark text to video"""
        watermark_text = self.config.get('editing.watermark.text', '@lostmoment8')
        position = self.config.get('editing.watermark.position', 'bottom-right')
        opacity = self.config.get('editing.watermark.opacity', 0.7)
        
        # Create text clip
        txt_clip = TextClip(
            watermark_text,
            fontsize=40,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        )
        
        # Set position
        if position == 'bottom-right':
            txt_clip = txt_clip.set_position(('right', 'bottom')).margin(right=20, bottom=20, opacity=0)
        elif position == 'bottom-left':
            txt_clip = txt_clip.set_position(('left', 'bottom')).margin(left=20, bottom=20, opacity=0)
        elif position == 'top-right':
            txt_clip = txt_clip.set_position(('right', 'top')).margin(right=20, top=20, opacity=0)
        elif position == 'top-left':
            txt_clip = txt_clip.set_position(('left', 'top')).margin(left=20, top=20, opacity=0)
        
        txt_clip = txt_clip.set_opacity(opacity).set_duration(clip.duration)
        
        # Composite video
        return CompositeVideoClip([clip, txt_clip])
    
    def _add_intro_outro(self, clip: VideoFileClip) -> VideoFileClip:
        """Add intro and outro clips"""
        clips = [clip]
        
        intro_path = self.config.get('editing.intro_outro.intro_path')
        outro_path = self.config.get('editing.intro_outro.outro_path')
        
        if intro_path and Path(intro_path).exists():
            intro = VideoFileClip(intro_path)
            intro = self._convert_to_reels_format(intro)
            clips.insert(0, intro)
        
        if outro_path and Path(outro_path).exists():
            outro = VideoFileClip(outro_path)
            outro = self._convert_to_reels_format(outro)
            clips.append(outro)
        
        if len(clips) > 1:
            return concatenate_videoclips(clips)
        
        return clip
    
    def _export_video(self, clip: VideoFileClip, output_file: Path):
        """Export video with optimized settings for Instagram"""
        output_format = self.config.get('editing.output_format', 'mp4')
        
        clip.write_videofile(
            str(output_file),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=f'temp-audio-{output_file.stem}.m4a',
            remove_temp=True,
            fps=self.config.get('editing.fps', 30),
            preset='medium',
            bitrate='8000k',
            audio_bitrate='192k',
            threads=4,
            logger=None
        )
    
    def add_subtitles(self, video_path: str, subtitles: list) -> Optional[str]:
        """
        Add subtitles to video
        subtitles: list of dicts with 'start', 'end', 'text'
        """
        if not self.config.get('editing.add_subtitles', True):
            return video_path
        
        try:
            clip = VideoFileClip(video_path)
            subtitle_clips = []
            
            style = self.config.get('editing.subtitle_style', {})
            font_size = style.get('font_size', 40)
            font_color = style.get('font_color', 'white')
            stroke_color = style.get('stroke_color', 'black')
            stroke_width = style.get('stroke_width', 2)
            
            for sub in subtitles:
                txt_clip = TextClip(
                    sub['text'],
                    fontsize=font_size,
                    color=font_color,
                    font='Arial-Bold',
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='caption',
                    size=(clip.w * 0.9, None)
                )
                
                txt_clip = txt_clip.set_position(('center', 0.8), relative=True)
                txt_clip = txt_clip.set_start(sub['start']).set_end(sub['end'])
                subtitle_clips.append(txt_clip)
            
            final_clip = CompositeVideoClip([clip] + subtitle_clips)
            
            output_file = Path(video_path).parent / f"{Path(video_path).stem}_subtitled.mp4"
            self._export_video(final_clip, output_file)
            
            clip.close()
            final_clip.close()
            
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            return video_path
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 0.0
    
    def extract_thumbnail(self, video_path: str, output_path: str = None) -> Optional[str]:
        """Extract thumbnail from video"""
        try:
            clip = VideoFileClip(video_path)
            frame = clip.get_frame(clip.duration / 2)  # Middle frame
            
            if output_path is None:
                output_path = Path(video_path).parent / f"{Path(video_path).stem}_thumbnail.jpg"
            
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path)
            
            clip.close()
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {e}")
            return None
