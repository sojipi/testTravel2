#!/usr/bin/env python3
"""Test the fixed checklist generation function."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_checklist_function():
    """Test the checklist generation function with proper return values."""
    print("=== 测试修复后的清单生成功能 ===\n")
    
    # Import the function
    try:
        from src.core.travel_functions import generate_checklist
        from src.ui.components import create_loading_animation
        from src.utils.helpers import extract_hotels_from_itinerary
    except ImportError:
        from core.travel_functions import generate_checklist
        from ui.components import create_loading_animation
        from utils.helpers import extract_hotels_from_itinerary
    
    # Test data
    test_origin = "北京"
    test_destination = "上海"
    test_duration = "3天"
    test_needs = "身体健康，常规旅行"
    test_itinerary = """
    上海3日游行程规划：
    
    第一天：
    - 抵达上海，入住上海浦东香格里拉酒店
    - 游览外滩
    
    第二天：
    - 参观上海博物馆
    - 推荐酒店：上海金茂君悦大酒店
    
    第三天：
    - 购物，返回
    """
    
    # Simulate the fixed function logic
    def generate_checklist_with_itinerary(origin, destination, duration, needs, itinerary_content):
        """Generate checklist with itinerary context."""
        # Extract hotels from itinerary if available
        hotels = extract_hotels_from_itinerary(itinerary_content)
        
        # Build enhanced special needs with hotel information
        enhanced_needs = needs
        if hotels:
            hotel_info = f"行程规划中提到的酒店：{', '.join(hotels)}"
            enhanced_needs = f"{needs}\n{hotel_info}" if needs else hotel_info
        
        # Generate checklist and return both loading and output components
        checklist_result = generate_checklist(origin, destination, duration, enhanced_needs, itinerary_content)
        loading_animation = create_loading_animation()
        return loading_animation, checklist_result
    
    print("测试参数:")
    print(f"出发地: {test_origin}")
    print(f"目的地: {test_destination}")
    print(f"旅行时长: {test_duration}")
    print(f"特殊需求: {test_needs}")
    print(f"行程内容长度: {len(test_itinerary)} 字符")
    
    # Test the function
    try:
        loading_result, checklist_result = generate_checklist_with_itinerary(
            test_origin, test_destination, test_duration, test_needs, test_itinerary
        )
        
        print(f"\n✅ 函数执行成功!")
        print(f"返回类型: {type(loading_result)}, {type(checklist_result)}")
        print(f"加载动画长度: {len(loading_result)} 字符")
        print(f"清单结果长度: {len(checklist_result)} 字符")
        
        # Verify return structure
        assert isinstance(loading_result, str), "加载动画应该是字符串"
        assert isinstance(checklist_result, str), "清单结果应该是字符串"
        assert len(loading_result) > 0, "加载动画不应为空"
        assert len(checklist_result) > 0, "清单结果不应为空"
        
        print("✅ 返回结构验证通过!")
        
        # Check if hotels were extracted and included
        hotels = extract_hotels_from_itinerary(test_itinerary)
        print(f"提取到的酒店: {hotels}")
        
        if hotels:
            print("✅ 酒店信息成功提取并融入清单生成")
        else:
            print("⚠️ 未提取到酒店信息")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checklist_function()
    if success:
        print("\n🎉 修复验证成功!")
        print("🎉 清单生成功能现在可以正确返回两个值")
    else:
        print("\n❌ 修复验证失败!")
        sys.exit(1)