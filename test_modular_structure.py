"""
Module validation test script for the travel assistant application.
Tests all modules and their imports to ensure the modular structure works correctly.
"""

import sys
import os
from pathlib import Path

def test_module_imports():
    """Test that all modules can be imported correctly."""
    print("🔍 正在测试模块化结构...")
    
    # Add src to path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    tests = [
        ("配置模块", "from config.config import APP_TITLE, API_KEY"),
        ("API客户端", "from api.openai_client import OpenAIClient, get_client"),
        ("工具函数", "from utils.helpers import clean_response, validate_inputs, safe_json_parse"),
        ("核心功能", "from core.travel_functions import generate_destination_recommendation, generate_itinerary_plan, generate_checklist"),
        ("数据处理", "from data.processors import save_checklist_data, load_checklist_data"),
        ("UI组件", "from ui.components import create_header, create_app_theme, create_destination_section"),
        ("主应用", "from main import create_app, main"),
    ]
    
    results = []
    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}: 导入成功")
            results.append(True)
        except Exception as e:
            print(f"❌ {test_name}: 导入失败 - {e}")
            results.append(False)
    
    return all(results)

def test_function_calls():
    """Test that key functions can be called."""
    print("\n🔍 正在测试函数调用...")
    
    try:
        # Test configuration access
        from config.config import APP_TITLE, INTEREST_OPTIONS
        print(f"✅ 配置访问: {APP_TITLE}")
        print(f"✅ 兴趣选项: {len(INTEREST_OPTIONS)} 个选项")
        
        # Test utility functions
        from utils.helpers import validate_inputs, clean_response
        test_inputs = {
            'season': '春季',
            'health_status': '健康',
            'budget': '中等',
            'interests': '休闲',
            'mobility': '良好'
        }
        result = validate_inputs(test_inputs)
        print(f"✅ 输入验证: {result}")
        
        # Test data processors
        from data.processors import save_checklist_data, load_checklist_data
        test_data = {"test": "data"}
        result = save_checklist_data(test_data, "北京", "上海", "3天")
        print(f"✅ 数据保存: {result}")
        
        # Clean up test file
        import os
        if os.path.exists("test_checklist.json"):
            os.remove("test_checklist.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 函数调用测试失败: {e}")
        return False

def test_application_creation():
    """Test that the main application can be created."""
    print("\n🔍 正在测试应用创建...")
    
    try:
        from main import create_app
        app = create_app()
        print(f"✅ 应用创建成功: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 开始模块化结构验证测试\n")
    
    # Run tests
    import_success = test_module_imports()
    function_success = test_function_calls()
    app_success = test_application_creation()
    
    print(f"\n📊 测试结果总结:")
    print(f"模块导入: {'✅ 通过' if import_success else '❌ 失败'}")
    print(f"函数调用: {'✅ 通过' if function_success else '❌ 失败'}")
    print(f"应用创建: {'✅ 通过' if app_success else '❌ 失败'}")
    
    overall_success = import_success and function_success and app_success
    print(f"\n🎯 整体结果: {'✅ 模块化结构验证通过!' if overall_success else '❌ 模块化结构验证失败!'}")
    
    if overall_success:
        print("\n🎉 恭喜! 旅行助手应用已成功模块化!")
        print("📁 模块结构:")
        print("  ├── src/config/     - 配置和常量")
        print("  ├── src/api/        - API客户端")
        print("  ├── src/utils/      - 工具函数")
        print("  ├── src/core/       - 核心旅行功能")
        print("  ├── src/data/       - 数据处理")
        print("  ├── src/ui/         - UI组件")
        print("  └── src/main.py     - 主应用入口")
        print("\n🚀 使用方法:")
        print("  python travel_assistant_modular.py  # 启动应用")
        print("  # 或")
        print("  cd src && python main.py  # 从src目录启动")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)