"""
Video editor module for the travel assistant application.
Contains functions for creating videos from images with audio and effects.
"""

import os
import re
import sys
import tempfile
from typing import List, Optional, Dict, Any
import moviepy.editor as mpy
from moviepy.video.fx.all import fadein, fadeout

# Add the src directory to Python path
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import AI client
from api.openai_client import get_client


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


def parse_video_script(script: str) -> Dict[str, Any]:
    """
    Parse the video script to extract video parameters.
    
    Args:
        script: Generated video script text
        
    Returns:
        Dictionary of video parameters
    """
    params = {
        'fps': 24,
        'duration_per_image': 3.0,
        'transition_duration': 0.5,
        'animation_type': 'fade'
    }
    
    try:
        # Extract duration per image
        duration_match = re.search(r'时长[:：]\s*(\d+(?:\.\d+)?)\s*秒', script)
        if duration_match:
            params['duration_per_image'] = float(duration_match.group(1))
        
        # Extract transition duration
        transition_match = re.search(r'转场[:：]\s*(\d+(?:\.\d+)?)\s*秒', script)
        if transition_match:
            params['transition_duration'] = float(transition_match.group(1))
        
        # Extract animation type
        if '缩放' in script or '放大' in script or '缩小' in script:
            params['animation_type'] = 'zoom'
        elif '平移' in script or '移动' in script or '摇镜头' in script:
            params['animation_type'] = 'pan'
        elif '淡入淡出' in script or '渐变' in script:
            params['animation_type'] = 'fade'
        
        # Extract FPS if mentioned
        fps_match = re.search(r'(\d+)fps|(\d+)FPS', script)
        if fps_match:
            params['fps'] = int(fps_match.group(1) or fps_match.group(2))
            
    except Exception as e:
        # If parsing fails, use default parameters
        print(f"脚本解析失败，使用默认参数: {str(e)}")
    
    return params


def create_ai_video(
    images: List[str],
    audio: Optional[str] = None
) -> str:
    """
    Create a video from images using AI generated script.
    
    Args:
        images: List of image file paths
        audio: Optional audio file path
        
    Returns:
        Path to the created video file
    """
    try:
        # Get AI client instance
        client = get_client()
        
        # Analyze images using Qwen3-VL model
        print("正在分析图片内容...")
        image_descriptions = client.analyze_images(images)
        
        # Generate video script using DeepSeek model
        print("正在生成视频脚本...")
        script = client.generate_video_script(image_descriptions, audio)
        print(f"生成的脚本:\n{script}")
        
        # Parse script to get video parameters
        params = parse_video_script(script)
        print(f"解析后的参数: {params}")
        
        # Create video using parsed parameters
        print("正在制作视频...")
        video_path = create_video_from_images(
            images=images,
            audio=audio,
            **params
        )
        
        return video_path
        
    except Exception as e:
        raise RuntimeError(f"AI视频制作失败: {str(e)}") from e
