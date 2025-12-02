"""
Video editor module for the travel assistant application.
Contains functions for creating videos from images with audio and effects.
"""

import os
import tempfile
from typing import List, Optional, Dict, Any
import moviepy.editor as mpy
from moviepy.video.fx.all import fadein, fadeout

# Import AI client
from api.openai_client import OpenAIClient


def validate_media_files(images: List[str], audio: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate media files before processing.
    
    Args:
        images: List of image file paths
        audio: Optional audio file path
        
    Returns:
        Dict with validation results
    """
    errors = []
    
    # Validate images
    if not images:
        errors.append("请至少上传一张图片")
    else:
        for img_path in images:
            if not os.path.exists(img_path):
                errors.append(f"图片文件不存在: {img_path}")
            elif not os.path.isfile(img_path):
                errors.append(f"不是有效的图片文件: {img_path}")
    
    # Validate audio
    if audio:
        if not os.path.exists(audio):
            errors.append(f"音频文件不存在: {audio}")
        elif not os.path.isfile(audio):
            errors.append(f"不是有效的音频文件: {audio}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def analyze_images_and_generate_script(images: List[str], audio_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze images using AI and generate a video script.
    
    Args:
        images: List of image file paths
        audio_path: Optional audio file path
        
    Returns:
        Dictionary containing image analysis results and generated script
    """
    try:
        # Initialize OpenAI client
        openai_client = OpenAIClient()
        
        # Step 1: Analyze images using Qwen/Qwen3-VL-8B-Instruct model
        image_descriptions = []
        for i, img_path in enumerate(images):
            # Use OpenAIClient to analyze image with Qwen model
            # Note: This assumes OpenAIClient has been modified to support Qwen model
            image_analysis = openai_client.analyze_image_with_qwen(img_path)
            image_descriptions.append(f"图片{i+1}：{image_analysis}")
        
        # Step 2: Generate video script using deepseek-ai/DeepSeek-V3.2-Exp model
        system_prompt = "你是一个专业的视频脚本创作者，擅长根据图片内容和场景生成高质量的视频脚本。"
        
        user_prompt = f"""
        请根据以下图片描述和背景音乐，生成一个适合的视频脚本：
        
        图片描述：
        {chr(10).join(image_descriptions)}
        
        背景音乐：{audio_path if audio_path else '无'}
        
        请生成一个详细的视频脚本，包括：
        1. 视频整体风格和主题
        2. 每个图片的展示时长
        3. 图片之间的过渡效果
        4. 适合的动画效果
        5. 视频的整体节奏
        
        请以JSON格式返回，包含以下字段：
        - theme: 视频主题
        - style: 视频风格
        - fps: 帧率
        - duration_per_image: 每张图片的展示时长（秒）
        - transition_duration: 过渡时长（秒）
        - animation_type: 动画类型（fade, zoom, pan）
        - overall_duration: 视频总时长（秒）
        """
        
        script = openai_client.generate_response_with_deepseek(system_prompt, user_prompt)
        
        return {
            "image_analysis": image_descriptions,
            "script": script
        }
        
    except Exception as e:
        raise RuntimeError(f"AI分析和脚本生成失败: {str(e)}") from e


def parse_video_script(script: str) -> Dict[str, Any]:
    """
    Parse the video script JSON string into a dictionary of parameters.
    
    Args:
        script: JSON string containing the video script
        
    Returns:
        Dictionary of video parameters
    """
    import json
    
    try:
        script_data = json.loads(script)
        
        # Extract and validate parameters
        video_params = {
            'fps': script_data.get('fps', 24),
            'duration_per_image': script_data.get('duration_per_image', 3.0),
            'transition_duration': script_data.get('transition_duration', 0.5),
            'animation_type': script_data.get('animation_type', 'fade'),
        }
        
        # Validate parameter types
        if not isinstance(video_params['fps'], int) or video_params['fps'] <= 0:
            video_params['fps'] = 24
        
        if not isinstance(video_params['duration_per_image'], (int, float)) or video_params['duration_per_image'] <= 0:
            video_params['duration_per_image'] = 3.0
        
        if not isinstance(video_params['transition_duration'], (int, float)) or video_params['transition_duration'] < 0:
            video_params['transition_duration'] = 0.5
        
        if not isinstance(video_params['animation_type'], str) or video_params['animation_type'] not in ['fade', 'zoom', 'pan']:
            video_params['animation_type'] = 'fade'
        
        return video_params
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # If parsing fails, return default parameters
        return {
            'fps': 24,
            'duration_per_image': 3.0,
            'transition_duration': 0.5,
            'animation_type': 'fade',
        }


def create_video_with_ai(images: List[str], audio: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a video using AI to analyze images and generate a script.
    
    Args:
        images: List of image file paths
        audio: Optional audio file path
        
    Returns:
        Dictionary containing video path, image analysis results, and generated script
    """
    try:
        # Step 1: Analyze images and generate video script
        analysis_result = analyze_images_and_generate_script(images, audio)
        image_analysis = analysis_result["image_analysis"]
        script = analysis_result["script"]
        
        # Step 2: Parse script to extract video parameters
        video_params = parse_video_script(script)
        
        # Step 3: Create video using the extracted parameters
        video_path = create_video_from_images(
            images=images,
            audio=audio,
            **video_params
        )
        
        return {
            "video_path": video_path,
            "image_analysis": image_analysis,
            "script": script
        }
        
    except Exception as e:
        raise RuntimeError(f"AI视频制作失败: {str(e)}") from e


def create_video_from_images(
    images: List[str],
    audio: Optional[str] = None,
    fps: int = 24,
    duration_per_image: float = 3.0,
    transition_duration: float = 0.5,
    animation_type: str = "fade",
    target_width: int = 720,
    target_height: int = 1280  # 9:16 竖屏比例，适合手机播放
) -> str:
    """
    Create a video from images with optional audio, transitions, and animations.
    
    Args:
        images: List of image file paths
        audio: Optional audio file path
        fps: Frames per second
        duration_per_image: Duration to display each image (in seconds)
        transition_duration: Duration of transitions between images (in seconds)
        animation_type: Type of animation/transition to use
        
    Returns:
        Path to the created video file
    """
    try:
        # Validate input files
        validation = validate_media_files(images, audio)
        if not validation['valid']:
            raise ValueError(f"输入验证失败: {', '.join(validation['errors'])}")
        
        # Create image clips with animations
        image_clips = []
        for i, img_path in enumerate(images):
            # Create base image clip
            clip = mpy.ImageClip(img_path)
            
            # Resize and crop to fit target dimensions (maintaining aspect ratio)
            # First, resize the image to fit within target dimensions
            clip = clip.resize(height=target_height) if clip.h < clip.w else clip.resize(width=target_width)
            
            # Then, center and crop if necessary
            if clip.w > target_width:
                x_center = clip.w // 2
                y_center = clip.h // 2
                clip = clip.crop(x_center=x_center, y_center=y_center, width=target_width, height=target_height)
            
            # Set duration for each clip
            clip = clip.set_duration(duration_per_image)
            
            # Add animations based on selected type
            if animation_type == "fade":
                # Fade in and out
                clip = clip.fx(fadein, 0.5)
                clip = clip.fx(fadeout, 0.5)
            elif animation_type == "zoom":
                # Zoom in effect
                clip = clip.resize(lambda t: 1 + 0.05 * t)  # Zoom in over time
                clip = clip.set_position("center")
            elif animation_type == "pan":
                # Pan effect (slow movement)
                clip = clip.resize(1.2)  # Resize to allow panning
                def pan_position(t):
                    # Move from left to right slowly
                    return (int(100 * t), "center")
                clip = clip.set_position(pan_position)
            
            image_clips.append(clip)
        
        # Add transitions between clips
        if len(image_clips) > 1:
            # Use concatenate_videoclips with transition effect
            # First, we'll create a list of clips with fade out for all except last
            clips_with_transitions = []
            
            for i, clip in enumerate(image_clips):
                if i < len(image_clips) - 1:
                    # Add fade out to all clips except the last one
                    clip = clip.fx(fadeout, transition_duration)
                clips_with_transitions.append(clip)
            
            # Concatenate all clips
            video = mpy.concatenate_videoclips(clips_with_transitions, method="compose")
            
            # Add fade in to the first clip
            video = video.fx(fadein, transition_duration)
        else:
            # Only one clip, add fade in and out
            video = image_clips[0]
            video = video.fx(fadein, 0.5)
            video = video.fx(fadeout, 0.5)
        
        # Add audio if provided
        if audio:
            audio_clip = mpy.AudioFileClip(audio)
            
            # If audio is longer than video, trim audio
            # If audio is shorter than video, loop audio
            if audio_clip.duration > video.duration:
                audio_clip = audio_clip.subclip(0, video.duration)
            elif audio_clip.duration < video.duration:
                # Calculate how many times to loop the audio
                loop_count = int(video.duration / audio_clip.duration) + 1
                audio_clip = mpy.concatenate_audioclips([audio_clip] * loop_count)
                audio_clip = audio_clip.subclip(0, video.duration)
            
            # Set the audio to the video
            video = video.set_audio(audio_clip)
        
        # Set FPS and ensure target resolution
        video = video.set_fps(fps)
        video = video.resize(width=target_width, height=target_height)
        
        # Create temporary file to save the video
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            output_path = tmp.name
        
        # Write the video file
        video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset="medium"
        )
        
        # Close all clips to release resources
        video.close()
        for clip in image_clips:
            clip.close()
        if audio:
            audio_clip.close()
        
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"视频制作失败: {str(e)}") from e
