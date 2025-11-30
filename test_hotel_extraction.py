#!/usr/bin/env python3
"""Test hotel extraction functionality in detail."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.helpers import extract_hotels_from_itinerary

def test_detailed_extraction():
    """Test detailed hotel extraction patterns."""
    print("=== 详细酒店提取测试 ===\n")
    
    test_text = """
    北京5日游行程规划：
    
    第一天：
    - 抵达北京，入住北京饭店
    - 游览天安门广场
    
    第二天：
    - 参观故宫博物院
    - 晚上入住王府井希尔顿酒店
    
    第三天：
    - 登长城
    - 推荐酒店：北京香格里拉大酒店
    
    第四天：
    - 游览颐和园
    - 住宿：北京四季酒店
    
    第五天：
    - 购物，返回
    """
    
    print("测试文本:")
    print(test_text)
    print("\n" + "="*50)
    
    hotels = extract_hotels_from_itinerary(test_text)
    
    print(f"提取到的酒店 ({len(hotels)}个):")
    for i, hotel in enumerate(hotels, 1):
        print(f"{i}. {hotel}")
    
    # 检查是否包含预期的酒店
    expected_hotels = ["北京饭店", "王府井希尔顿酒店", "北京香格里拉大酒店", "北京四季酒店"]
    
    print(f"\n预期酒店: {expected_hotels}")
    print(f"实际提取: {hotels}")
    
    # 检查每个预期酒店
    for expected in expected_hotels:
        found = any(expected in hotel for hotel in hotels)
        status = "✅" if found else "❌"
        print(f"{status} {expected}: {'找到' if found else '未找到'}")
    
    return hotels

def test_various_patterns():
    """Test various hotel description patterns."""
    print("\n\n=== 测试不同酒店描述模式 ===\n")
    
    test_cases = [
        ("入住北京饭店", ["入住北京饭店"]),
        ("住宿：上海浦东香格里拉酒店", ["住宿：上海浦东香格里拉酒店"]),
        ("下榻王府井希尔顿酒店", ["下榻王府井希尔顿酒店"]),
        ("酒店：北京四季酒店", ["酒店：北京四季酒店"]),
        ("推荐酒店：深圳威尼斯酒店", ["推荐酒店：深圳威尼斯酒店"]),
        ("- 晚上入住广州白天鹅宾馆", ["- 晚上入住广州白天鹅宾馆"]),
        ("• 预订杭州西湖国宾馆", ["• 预订杭州西湖国宾馆"]),
        ("位于成都世纪城假日酒店", ["位于成都世纪城假日酒店"]),
        ("在三亚亚特兰蒂斯酒店", ["在三亚亚特兰蒂斯酒店"]),
        ("预约厦门康莱德酒店", ["预约厦门康莱德酒店"]),
    ]
    
    for test_text, expected in test_cases:
        hotels = extract_hotels_from_itinerary(test_text)
        print(f"文本: {test_text}")
        print(f"提取: {hotels}")
        print(f"预期: {expected}")
        
        if hotels:
            found = any(exp in hotels[0] for exp in expected)
            status = "✅" if found else "❌"
            print(f"{status} 匹配成功" if found else f"{status} 匹配失败")
        else:
            print("❌ 未提取到任何酒店")
        print("-" * 40)

if __name__ == "__main__":
    try:
        test_detailed_extraction()
        test_various_patterns()
        print("\n🎉 详细测试完成!")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)