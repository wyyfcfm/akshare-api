"""
测试前端功能的简单脚本
"""
import subprocess
import time
import webbrowser
import sys

def test_frontend():
    print("🚀 启动 AKShare 财报数据可视化平台...")
    print("-" * 50)
    
    # 启动服务器
    print("📡 正在启动 FastAPI 服务器...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    time.sleep(3)
    
    # 检查服务器是否启动成功
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器启动成功!")
            print()
            print("📱 访问地址:")
            print("   本地: http://localhost:8000")
            print()
            print("🎯 功能说明:")
            print("   1. 接口测试 - 查询 A股/港股财报数据")
            print("   2. 思维导图 - 查看投资学习思维导图")
            print("   3. API文档 - 查看接口调用说明")
            print()
            print("按 Ctrl+C 停止服务器")
            print("-" * 50)
            
            # 自动打开浏览器
            time.sleep(1)
            webbrowser.open("http://localhost:8000")
            
            # 保持运行
            process.wait()
        else:
            print("❌ 服务器启动失败!")
            process.terminate()
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保:")
        print("  1. 已安装所有依赖: pip install -r requirements.txt")
        print("  2. 端口 8000 未被占用")
        process.terminate()

if __name__ == "__main__":
    try:
        test_frontend()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
