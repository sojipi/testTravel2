"""
Utility functions module for the travel assistant application.
Contains helper functions for validation, cleaning, and general utilities.
"""

import json
import re
from typing import Dict, Any, List, Optional
try:
    from config.config import MAX_INPUT_LENGTH, ALLOWED_SEASONS, ALLOWED_HEALTH_STATUS, ALLOWED_BUDGET, ALLOWED_MOBILITY, ALLOWED_DURATION
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.config import MAX_INPUT_LENGTH, ALLOWED_SEASONS, ALLOWED_HEALTH_STATUS, ALLOWED_BUDGET, ALLOWED_MOBILITY, ALLOWED_DURATION


def clean_response(response_text: str) -> str:
    """
    Clean and format the AI response text.
    
    Args:
        response_text: Raw response text from AI
        
    Returns:
        Cleaned and formatted response text
    """
    # Remove markdown formatting
    response_text = re.sub(r'```json\n?', '', response_text)
    response_text = re.sub(r'\n?```', '', response_text)
    
    # Remove leading/trailing whitespace
    response_text = response_text.strip()
    
    # Remove extra blank lines
    response_text = re.sub(r'\n{3,}', '\n\n', response_text)
    
    return response_text


def validate_inputs(inputs: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate user inputs for safety and correctness.
    
    Args:
        inputs: Dictionary of user inputs
        
    Returns:
        Dictionary with validation results (empty if valid, error messages if invalid)
    """
    errors = {}
    
    # Validate text inputs
    text_fields = ['destination', 'origin', 'special_needs']
    for field in text_fields:
        if field in inputs and inputs[field]:
            if len(inputs[field]) > MAX_INPUT_LENGTH:
                errors[field] = f"输入内容过长，请控制在{MAX_INPUT_LENGTH}字符以内"
            
            # Check for potentially harmful content
            if re.search(r'<script|javascript:|onerror=|onload=', inputs[field], re.IGNORECASE):
                errors[field] = "输入内容包含不安全字符"
    
    # Validate dropdown selections
    if 'season' in inputs and inputs['season'] not in ALLOWED_SEASONS:
        errors['season'] = "请选择有效的季节选项"
    
    if 'health_status' in inputs and inputs['health_status'] not in ALLOWED_HEALTH_STATUS:
        errors['health_status'] = "请选择有效的健康状况"
    
    if 'budget' in inputs and inputs['budget'] not in ALLOWED_BUDGET:
        errors['budget'] = "请选择有效的预算范围"
    
    if 'mobility' in inputs and inputs['mobility'] not in ALLOWED_MOBILITY:
        errors['mobility'] = "请选择有效的行动能力选项"
    
    if 'duration' in inputs and inputs['duration'] not in ALLOWED_DURATION:
        errors['duration'] = "请选择有效的旅行时长"
    
    return errors


def safe_json_parse(json_string: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON string with error handling.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        # Clean the JSON string first
        json_string = clean_response(json_string)
        return json.loads(json_string)
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def format_interests(interests: List[str]) -> str:
    """
    Format interests list into a readable string.
    
    Args:
        interests: List of interest strings
        
    Returns:
        Formatted string of interests
    """
    if not interests:
        return "暂无特别偏好"
    
    return "、".join(interests)


def format_health_focus(health_focus: List[str]) -> str:
    """
    Format health focus list into a readable string.
    
    Args:
        health_focus: List of health focus strings
        
    Returns:
        Formatted string of health focuses
    """
    if not health_focus:
        return "暂无特别关注点"
    
    return "、".join(health_focus)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename or 'default'


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON content from text that might contain JSON.
    
    Args:
        text: Text that might contain JSON
        
    Returns:
        Extracted JSON string or None
    """
    # Look for JSON-like content between curly braces
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json_match.group(0)
    
    # Look for JSON-like content between square brackets
    json_match = re.search(r'\[[\s\S]*\]', text)
    if json_match:
        return json_match.group(0)
    
    return None


def is_valid_chinese_location(location: str) -> bool:
    """
    Basic validation for Chinese location names.
    
    Args:
        location: Location name to validate
        
    Returns:
        True if location appears valid
    """
    if not location or len(location.strip()) < 2:
        return False
    
    # Check if it contains Chinese characters
    if not re.search(r'[\u4e00-\u9fff]', location):
        return False
    
    # Check for obviously invalid patterns
    invalid_patterns = [
        r'<[^>]+>',  # HTML tags
        r'javascript:',  # JavaScript
        r'on\w+=',  # Event handlers
        r'[<>"\'&]',  # Special characters
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, location, re.IGNORECASE):
            return False
    
    return True


def extract_hotels_from_itinerary(itinerary_text: str) -> List[str]:
    """
    Extract hotel information from itinerary content.
    
    Args:
        itinerary_text: Itinerary content to extract hotels from
        
    Returns:
        List of hotel names found in the itinerary
    """
    if not itinerary_text:
        return []
    
    hotels = []
    
    # Hotel extraction patterns - comprehensive matching
    hotel_patterns = [
        r'(?:入住|住宿|下榻)[：:]\s*([^\n，,。.]+)',  # 入住: 名称
        r'(?:酒店|宾馆|度假村|客栈)[：:]\s*([^\n，,。.]+)',  # 酒店: 名称
        r'推荐(?:酒店|住宿)[：:]\s*([^\n，,。.]+)',  # 推荐酒店: 名称
        r'([^\n，,。.]*(?:酒店|宾馆|度假村|客栈)[^\n，,。.]*)',  # 包含酒店关键词
        r'([^\n，,。.]*(?:Hotel|Resort|Inn|Motel)[^\n，,。.]*)',  # 英文酒店关键词
        r'(?:位于|在)([^\n，,。.]*(?:酒店|宾馆|度假村|客栈)[^\n，,。.]*)',  # 位置描述
        r'(?:预订|预约)([^\n，,。.]*(?:酒店|宾馆|度假村|客栈)[^\n，,。.]*)',  # 预订描述
    ]
    
    for pattern in hotel_patterns:
        matches = re.findall(pattern, itinerary_text, re.IGNORECASE)
        hotels.extend(matches)
    
    # Additional extraction for specific formats
    # Look for patterns like "- 酒店名称" or "• 酒店名称"
    list_patterns = re.findall(r'[-•]\s*([^\n，,。.]*(?:酒店|宾馆|度假村|客栈)[^\n，,。.]*)', itinerary_text, re.IGNORECASE)
    hotels.extend(list_patterns)
    
    # Clean and deduplicate
    hotels = [hotel.strip() for hotel in hotels if hotel.strip()]
    hotels = list(dict.fromkeys(hotels))[:10]  # Remove duplicates and limit to 10
    
    return hotels