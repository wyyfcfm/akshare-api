"""测试不同格式给AI分析的效果"""
import sys
sys.path.append('.')

from main import get_a_stock_financial, search_a_stock
from format_for_ai import format_for_ai_summary, format_for_ai_detailed
import json

# 1. 获取真实数据
print("=" * 80)
print("获取海螺水泥财报数据...")
print("=" * 80)

stock_info = search_a_stock("海螺水泥")
if not stock_info.get("found"):
    print("未找到股票")
    exit(1)

financial_data = get_a_stock_financial(stock_info["symbol"])

print(f"\n✅ 成功获取 {stock_info['name']} 的财报数据\n")

# 2. 方案对比
print("=" * 80)
print("方案1: 直接原始JSON数据（不推荐）")
print("=" * 80)

raw_json = json.dumps(financial_data, ensure_ascii=False, indent=2)
print(f"数据大小: {len(raw_json)} 字符")
print(f"预估Token: ~{len(raw_json) // 4} tokens\n")
print("数据示例（仅显示前500字符）:")
print(raw_json[:500])
print("...(省略)")

print("\n" + "=" * 80)
print("方案2: AI友好的摘要格式（推荐⭐⭐⭐⭐⭐）")
print("=" * 80)

summary = format_for_ai_summary(stock_info, financial_data)
print(f"数据大小: {len(summary)} 字符")
print(f"预估Token: ~{len(summary) // 4} tokens\n")
print(summary)

print("\n" + "=" * 80)
print("方案3: AI友好的详细格式（深度分析时使用）")
print("=" * 80)

detailed = format_for_ai_detailed(financial_data, periods=3)
print(f"数据大小: {len(detailed)} 字符")
print(f"预估Token: ~{len(detailed) // 4} tokens\n")
print(detailed)

print("\n" + "=" * 80)
print("📊 效果对比总结")
print("=" * 80)

print(f"""
| 方案 | 字符数 | 预估Token | AI理解度 | 适用场景 |
|------|--------|-----------|---------|----------|
| 原始JSON | {len(raw_json)} | ~{len(raw_json)//4} | ⭐⭐ | 程序化处理 |
| 摘要格式 | {len(summary)} | ~{len(summary)//4} | ⭐⭐⭐⭐⭐ | 快速判断 |
| 详细格式 | {len(detailed)} | ~{len(detailed)//4} | ⭐⭐⭐⭐ | 深度分析 |

Token节省: {(1 - (len(summary) + len(detailed)) / len(raw_json)) * 100:.1f}%

推荐做法:
1. 先给AI看摘要格式，让它快速理解公司情况
2. 如果需要深入分析，再提供详细格式
3. 只在AI需要精确计算时才提供原始JSON
""")
