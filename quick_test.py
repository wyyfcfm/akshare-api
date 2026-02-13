"""快速测试 - 添加超时控制"""
import akshare as ak
import signal
import sys

def timeout_handler(signum, frame):
    print("\n超时！程序被终止")
    sys.exit(1)

# 设置30秒超时
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)

try:
    symbol = "SH600585"  # 海螺水泥
    print(f"测试股票: {symbol}")
    
    print("\n1. 资产负债表...")
    df1 = ak.stock_balance_sheet_by_report_em(symbol=symbol)
    print(f"   ✓ 成功！行数: {len(df1)}, 列数: {len(df1.columns)}")
    print(f"   前3个列名: {list(df1.columns)[:3]}")
    
    print("\n2. 利润表...")
    df2 = ak.stock_profit_sheet_by_report_em(symbol=symbol)
    print(f"   ✓ 成功！行数: {len(df2)}, 列数: {len(df2.columns)}")
    print(f"   前3个列名: {list(df2.columns)[:3]}")
    
    print("\n3. 现金流量表...")
    df3 = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
    print(f"   ✓ 成功！行数: {len(df3)}, 列数: {len(df3.columns)}")
    print(f"   前3个列名: {list(df3.columns)[:3]}")
    
    print("\n4. 财务指标...")
    df4 = ak.stock_financial_analysis_indicator(symbol="600585", start_year="2023")
    print(f"   ✓ 成功！行数: {len(df4)}, 列数: {len(df4.columns)}")
    print(f"   前3个列名: {list(df4.columns)[:3]}")
    
    print("\n✅ 所有测试完成！")
    signal.alarm(0)  # 取消超时
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    signal.alarm(0)
    sys.exit(1)
