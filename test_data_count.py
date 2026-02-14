"""快速测试各个报表的数据条数"""
import requests
import json

# 测试 API
url = "http://localhost:8000/api/financial-report"
data = {"company": "海螺水泥"}

print("=" * 80)
print("测试各报表数据条数（应该都是：最新季报 + 最近3年年报）")
print("=" * 80)

try:
    response = requests.post(url, json=data, timeout=30)
    result = response.json()
    
    if result.get("success"):
        financial = result["data"]["financial"]
        
        print(f"\n✅ API 调用成功")
        print(f"\n📊 数据条数统计:")
        
        # 检查每个报表的数据条数
        reports = [
            ("资产负债表", "balance_sheet"),
            ("利润表", "income_statement"),
            ("现金流量表", "cash_flow"),
            ("财务指标", "financial_indicator")
        ]
        
        all_consistent = True
        for name, key in reports:
            if key in financial:
                data_list = financial[key]
                count = len(data_list) if isinstance(data_list, list) else 0
                print(f"  {name:12s}: {count} 条数据", end="")
                
                # 显示报告期
                if count > 0 and isinstance(data_list, list):
                    dates = []
                    for item in data_list:
                        # 尝试不同的日期字段名
                        date = item.get('报告期') or item.get('日期') or item.get('REPORT_DATE') or '未知'
                        dates.append(str(date).split()[0])  # 只取日期部分
                    print(f"  [{', '.join(dates)}]")
                    
                    # 检查是否符合预期（3或4条）
                    if count not in [3, 4]:
                        all_consistent = False
                        print(f"    ⚠️  预期3-4条数据")
                else:
                    print()
        
        if all_consistent:
            print(f"\n✅ 所有报表数据格式一致！")
        else:
            print(f"\n⚠️  部分报表数据条数异常")
            
    else:
        print(f"❌ API 调用失败: {result.get('message')}")
        
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到 API 服务器，请确保服务已启动 (uvicorn main:app)")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
