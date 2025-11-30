#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 简单测试清单生成函数
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # 导入函数
    from travel_assistant_improved import generate_checklist

    print("开始测试清单生成功能...")

    # 测试参数
    destination = "北京"
    duration = "3天2夜"
    special_needs = "常规旅行"

    print(f"目的地: {destination}")
    print(f"时长: {duration}")
    print(f"特殊需求: {special_needs}")

    # 调用函数
    result = generate_checklist(destination, duration, special_needs)

    print(f"生成成功！结果长度: {len(result)}")
    print("前100个字符:")
    print(result[:100])

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()