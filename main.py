"""
AKShare Financial Report API
为 n8n 工作流提供 A股/港股 财报数据
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal
import akshare as ak
import pandas as pd
import datetime
import math

app = FastAPI(
    title="AKShare Financial API",
    description="A股/港股财报数据 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompanyRequest(BaseModel):
    company: str
    market: Optional[Literal["A", "HK"]] = None


class FinancialResponse(BaseModel):
    success: bool
    data: dict
    message: str = ""


def _search_stock_em(keyword: str, market_filter: str = None) -> dict:
    """
    使用东方财富搜索 API 搜索股票（统一搜索，速度快）

    market_filter:
        None  - 不限市场
        "A"   - 仅 A 股（沪A + 深A）
        "HK"  - 仅港股
    """
    import requests as _requests
    try:
        url = "https://searchapi.eastmoney.com/api/suggest/get"
        params = {
            "input": keyword,
            "type": 14,
            "token": "D43BF722C8E33BDC906FB84D85E326E8",
            "count": 10,
        }
        r = _requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = data.get("QuotationCodeTable", {}).get("Data", [])
        if not items:
            return {"found": False}

        # MktNum: "0"=深A(SZ), "1"=沪A(SH), "116"=港股(HK)
        # 注意: API 返回的 MktNum 是字符串类型
        MKT_A = {"0", "1"}      # 深A, 沪A
        MKT_HK = {"116"}        # 港股

        for item in items:
            mkt = str(item.get("MktNum", ""))
            code = item.get("Code", "")
            name = item.get("Name", "")

            if market_filter == "A" and mkt not in MKT_A:
                continue
            if market_filter == "HK" and mkt not in MKT_HK:
                continue
            if market_filter is None and mkt not in (MKT_A | MKT_HK):
                continue

            if mkt in MKT_A:
                # A 股: 构造 SH/SZ 前缀的 symbol
                prefix = "SH" if mkt == "1" else "SZ"
                return {
                    "found": True,
                    "code": code,
                    "name": name,
                    "symbol": f"{prefix}{code}",
                    "market": "A"
                }
            elif mkt in MKT_HK:
                return {
                    "found": True,
                    "code": code,
                    "name": name,
                    "symbol": code,
                    "market": "HK"
                }

        return {"found": False}
    except Exception as e:
        return {"found": False, "error": str(e)}


def search_a_stock(keyword: str) -> dict:
    """搜索 A 股股票代码"""
    return _search_stock_em(keyword, market_filter="A")


def search_hk_stock(keyword: str) -> dict:
    """搜索港股股票代码"""
    return _search_stock_em(keyword, market_filter="HK")


def format_number_readable(value):
    """将数字格式化为易读形式（亿/万）"""
    if value is None or value == "" or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        num = float(value)
        if abs(num) >= 100000000:  # 亿
            return f"{num/100000000:.2f}亿"
        elif abs(num) >= 10000:  # 万
            return f"{num/10000:.2f}万"
        else:
            return round(num, 2)
    except:
        return value


# 中文字段映射
FIELD_NAME_MAPPING = {
    # 基本信息
    'SECUCODE': '证券代码',
    'SECURITY_NAME_ABBR': '股票简称',
    'REPORT_DATE': '报告期',
    
    # 资产负债表
    'TOTAL_ASSETS': '总资产',
    'TOTAL_LIABILITIES': '总负债',
    'TOTAL_EQUITY': '股东权益',
    'MONETARYFUNDS': '货币资金',
    'ACCOUNTS_RECE': '应收账款',
    'INVENTORY': '存货',
    'FIXED_ASSET': '固定资产',
    'GOODWILL': '商誉',
    'INTANGIBLE_ASSET': '无形资产',
    'SHORT_LOAN': '短期借款',
    'LONG_LOAN': '长期借款',
    'BOND_PAYABLE': '应付债券',
    
    # 利润表
    'TOTAL_OPERATE_INCOME': '营业总收入',
    'OPERATE_INCOME': '营业收入',
    'OPERATE_COST': '营业成本',
    'SALE_EXPENSE': '销售费用',
    'MANAGE_EXPENSE': '管理费用',
    'FINANCE_EXPENSE': '财务费用',
    'RESEARCH_EXPENSE': '研发费用',
    'OPERATE_PROFIT': '营业利润',
    'TOTAL_PROFIT': '利润总额',
    'INCOME_TAX': '所得税',
    'NETPROFIT': '净利润',
    'PARENT_NETPROFIT': '归母净利润',
    'BASIC_EPS': '基本每股收益',
    'DILUTED_EPS': '稀释每股收益',
    
    # 现金流量表
    'SALES_SERVICES': '销售商品收到现金',
    'TOTAL_OPERATE_INFLOW': '经营活动现金流入',
    'TOTAL_OPERATE_OUTFLOW': '经营活动现金流出',
    'NETCASH_OPERATE': '经营活动现金流量净额',
    'NETCASH_INVEST': '投资活动现金流量净额',
    'NETCASH_FINANCE': '筹资活动现金流量净额',
    'CCE_ADD': '现金净增加额',
}


def format_for_ai_analysis(df: pd.DataFrame) -> list:
    """
    将DataFrame格式化为AI友好的中文数据
    - 转换字段名为中文
    - 格式化数字为易读形式
    - 添加计算指标
    """
    if df is None or df.empty:
        return []
    
    result = []
    for idx, row in df.iterrows():
        formatted_row = {}
        
        # 基本信息（保持原样）
        for field in ['SECUCODE', 'SECURITY_NAME_ABBR', 'REPORT_DATE']:
            if field in row:
                cn_name = FIELD_NAME_MAPPING.get(field, field)
                value = row[field]
                if field == 'REPORT_DATE':
                    # 转换为字符串，只保留日期部分
                    value = str(value).split()[0] if pd.notna(value) else None
                formatted_row[cn_name] = value
        
        # 财务数字（格式化）
        for field, cn_name in FIELD_NAME_MAPPING.items():
            if field in row and field not in ['SECUCODE', 'SECURITY_NAME_ABBR', 'REPORT_DATE']:
                value = row[field]
                formatted_row[cn_name] = format_number_readable(value)
        
        # 计算衍生指标
        if '营业收入' in formatted_row and '营业成本' in formatted_row:
            try:
                revenue = float(row.get('OPERATE_INCOME', 0))
                cost = float(row.get('OPERATE_COST', 0))
                if revenue > 0:
                    formatted_row['毛利率'] = f"{(revenue - cost) / revenue * 100:.2f}%"
            except:
                pass
        
        if '归母净利润' in formatted_row and '营业收入' in formatted_row:
            try:
                profit = float(row.get('PARENT_NETPROFIT', 0))
                revenue = float(row.get('OPERATE_INCOME', 0))
                if revenue > 0:
                    formatted_row['净利率'] = f"{profit / revenue * 100:.2f}%"
            except:
                pass
        
        if '总负债' in formatted_row and '总资产' in formatted_row:
            try:
                liab = float(row.get('TOTAL_LIABILITIES', 0))
                assets = float(row.get('TOTAL_ASSETS', 0))
                if assets > 0:
                    formatted_row['资产负债率'] = f"{liab / assets * 100:.2f}%"
            except:
                pass
        
        result.append(formatted_row)
    
    return result


def safe_to_dict(df: pd.DataFrame, max_rows: int = None) -> list:
    """安全地将 DataFrame 转为 dict 列表，处理 NaN/NaT/Inf 等 JSON 不兼容值"""
    if df is None or df.empty:
        return []
    # 如果指定了 max_rows 则限制行数，否则返回所有行
    subset = df.head(max_rows).copy() if max_rows else df.copy()
    # 转换 Timestamp 类型为字符串
    for col in subset.columns:
        if pd.api.types.is_datetime64_any_dtype(subset[col]):
            subset[col] = subset[col].astype(str).replace("NaT", None)
    # 转成 records
    records = subset.to_dict(orient='records')
    # 清理每条记录中的 NaN / Inf / -Inf
    cleaned = []
    for record in records:
        clean_record = {}
        for k, v in record.items():
            if v is None:
                clean_record[k] = None
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_record[k] = None
            elif isinstance(v, pd.Timestamp):
                clean_record[k] = str(v) if pd.notna(v) else None
            else:
                clean_record[k] = v
        cleaned.append(clean_record)
    return cleaned


# A股核心财务字段（精简，避免返回 300+ 列导致超时/过大）
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
    """只保留存在的列"""
    existing = [k for k in keys if k in df.columns]
    return df[existing] if existing else df


def filter_annual_and_latest(df: pd.DataFrame, annual_years: int = 3) -> pd.DataFrame:
    """
    只保留最新季报 + 最近N年年报
    
    Args:
        df: 包含日期列的 DataFrame (REPORT_DATE 或 报告期)
        annual_years: 保留最近几年的年报，默认3年
    
    Returns:
        过滤后的 DataFrame（最新季报 + 最近N年年报）
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


