"""测试财务指标接口"""
import akshare as ak
import pandas as pd
import datetime

code = "600585"  # 海螺水泥

print("=" * 80)
print("测试财务指标接口 - stock_financial_analysis_indicator")
print("=" * 80)

def filter_annual_and_latest(df: pd.DataFrame, annual_years: int = 3) -> pd.DataFrame:
    """
    只保留最新季报 + 最近N年年报
    与 main.py 保持一致
    """
    if df is None or df.empty:
        return df
    
    # 尝试找到日期列
    date_column = None
    for col in ['REPORT_DATE', '报告期', '截止日期', '日期']:
        if col in df.columns:
            date_column = col
            break
    
    if date_column is None:
        return df
    
    try:
        # 确保日期列是 datetime 类型
        df[date_column] = pd.to_datetime(df[date_column])
        
        # 按日期降序排序
        df_sorted = df.sort_values(by=date_column, ascending=False).reset_index(drop=True)
        
        # 获取最新日期
        latest_date = df_sorted[date_column].iloc[0]
        
        # 判断最新数据是否是年报（12月31日）
        is_annual = latest_date.month == 12 and latest_date.day == 31
        
        result_rows = []
        
        # 1. 如果最新数据不是年报，加入最新季报
        if not is_annual:
            result_rows.append(df_sorted.iloc[0])
        
        # 2. 筛选所有年报（12月31日），取最近的N条
        annual_reports = df_sorted[
            (df_sorted[date_column].dt.month == 12) &
            (df_sorted[date_column].dt.day == 31)
        ]
        
        # 取最近的N年年报
        for idx, row in annual_reports.head(annual_years).iterrows():
            result_rows.append(row)
        
        if result_rows:
            filtered_df = pd.DataFrame(result_rows).reset_index(drop=True)
            return filtered_df
        else:
            return df_sorted.head(4)  # 降级方案：返回前4条
        
    except Exception as e:
        print(f"日期过滤失败: {e}")
        return df

try:
    # 与 main.py 保持一致：从3年前开始
    start_year = str(datetime.datetime.now().year - 3)
    print(f"查询起始年份: {start_year}")
    print("正在获取数据...\n")
    
    df = ak.stock_financial_analysis_indicator(symbol=code, start_year=start_year)
    
    print(f"✅ 成功获取原始数据")
    print(f"原始数据 - 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 应用过滤（与 main.py 保持一致）
    df_filtered = filter_annual_and_latest(df, annual_years=3)
    
    print(f"\n📊 过滤后数据（最新季报 + 最近3年年报）")
    print(f"过滤后数据 - 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    
    # 显示日期范围
    date_column = None
    for col in ['日期', '截止日期', 'REPORT_DATE', '报告期']:
        if col in df_filtered.columns:
            date_column = col
            break
    
    if date_column:
        print(f"\n保留的报告期:")
        for idx, row in df_filtered.iterrows():
            print(f"  - {row[date_column]}")
    
    # 只去除完全为NaN的列
    df_display = df_filtered.dropna(axis=1, how='all')
    
    print(f"\n所有字段 ({len(df_display.columns)}个):")
    print(list(df_display.columns))
    
    print(f"\n数据预览:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 30)
    print(df_display)
    
    print(f"\n✅ 财务指标接口工作正常！")
    print(f"✅ 数据格式与其他报表一致：最新季报 + 最近3年年报")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
