"""
Data processing module for the travel assistant application.
Contains functions for processing and formatting travel data.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

try:
    from ..utils.helpers import sanitize_filename
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.helpers import sanitize_filename


def save_checklist_data(data: Dict[str, Any], 
                       origin: str, 
                       destination: str, 
                       duration: str) -> Optional[str]:
    """
    Save checklist data to a JSON file.
    
    Args:
        data: Checklist data to save
        origin: Departure location
        destination: Travel destination
        duration: Trip duration
        
    Returns:
        Path to saved file or None if save failed
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = "checklist_data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_origin = origin.replace(" ", "_").replace("/", "_")[:20]
        safe_destination = destination.replace(" ", "_").replace("/", "_")[:20]
        filename = f"checklist_{safe_origin}_to_{safe_destination}_{duration}_{timestamp}.json"
        
        # Ensure filename is safe
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        filepath = os.path.join(data_dir, filename)
        
        # Add metadata
        data_with_metadata = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "origin": origin,
                "destination": destination,
                "duration": duration,
                "version": "1.0"
            },
            "checklist": data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)
        
        return filepath
        
    except Exception as e:
        print(f"保存清单数据失败: {e}")
        return None


def load_checklist_data(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load checklist data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Loaded checklist data or None if load failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Return the checklist data, not the metadata
        return data.get("checklist", data)
        
    except Exception as e:
        print(f"加载清单数据失败: {e}")
        return None


def format_travel_history(travel_data: List[Dict[str, Any]]) -> str:
    """
    Format travel history data for display.
    
    Args:
        travel_data: List of travel records
        
    Returns:
        Formatted HTML string
    """
    if not travel_data:
        return "<p>暂无旅行记录</p>"
    
    html = """
    <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;">
        <h3>旅行历史记录</h3>
        <div style="display: grid; gap: 15px;">
    """
    
    for record in travel_data:
        html += f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">
            <div style="display: flex; justify-content: between; align-items: center;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{record.get('destination', '未知目的地')}</h4>
                <span style="color: #666; font-size: 14px;">{record.get('date', '未知日期')}</span>
            </div>
            <p style="margin: 5px 0; color: #555;">出发地: {record.get('origin', '未知')}</p>
            <p style="margin: 5px 0; color: #555;">时长: {record.get('duration', '未知')}</p>
            <p style="margin: 5px 0; color: #555;">备注: {record.get('notes', '无')}</p>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


def process_weather_data(weather_data: Dict[str, Any]) -> str:
    """
    Process weather data and format for display.
    
    Args:
        weather_data: Raw weather data
        
    Returns:
        Formatted weather information HTML
    """
    try:
        location = weather_data.get("location", "未知地区")
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", [])
        
        html = f"""
        <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #74b9ff, #0984e3); color: white; padding: 20px; border-radius: 15px;">
            <h3 style="margin: 0 0 15px 0; text-align: center;">🌤️ {location} 天气信息</h3>
            
            <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0;">当前天气</h4>
                <p style="margin: 5px 0;">温度: {current.get('temperature', '未知')}°C</p>
                <p style="margin: 5px 0;">天气: {current.get('condition', '未知')}</p>
                <p style="margin: 5px 0;">湿度: {current.get('humidity', '未知')}%</p>
                <p style="margin: 5px 0;">风速: {current.get('wind_speed', '未知')} km/h</p>
            </div>
        """
        
        if forecast:
            html += """
            <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                <h4 style="margin: 0 0 10px 0;">未来预报</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px;">
            """
            
            for day in forecast[:5]:  # Show only 5 days
                html += f"""
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin: 0; font-weight: bold;">{day.get('date', '')}</p>
                    <p style="margin: 5px 0;">{day.get('condition', '未知')}</p>
                    <p style="margin: 0; font-size: 14px;">{day.get('high', '未知')}° / {day.get('low', '未知')}°</p>
                </div>
                """
            
            html += """
                </div>
            </div>
        """
        
        html += """
        </div>
        """
        
        return html
        
    except Exception as e:
        return f"<p style='color: red;'>天气数据处理失败: {str(e)}</p>"


def format_destination_info(destination_data: Dict[str, Any]) -> str:
    """
    Format destination information for display.
    
    Args:
        destination_data: Destination information data
        
    Returns:
        Formatted HTML string
    """
    try:
        name = destination_data.get("name", "未知目的地")
        description = destination_data.get("description", "暂无描述")
        attractions = destination_data.get("attractions", [])
        best_time = destination_data.get("best_time", "全年")
        transportation = destination_data.get("transportation", "")
        accommodation = destination_data.get("accommodation", [])
        
        html = f"""
        <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; background: #f8f9fa; padding: 20px; border-radius: 15px; border: 1px solid #e9ecef;">
            <h2 style="color: #2c3e50; margin: 0 0 20px 0; text-align: center;">🏞️ {name}</h2>
            
            <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #34495e; margin: 0 0 10px 0;">📍 目的地介绍</h4>
                <p style="color: #555; line-height: 1.6; margin: 0;">{description}</p>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #34495e; margin: 0 0 10px 0;">🌸 最佳旅游时间</h4>
                <p style="color: #555; margin: 0;">{best_time}</p>
            </div>
        """
        
        if transportation:
            html += f"""
            <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #34495e; margin: 0 0 10px 0;">🚗 交通信息</h4>
                <p style="color: #555; margin: 0;">{transportation}</p>
            </div>
            """
        
        if attractions:
            html += """
            <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: #34495e; margin: 0 0 10px 0;">🎯 主要景点</h4>
                <ul style="margin: 0; padding-left: 20px; color: #555;">
            """
            
            for attraction in attractions:
                html += f'<li style="margin-bottom: 5px;">{attraction}</li>'
            
            html += """
                </ul>
            </div>
            """
        
        if accommodation:
            html += """
            <div style="background: white; padding: 15px; border-radius: 10px;">
                <h4 style="color: #34495e; margin: 0 0 10px 0;">🏨 住宿推荐</h4>
                <ul style="margin: 0; padding-left: 20px; color: #555;">
            """
            
            for hotel in accommodation:
                html += f'<li style="margin-bottom: 5px;">{hotel}</li>'
            
            html += """
                </ul>
            </div>
            """
        
        html += """
        </div>
        """
        
        return html
        
    except Exception as e:
        return f"<p style='color: red;'>目的地信息格式化失败: {str(e)}</p>"


def create_travel_summary(travel_plan: Dict[str, Any]) -> str:
    """
    Create a travel summary from travel plan data.
    
    Args:
        travel_plan: Travel plan data
        
    Returns:
        Formatted summary HTML
    """
    try:
        destination = travel_plan.get("destination", "未知")
        duration = travel_plan.get("duration", "未知")
        total_cost = travel_plan.get("estimated_cost", "未估算")
        highlights = travel_plan.get("highlights", [])
        
        html = f"""
        <div style="font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; text-align: center; font-size: 24px;">📋 旅行计划摘要</h3>
            
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                <p style="margin: 5px 0; font-size: 16px;"><strong>目的地:</strong> {destination}</p>
                <p style="margin: 5px 0; font-size: 16px;"><strong>时长:</strong> {duration}</p>
                <p style="margin: 5px 0; font-size: 16px;"><strong>预估费用:</strong> {total_cost}</p>
            </div>
            
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                <h4 style="margin: 0 0 10px 0;">🌟 行程亮点</h4>
                <ul style="margin: 0; padding-left: 20px;">
        """
        
        for highlight in highlights:
            html += f'<li style="margin-bottom: 5px;">{highlight}</li>'
        
        html += """
                </ul>
            </div>
        </div>
        """
        
        return html
        
    except Exception as e:
        return f"<p style='color: red;'>旅行摘要生成失败: {str(e)}</p>"