def get_a_stock_financial(symbol: str) -> dict:
    """获取 A 股财报数据
    symbol 格式: SH600519 / SZ000001
    """
    result = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": [],
        "financial_indicator": []
    }

    try:
        # 资产负债表 - 按报告期
        df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            df = filter_columns(df, A_BALANCE_KEYS)
            df = filter_annual_and_latest(df, annual_years=3)  # 最新季报 + 最近3年年报
            result["balance_sheet"] = format_for_ai_analysis(df)  # 使用AI友好格式
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        # 利润表 - 按报告期
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            df = filter_columns(df, A_PROFIT_KEYS)
            df = filter_annual_and_latest(df, annual_years=3)  # 最新季报 + 最近3年年报
            result["income_statement"] = format_for_ai_analysis(df)  # 使用AI友好格式
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        # 现金流量表 - 按报告期
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            df = filter_columns(df, A_CASHFLOW_KEYS)
            df = filter_annual_and_latest(df, annual_years=3)  # 最新季报 + 最近3年年报
            result["cash_flow"] = format_for_ai_analysis(df)  # 使用AI友好格式
    except Exception as e:
        result["cash_flow_error"] = str(e)

    try:
        # 财务指标（新浪）- 需要纯数字代码 + start_year
        code = symbol[2:] if symbol.startswith(('SH', 'SZ')) else symbol
        current_year = str(datetime.datetime.now().year - 3)
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year=current_year)
        if df is not None and not df.empty:
            df = filter_annual_and_latest(df, annual_years=3)  # 最新季报 + 最近3年年报
            result["financial_indicator"] = safe_to_dict(df)
    except Exception as e:
        result["financial_indicator_error"] = str(e)

    return result


