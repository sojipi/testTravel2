"""
OpenAI API client module for the travel assistant application.
Handles all API communications with the AI model.
"""

import openai
import base64
from typing import Optional, Dict, Any, List
from PIL import Image
import io
try:
    from ..config.config import (
        API_KEY, API_BASE, MODEL_NAME, MAX_TOKENS, TEMPERATURE,
        MODELSCOPE_API_KEY, MODELSCOPE_BASE_URL,
        QWEN_MODEL_NAME, DEEPSEEK_MODEL_NAME
    )
except ImportError:
    # Handle direct execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.config import (
        API_KEY, API_BASE, MODEL_NAME, MAX_TOKENS, TEMPERATURE,
        MODELSCOPE_API_KEY, MODELSCOPE_BASE_URL, QWEN_MODEL_NAME, DEEPSEEK_MODEL_NAME
    )


class OpenAIClient:
    """OpenAI API client for travel assistant functionality."""
    
    def __init__(self):
        """Initialize the OpenAI client with configuration."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client with API key and base URL."""
        if not API_KEY:
            raise ValueError("API密钥未设置。请在.env文件中设置MODEL_API_KEY")
        
        self.client = openai.OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )
    
    def generate_response(self, 
                         system_prompt: str, 
                         user_prompt: str, 
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None,
                         model_name: Optional[str] = None,
                         use_modelscope: bool = False) -> str:
        """
        Generate a response using the OpenAI API.
        
        Args:
            system_prompt: The system prompt to guide the AI behavior
            user_prompt: The user's input prompt
            max_tokens: Maximum tokens for the response (overrides default)
            temperature: Temperature for response generation (overrides default)
            model_name: Custom model name to use
            use_modelscope: Whether to use ModelScope API base URL
            
        Returns:
            The generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Use ModelScope configuration if requested
            client = self.client
            if use_modelscope:
                client = openai.OpenAI(
                    api_key=MODELSCOPE_API_KEY,
                    base_url=MODELSCOPE_BASE_URL
                )
                
            response = client.chat.completions.create(
                model=model_name or MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens or MAX_TOKENS,
                temperature=temperature or TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def generate_destination_recommendations(self, 
                                           season: str, 
                                           health_status: str, 
                                           budget: str, 
                                           interests: str) -> str:
        """
        Generate destination recommendations based on user preferences.
        
        Args:
            season: The travel season
            health_status: User's health status
            budget: Budget range
            interests: Selected interests
            
        Returns:
            Generated destination recommendations
        """
        try:
            from ..config.config import DESTINATION_SYSTEM_PROMPT
        except ImportError:
            from config.config import DESTINATION_SYSTEM_PROMPT
        
        user_prompt = f"""
请根据以下条件推荐适合银发族的国内旅行目的地：

1. 季节：{season}
2. 健康状况：{health_status}
3. 预算范围：{budget}
4. 兴趣偏好：{interests}

请推荐3-5个目的地，并说明推荐理由，考虑以下因素：
- 气候适宜性
- 交通便利程度
- 医疗条件
- 住宿条件
- 景点特色
- 适合老年人的活动
- 安全因素

请用温暖、耐心的语气，像对待长辈一样详细说明每个推荐地的特点。
"""
        
        return self.generate_response(DESTINATION_SYSTEM_PROMPT, user_prompt)
    
    def generate_itinerary_plan(self, 
                              destination: str, 
                              duration: str, 
                              mobility: str, 
                              health_focus: str) -> str:
        """
        Generate a detailed itinerary plan.
        
        Args:
            destination: Travel destination
            duration: Trip duration
            mobility: Mobility status
            health_focus: Health concerns
            
        Returns:
            Generated itinerary plan
        """
        try:
            from ..config.config import ITINERARY_SYSTEM_PROMPT
        except ImportError:
            from config.config import ITINERARY_SYSTEM_PROMPT
        
        user_prompt = f"""
请为银发族制定一份详细的旅行行程计划：

1. 目的地：{destination}
2. 旅行时长：{duration}
3. 行动能力：{mobility}
4. 健康关注点：{health_focus}

请制定一份详细的行程计划，包括：
- 每日具体安排（时间、地点、活动）
- 交通方式和路线
- 住宿推荐
- 餐饮建议
- 休息安排
- 注意事项
- 应急准备

