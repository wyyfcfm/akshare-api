"""测试 AKShare 返回的完整数据结构（使用与 main.py 相同的字段）"""
import akshare as ak
import pandas as pd

symbol = "SH600585"  # 海螺水泥
code = "600585"

# 与 main.py 保持一致的核心财务字段
A_BALANCE_KEYS = [
    "SECUCODE", "SECURITY_NAME_ABBR", "REPORT_DATE",
    "TOTAL_ASSETS", "TOTAL_LIABILITIES", "TOTAL_EQUITY",
    "MONETARYFUNDS", "ACCOUNTS_RECE", "INVENTORY",
    "FIXED_ASSET", "GOODWILL", "INTANGIBLE_ASSET",
    "SHORT_LOAN", "LONG_LOAN", "BOND_PAYABLE",
]
A_PROFIT_KEYS = [
    "SECUCODE", "SECURITY_NAME_ABBR", "REPORT_DATE",
    "TOTAL_OPERATE_INCOME", "OPERATE_INCOME", "OPERATE_COST",
    "SALE_EXPENSE", "MANAGE_EXPENSE", "FINANCE_EXPENSE",
    "RESEARCH_EXPENSE", "OPERATE_PROFIT", "TOTAL_PROFIT",
    "INCOME_TAX", "NETPROFIT", "PARENT_NETPROFIT",
    "BASIC_EPS", "DILUTED_EPS",
]
A_CASHFLOW_KEYS = [
    "SECUCODE", "SECURITY_NAME_ABBR", "REPORT_DATE",
    "SALES_SERVICES", "TOTAL_OPERATE_INFLOW", "TOTAL_OPERATE_OUTFLOW",
    "NETCASH_OPERATE", "NETCASH_INVEST", "NETCASH_FINANCE",
    "CCE_ADD",
]


def filter_columns(df: pd.DataFrame, keys: list) -> pd.DataFrame:
    """只保留存在的列（与 main.py 保持一致）"""
    existing = [k for k in keys if k in df.columns]
    return df[existing] if existing else df


def filter_recent_years(df: pd.DataFrame, years: int = 3) -> pd.DataFrame:
    """
    过滤最近N年的数据（包括最新一季度）
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
        
        # 获取当前年份
        import datetime
        current_year = datetime.datetime.now().year
        
        # 计算起始年份（往前推N年）
        start_year = current_year - years
        
        # 过滤：保留 >= start_year 的数据
        filtered_df = df[df[date_column].dt.year >= start_year].copy()
        
        return filtered_df
    except Exception as e:
        print(f"日期过滤失败: {e}")
        return df

print("=" * 80)
print("1. 资产负债表 - stock_balance_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
    print(f"原始数据 - 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 使用与 main.py 相同的字段过滤
    df_filtered = filter_columns(df, A_BALANCE_KEYS)
    # 只保留最近3年数据（与 main.py 保持一致）
    df_filtered = filter_recent_years(df_filtered, years=3)
    
    print(f"过滤后数据（最近3年）- 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    print(f"\n核心字段 ({len(df_filtered.columns)}个):\n{list(df_filtered.columns)}")
    print(f"\n最近3年数据（与API返回一致）:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 30)
    pd.set_option('display.max_rows', None)  # 显示所有行
    # 用"-"替换NaN，显示更清晰
    print(df_filtered.fillna("-").T)  # 转置显示更清晰
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("2. 利润表 - stock_profit_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
    print(f"原始数据 - 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 使用与 main.py 相同的字段过滤
    df_filtered = filter_columns(df, A_PROFIT_KEYS)
    # 只保留最近3年数据（与 main.py 保持一致）
    df_filtered = filter_recent_years(df_filtered, years=3)
    
    print(f"过滤后数据（最近3年）- 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    print(f"\n核心字段 ({len(df_filtered.columns)}个):\n{list(df_filtered.columns)}")
    print(f"\n最近3年数据（与API返回一致）:")
    # 用"-"替换NaN，显示更清晰
    print(df_filtered.fillna("-").T)
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("3. 现金流量表 - stock_cash_flow_sheet_by_report_em")
print("=" * 80)
try:
    df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
    print(f"原始数据 - 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 使用与 main.py 相同的字段过滤
    df_filtered = filter_columns(df, A_CASHFLOW_KEYS)
    # 只保留最近3年数据（与 main.py 保持一致）
    df_filtered = filter_recent_years(df_filtered, years=3)
    
    print(f"过滤后数据（最近3年）- 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    print(f"\n核心字段 ({len(df_filtered.columns)}个):\n{list(df_filtered.columns)}")
    print(f"\n最近3年数据（与API返回一致）:")
    # 用"-"替换NaN，显示更清晰
    print(df_filtered.fillna("-").T)
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 80)
print("4. 财务指标 - stock_financial_analysis_indicator")
print("=" * 80)
try:
    # 与 main.py 保持一致：从3年前开始
    import datetime
    start_year = str(datetime.datetime.now().year - 3)
    df = ak.stock_financial_analysis_indicator(symbol=code, start_year=start_year)
    print(f"原始数据（从{start_year}年起）- 行数: {len(df)}, 列数: {len(df.columns)}")
    
    # 财务指标返回所有字段（与 main.py 保持一致）
    # 只去除完全为NaN的列
    df_filtered = df.dropna(axis=1, how='all')
    
    print(f"过滤后数据 - 行数: {len(df_filtered)}, 列数: {len(df_filtered.columns)}")
    print(f"\n所有字段 ({len(df_filtered.columns)}个):\n{list(df_filtered.columns)}")
    print(f"\n最近3年数据（与API返回一致）:")
    # 用"-"替换NaN，显示更清晰
    print(df_filtered.fillna("-").T)
except Exception as e:
    print(f"错误: {e}")
