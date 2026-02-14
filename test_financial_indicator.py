"""测试财务指标接口"""
import akshare as ak
import pandas as pd
import datetime

code = "600585"  # 海螺水泥

print("=" * 80)
print("测试财务指标接口 - stock_financial_analysis_indicator")
print("=" * 80)

try:
    # 与 main.py 保持一致：从3年前开始
    start_year = str(datetime.datetime.now().year - 3)
    print(f"查询起始年份: {start_year}")
    print("正在获取数据...\n")
    
    df = ak.stock_financial_analysis_indicator(symbol=code, start_year=start_year)
    
    print(f"✅ 成功获取数据")
    print(f"原始数据 - 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 只去除完全为NaN的列
    df_filtered = df.dropna(axis=1, how='all')
    
    print(f"过滤后数据 - 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    print(f"\n所有字段 ({len(df_filtered.columns)}个):")
    print(list(df_filtered.columns))
    
    print(f"\n数据预览（前5行）:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 30)
    print(df_filtered.head(5))
    
    print(f"\n数据时间范围:")
    if '截止日期' in df_filtered.columns:
        print(f"最早: {df_filtered['截止日期'].min()}")
        print(f"最新: {df_filtered['截止日期'].max()}")
    
    print(f"\n✅ 财务指标接口工作正常！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
