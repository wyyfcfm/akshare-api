"""测试 AKShare 返回的完整数据结构"""
import akshare as ak
import pandas as pd

symbol = "SH600585"  # 海螺水泥
code = "600585"

print("=" * 80)
print("1. 资产负债表 - stock_balance_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
    print(f"行数: {len(df)}, 列数: {len(df.columns)}")
    print(f"\n所有列名:\n{list(df.columns)}")
    print(f"\n前2行数据:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 30)
    print(df.head(2).T)  # 转置显示更清晰
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("2. 利润表 - stock_profit_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
    print(f"行数: {len(df)}, 列数: {len(df.columns)}")
    print(f"\n所有列名:\n{list(df.columns)}")
    print(f"\n前2行数据:")
    print(df.head(2).T)
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("3. 现金流量表 - stock_cash_flow_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
    print(f"行数: {len(df)}, 列数: {len(df.columns)}")
    print(f"\n所有列名:\n{list(df.columns)}")
    print(f"\n前2行数据:")
    print(df.head(2).T)
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("4. 财务指标 - stock_financial_analysis_indicator")
print("=" * 80)
try:
    df = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")
    print(f"行数: {len(df)}, 列数: {len(df.columns)}")
    print(f"\n所有列名:\n{list(df.columns)}")
    print(f"\n前2行数据:")
    print(df.head(2).T)
except Exception as e:
    print(f"错误: {e}")