请特别考虑银发族的特点，安排充足的休息时间，避免过于紧凑的行程。
请用温暖、关怀的语气，像为父母规划旅行一样细心周到。
"""
        
        return self.generate_response(ITINERARY_SYSTEM_PROMPT, user_prompt)
    
    def generate_checklist(self, 
                          origin: str, 
                          destination: str, 
                          duration: str, 
                          special_needs: str,
                          itinerary_text: str = "") -> str:
        """
        Generate a comprehensive travel checklist.
        
        Args:
            origin: Departure location
            destination: Travel destination
            duration: Trip duration
            special_needs: Special requirements
            itinerary_text: Optional itinerary text for context
            
        Returns:
            Generated travel checklist
        """
        try:
            from ..config.config import CHECKLIST_SYSTEM_PROMPT
        except ImportError:
            from config.config import CHECKLIST_SYSTEM_PROMPT
        
        itinerary_context = f"\n参考行程：{itinerary_text}" if itinerary_text else ""
        
        user_prompt = f"""
请为银发族生成一份详细的旅行清单：

1. 出发地：{origin}
2. 目的地：{destination}
3. 旅行时长：{duration}
4. 特殊需求：{special_needs}
{itinerary_context}

请生成一份详细的旅行清单，包括：
- 证件类（身份证、医保卡、老年证等）
- 衣物类（根据季节和目的地气候）
- 药品类（常用药品、应急药品）
- 生活用品类
- 电子设备类
- 财务准备
- 安全用品
- 娱乐用品
- 特殊用品（根据健康状况）

请用JSON格式返回，包含以下字段：
- documents: 证件类清单
- clothing: 衣物类清单
- medications: 药品类清单
- daily_items: 生活用品清单
- electronics: 电子设备清单
- financial: 财务准备清单
- safety: 安全用品清单
- entertainment: 娱乐用品清单
- special_items: 特殊用品清单
- tips: 温馨提示列表

请用温暖、细致的语气，像为父母准备行李一样周到贴心。
"""
        
        return self.generate_response(CHECKLIST_SYSTEM_PROMPT, user_prompt)


    def analyze_images(self, image_paths: List[str]) -> List[str]:
        """
        Analyze images using Qwen3-VL model to get image descriptions.
        
        Args:
            image_paths: List of image file paths to analyze
            
        Returns:
            List of image descriptions
        """
        system_prompt = "你是一个专业的图像分析助手，请详细描述每张图片的内容，包括场景、人物、物体、氛围等信息，输出语言为中文。"
        
        descriptions = []
        
        for image_path in image_paths:
            try:
                # Open and process image to reduce size
                with Image.open(image_path) as img:
                    # Convert to RGB if needed
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Resize image to maximum 1024x1024
                    max_dimension = 1024
                    width, height = img.size
                    if width > max_dimension or height > max_dimension:
                        ratio = min(max_dimension / width, max_dimension / height)
                        new_width = int(width * ratio)
                        new_height = int(height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Compress image to reduce file size
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85, optimize=True)
                    buffer.seek(0)
                    
                    # Encode image to base64
                    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                user_prompt = f"请详细描述这张图片的内容：![image](data:image/jpeg;base64,{base64_image})"
                
                # Use Qwen3-VL model for image analysis
                description = self.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=1024,
                    temperature=0.3,
                    model_name=QWEN_MODEL_NAME,
                    use_modelscope=True
                )
                
                descriptions.append(description)
            except Exception as e:
                raise Exception(f"图片分析失败 {image_path}: {str(e)}")
        
        return descriptions
    
    def generate_video_script(self, image_descriptions: List[str], audio_path: Optional[str] = None) -> str:
        """
        Generate video script based on image descriptions and audio information.
        
        Args:
            image_descriptions: List of image descriptions
            audio_path: Path to background audio file
            
        Returns:
            Generated video script
        """
        try:
            system_prompt = "你是一个专业的视频脚本创作大师，请根据图片分析结果生成详细的视频制作脚本。脚本需要包含：每个镜头的时长、画面描述、动画效果、转场方式等信息，适合用于AI视频生成。"
            
            formatted_descriptions = "\n\n".join([f"镜头{i+1}：{desc}" for i, desc in enumerate(image_descriptions)])
            
            # Add audio information if provided
            audio_info = f"\n\n背景音乐：{audio_path}" if audio_path else ""
            
            user_prompt = f"请根据以下图片分析结果生成视频脚本：\n\n{formatted_descriptions}{audio_info}"
            
            # Generate the video script using DeepSeek model
            script = self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=2048,
                temperature=0.7,
                model_name=DEEPSEEK_MODEL_NAME,
                use_modelscope=True
            )
            
            return script
        except Exception as e:
            raise Exception(f"视频脚本生成失败: {str(e)}")


# Global client instance
_client_instance = None

def get_client() -> OpenAIClient:
    """Get the global OpenAI client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance