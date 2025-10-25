"""AI-powered caption and hashtag generation"""

import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

class CaptionGenerator:
    """Generates captions and hashtags using AI"""
    
    def __init__(self, config):
        self.config = config
        self.ai_provider = config.ai_provider
        
        if self.ai_provider == 'openai':
            self._init_openai()
        elif self.ai_provider == 'anthropic':
            self._init_anthropic()
        else:
            logger.warning(f"Unknown AI provider: {self.ai_provider}, using template-based generation")
            self.ai_client = None
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            openai.api_key = self.config.openai_api_key
            self.ai_client = openai
            logger.info("OpenAI client initialized")
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            self.ai_client = None
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {e}")
            self.ai_client = None
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.ai_client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
            logger.info("Anthropic client initialized")
        except ImportError:
            logger.error("Anthropic package not installed. Run: pip install anthropic")
            self.ai_client = None
        except Exception as e:
            logger.error(f"Error initializing Anthropic: {e}")
            self.ai_client = None
    
    def generate_caption(self, video_info: Dict) -> Dict[str, any]:
        """
        Generate caption and hashtags for a video
        Returns dict with 'caption', 'hashtags', 'full_caption'
        """
        logger.info(f"Generating caption for video: {video_info.get('title')}")
        
        if self.ai_client:
            return self._generate_ai_caption(video_info)
        else:
            return self._generate_template_caption(video_info)
    
    def _generate_ai_caption(self, video_info: Dict) -> Dict[str, any]:
        """Generate caption using AI"""
        title = video_info.get('title', '')
        description = video_info.get('description', '')[:500]  # Limit description length
        category = self.config.get('content.category', 'General')
        style = self.config.get('caption.style', 'inspiring')
        
        prompt = self._create_prompt(title, description, category, style)
        
        try:
            if self.ai_provider == 'openai':
                response = self._call_openai(prompt)
            else:
                response = self._call_anthropic(prompt)
            
            return self._parse_ai_response(response)
            
        except Exception as e:
            logger.error(f"Error generating AI caption: {e}")
            return self._generate_template_caption(video_info)
    
    def _create_prompt(self, title: str, description: str, category: str, style: str) -> str:
        """Create prompt for AI caption generation"""
        include_emojis = self.config.get('caption.include_emojis', True)
        call_to_action = self.config.get('caption.call_to_action', True)
        hashtag_count = self.config.get('caption.hashtag_count', 15)
        max_length = self.config.get('caption.max_length', 2200)
        
        prompt = f"""Create an engaging Instagram Reels caption for a {category} video.

Video Title: {title}
Video Description: {description}

Style: {style}
{"Include relevant emojis" if include_emojis else "No emojis"}
{"Include a call-to-action at the end" if call_to_action else ""}

Requirements:
- Write a caption that is {style} and engaging
- Maximum length: {max_length} characters
- Generate {hashtag_count} relevant and trending hashtags
- Format: First the caption text, then hashtags on separate lines

Please provide:
1. A compelling caption (2-3 sentences)
2. {hashtag_count} relevant hashtags

Format your response as:
CAPTION: [your caption here]
HASHTAGS: [hashtags separated by spaces]
"""
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Instagram content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        try:
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict[str, any]:
        """Parse AI response into caption and hashtags"""
        lines = response.strip().split('\n')
        caption = ""
        hashtags = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('CAPTION:'):
                caption = line.replace('CAPTION:', '').strip()
            elif line.startswith('HASHTAGS:'):
                hashtags_str = line.replace('HASHTAGS:', '').strip()
                hashtags = [tag.strip() for tag in hashtags_str.split() if tag.strip().startswith('#')]
        
        # Add custom hashtags
        custom_hashtags = self.config.get('caption.custom_hashtags', [])
        for tag in custom_hashtags:
            if tag not in hashtags:
                hashtags.append(tag)
        
        # Add call to action if configured
        if self.config.get('caption.call_to_action', True) and caption:
            cta = self._get_call_to_action()
            if cta not in caption:
                caption = f"{caption}\n\n{cta}"
        
        # Combine caption and hashtags
        hashtags_str = ' '.join(hashtags[:30])  # Instagram allows max 30 hashtags
        full_caption = f"{caption}\n\n{hashtags_str}"
        
        return {
            'caption': caption,
            'hashtags': hashtags,
            'full_caption': full_caption
        }
    
    def _generate_template_caption(self, video_info: Dict) -> Dict[str, any]:
        """Generate caption using templates (fallback)"""
        title = video_info.get('title', '')
        category = self.config.get('content.category', 'content')
        style = self.config.get('caption.style', 'inspiring')
        
        templates = {
            'inspiring': [
                f"💪 {title}\n\nYour daily dose of motivation! Save this for when you need it. 🔥",
                f"✨ {title}\n\nLet this be your reminder to keep pushing forward! 💯",
                f"🎯 {title}\n\nTag someone who needs to see this! 🙌"
            ],
            'casual': [
                f"🔥 {title}\n\nWhat do you think? Drop a comment! 👇",
                f"💯 {title}\n\nDouble tap if you agree! ❤️",
                f"😍 {title}\n\nSave this for later! 📌"
            ],
            'informative': [
                f"📚 {title}\n\nLearn something new every day! Follow for more. 🎓",
                f"💡 {title}\n\nHope you found this helpful! 🙏",
                f"🎯 {title}\n\nShare this with someone who needs it! 👥"
            ]
        }
        
        caption_templates = templates.get(style, templates['inspiring'])
        caption = random.choice(caption_templates)
        
        # Add call to action
        if self.config.get('caption.call_to_action', True):
            cta = self._get_call_to_action()
            caption = f"{caption}\n\n{cta}"
        
        # Generate hashtags
        hashtags = self._generate_hashtags(category)
        
        hashtags_str = ' '.join(hashtags)
        full_caption = f"{caption}\n\n{hashtags_str}"
        
        return {
            'caption': caption,
            'hashtags': hashtags,
            'full_caption': full_caption
        }
    
    def _generate_hashtags(self, category: str) -> List[str]:
        """Generate relevant hashtags"""
        custom_hashtags = self.config.get('caption.custom_hashtags', [])
        hashtag_count = self.config.get('caption.hashtag_count', 15)
        
        # Category-specific hashtags
        category_hashtags = {
            'motivational': [
                '#motivation', '#motivational', '#inspiration', '#inspire',
                '#mindset', '#success', '#goals', '#hustle', '#grind',
                '#positivevibes', '#motivationalquotes', '#successquotes',
                '#dailymotivation', '#motivated', '#entrepreneur'
            ],
            'tech': [
                '#technology', '#tech', '#innovation', '#ai', '#future',
                '#artificialintelligence', '#coding', '#programming',
                '#software', '#techtrends', '#digital', '#startup'
            ],
            'comedy': [
                '#funny', '#comedy', '#humor', '#memes', '#lol',
                '#funnyvideos', '#viral', '#entertainment', '#hilarious'
            ],
        }
        
        # Get category hashtags
        category_key = category.lower()
        base_hashtags = category_hashtags.get(category_key, [])
        
        # Common Instagram hashtags
        common_hashtags = [
            '#viral', '#trending', '#explore', '#reels', '#reelsinstagram',
            '#instareels', '#explorepage', '#fyp', '#foryou', '#instagood'
        ]
        
        # Combine all hashtags
        all_hashtags = list(set(custom_hashtags + base_hashtags + common_hashtags))
        
        # Return requested number of hashtags
        return all_hashtags[:hashtag_count]
    
    def _get_call_to_action(self) -> str:
        """Get a call to action"""
        ctas = [
            "Follow for more! 🔥",
            "Follow for daily content! 💯",
            "Like & Follow for more! ❤️",
            "Save & Share with friends! 📌",
            "Follow us for more amazing content! 🚀"
        ]
        return random.choice(ctas)
