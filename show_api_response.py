"""展示API返回给工作流的完整JSON数据结构"""
import sys
sys.path.append('.')

from main import get_a_stock_financial, search_a_stock
import json

print("=" * 80)
print("API返回给工作流的完整JSON数据结构")
print("=" * 80)

# 模拟API调用
company = "海螺水泥"
print(f"\n请求：POST /api/financial-report")
print(f"Body: {{'company': '{company}'}}\n")

# 搜索股票
stock_info = search_a_stock(company)

# 获取财报数据
if stock_info.get("found"):
    financial_data = get_a_stock_financial(stock_info["symbol"])
    
    # 构建完整的API响应（与main.py第522-530行一致）
    response = {
        "success": True,
        "data": {
            "stock_found": True,
            "stock_info": stock_info,
            "financial": financial_data
        },
        "message": "获取成功"
    }
    
    print("=" * 80)
    print("响应：完整JSON数据")
    print("=" * 80)
    
    # 打印完整JSON（只展示结构，不展示所有数据）
    print(json.dumps({
        "success": response["success"],
        "message": response["message"],
        "data": {
            "stock_found": response["data"]["stock_found"],
            "stock_info": response["data"]["stock_info"],
            "financial": {
                "balance_sheet": f"[{len(response['data']['financial'].get('balance_sheet', []))}条数据]",
                "income_statement": f"[{len(response['data']['financial'].get('income_statement', []))}条数据]",
                "cash_flow": f"[{len(response['data']['financial'].get('cash_flow', []))}条数据]",
                "financial_indicator": f"[{len(response['data']['financial'].get('financial_indicator', []))}条数据]"
            }
        }
    }, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("详细数据展示")
    print("=" * 80)
    
    # 展示股票信息
    print("\n1️⃣ stock_info（股票基本信息）:")
    print(json.dumps(response["data"]["stock_info"], ensure_ascii=False, indent=2))
    
    # 展示资产负债表
    print("\n2️⃣ financial.balance_sheet（资产负债表）:")
    if response["data"]["financial"].get("balance_sheet"):
        print(f"数据条数: {len(response['data']['financial']['balance_sheet'])}")
        print("第一条数据示例:")
        print(json.dumps(response["data"]["financial"]["balance_sheet"][0], ensure_ascii=False, indent=2))
    
    # 展示利润表
    print("\n3️⃣ financial.income_statement（利润表）:")
    if response["data"]["financial"].get("income_statement"):
        print(f"数据条数: {len(response['data']['financial']['income_statement'])}")
        print("第一条数据示例:")
        print(json.dumps(response["data"]["financial"]["income_statement"][0], ensure_ascii=False, indent=2))
    
    # 展示现金流量表
    print("\n4️⃣ financial.cash_flow（现金流量表）:")
    if response["data"]["financial"].get("cash_flow"):
        print(f"数据条数: {len(response['data']['financial']['cash_flow'])}")
        print("第一条数据示例:")
        print(json.dumps(response["data"]["financial"]["cash_flow"][0], ensure_ascii=False, indent=2))
    
    # 计算数据大小
    response_json = json.dumps(response, ensure_ascii=False)
    json_size = len(response_json)
    estimated_tokens = json_size // 4
    
    print("\n" + "=" * 80)
    print("📊 数据统计")
    print("=" * 80)
    print(f"""
- JSON字符数: {json_size:,}
- 预估Token: ~{estimated_tokens:,}
- 资产负债表: {len(response['data']['financial'].get('balance_sheet', []))}条
- 利润表: {len(response['data']['financial'].get('income_statement', []))}条
- 现金流量表: {len(response['data']['financial'].get('cash_flow', []))}条
- 财务指标: {len(response['data']['financial'].get('financial_indicator', []))}条
    """)
    
    print("=" * 80)
    print("💡 n8n工作流使用方法")
    print("=" * 80)
    print("""
在n8n中使用：

1. HTTP Request节点调用：
   POST http://localhost:8000/api/financial-report
   Body: {"company": "海螺水泥"}

2. 访问数据：
   - 股票代码: {{$json.data.stock_info.code}}
   - 股票名称: {{$json.data.stock_info.name}}
   - 资产负债表: {{$json.data.financial.balance_sheet}}
   - 利润表: {{$json.data.financial.income_statement}}
   - 现金流量表: {{$json.data.financial.cash_flow}}

3. 给AI分析：
   直接传递: {{$json.data.financial}}
   
   所有数据都是中文字段 + 格式化数字，AI可以直接理解！
    """)

else:
    print(f"未找到股票: {company}")
