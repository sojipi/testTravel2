@echo off
echo 正在启动银发族智能旅行助手...
echo.
echo 加载环境变量...
for /f "tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" (
        if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
)
echo 环境变量加载完成
echo.
echo 请确保已安装所需依赖：
echo   pip install -r requirements.txt
echo.
echo 正在启动应用，请稍等...
echo 浏览器将自动打开 http://localhost:7860
echo.
python travel_assistant_improved.py
pause
