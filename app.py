"""
Main entry point for the modular travel assistant application.
This script imports and runs the application from the src package.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    # Import and run the main application
    from main import main
    
    print("🚀 启动旅行助手应用...")
    main()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有模块文件都存在且路径正确")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 应用启动失败: {e}")
    sys.exit(1)