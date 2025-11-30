#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 测试清单生成功能
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from travel_assistant_improved import generate_checklist, format_checklist_output

    print("测试清单生成功能...")

    # 测试简单的清单生成
    destination = "北京"
    duration = "3天2夜"
    special_needs = "常规旅行"

    print(f"目的地: {destination}")
    print(f"时长: {duration}")
    print(f"特殊需求: {special_needs}")
    print("\n正在生成清单...")

    result = generate_checklist(destination, duration, special_needs)

    print(f"\n生成结果类型: {type(result)}")
    print(f"结果长度: {len(result)} 字符")
    print("\n前200个字符:")
    print(result[:200])

    # 检查是否包含HTML标签
    if "<script>" in result and "</script>" in result:
        print("\n✅ 包含JavaScript代码")
    else:
        print("\n❌ 缺少JavaScript代码")

    if "checkbox" in result.lower():
        print("✅ 包含checkbox元素")
    else:
        print("❌ 缺少checkbox元素")

    if "progress" in result.lower():
        print("✅ 包含进度条相关代码")
    else:
        print("❌ 缺少进度条代码")

    print("\n测试完成!")

except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"执行错误: {e}")
    import traceback
    traceback.print_exc()