def get_hk_stock_financial(code: str) -> dict:
    """获取港股财报数据
    code 格式: 纯数字如 00700
    AKShare 接口: stock_financial_hk_report_em(stock, symbol, indicator)
    """
    result = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": []
    }

    try:
        # 港股资产负债表（年度）
        df = ak.stock_financial_hk_report_em(stock=code, symbol="资产负债表", indicator="年度")
        if df is not None and not df.empty:
            df = filter_annual_and_latest(df, annual_years=3)  # 最近3年年报
            result["balance_sheet"] = safe_to_dict(df)  # 港股保留原格式
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        # 港股利润表（年度）
        df = ak.stock_financial_hk_report_em(stock=code, symbol="利润表", indicator="年度")
        if df is not None and not df.empty:
            df = filter_annual_and_latest(df, annual_years=3)  # 最近3年年报
            result["income_statement"] = safe_to_dict(df)  # 港股保留原格式
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        # 港股现金流量表（年度）
        df = ak.stock_financial_hk_report_em(stock=code, symbol="现金流量表", indicator="年度")
        if df is not None and not df.empty:
            df = filter_annual_and_latest(df, annual_years=3)  # 最近3年年报
            result["cash_flow"] = safe_to_dict(df)  # 港股保留原格式
    except Exception as e:
        result["cash_flow_error"] = str(e)

    return result


@app.get("/")
async def root():
    return {"status": "ok", "message": "AKShare Financial API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}



@app.post("/api/financial-report")
async def get_financial_report(request: CompanyRequest):
    """
    获取公司财报数据

    - company: 公司名称（如：海螺水泥、腾讯控股）
    - market: 可选，指定市场 A (A股) 或 HK (港股)，不指定则自动搜索
    """
    try:
        company = request.company.strip()
        market = request.market

        if not company:
            raise HTTPException(status_code=400, detail="公司名称不能为空")

        stock_info = None

        # 根据指定市场或自动搜索
        if market == "A":
            stock_info = search_a_stock(company)
        elif market == "HK":
            stock_info = search_hk_stock(company)
        else:
            # 先搜 A 股，再搜港股
            stock_info = search_a_stock(company)
            if not stock_info.get("found"):
                stock_info = search_hk_stock(company)

        if not stock_info.get("found"):
            return {
                "success": False,
                "data": {
                    "stock_found": False,
                    "company": company
                },
                "message": f"未找到「{company}」的股票信息，请检查公司名称是否正确"
            }

        # 获取财报数据
        if stock_info["market"] == "A":
            financial_data = get_a_stock_financial(stock_info["symbol"])
        else:
            financial_data = get_hk_stock_financial(stock_info["code"])

        return {
            "success": True,
            "data": {
                "stock_found": True,
                "stock_info": stock_info,
                "financial": financial_data
            },
            "message": "获取成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "data": {"error": str(e)},
            "message": f"服务器内部错误: {str(e)}"
        }


@app.get("/api/search")
async def search_stock(keyword: str, market: Optional[str] = None):
    """搜索股票"""
    if market == "A":
        return search_a_stock(keyword)
    elif market == "HK":
        return search_hk_stock(keyword)
    else:
        result = search_a_stock(keyword)
        if not result.get("found"):
            result = search_hk_stock(keyword)
        return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
