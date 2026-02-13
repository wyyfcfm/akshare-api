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


def search_a_stock(keyword: str) -> dict:
    """搜索 A 股股票代码"""
    try:
        # 使用东方财富搜索
        df = ak.stock_info_a_code_name()
        # 精确匹配
        exact_match = df[df['name'] == keyword]
        if not exact_match.empty:
            row = exact_match.iloc[0]
            code = row['code']
            market = "SH" if code.startswith(('6', '9')) else "SZ"
            return {
                "found": True,
                "code": code,
                "name": row['name'],
                "symbol": f"{market}{code}",
                "market": "A"
            }
        # 模糊匹配
        fuzzy_match = df[df['name'].str.contains(keyword, na=False)]
        if not fuzzy_match.empty:
            row = fuzzy_match.iloc[0]
            code = row['code']
            market = "SH" if code.startswith(('6', '9')) else "SZ"
            return {
                "found": True,
                "code": code,
                "name": row['name'],
                "symbol": f"{market}{code}",
                "market": "A"
            }
        return {"found": False}
    except Exception as e:
        return {"found": False, "error": str(e)}


def search_hk_stock(keyword: str) -> dict:
    """搜索港股股票代码"""
    try:
        df = ak.stock_hk_spot_em()
        # 精确匹配
        exact_match = df[df['名称'] == keyword]
        if not exact_match.empty:
            row = exact_match.iloc[0]
            return {
                "found": True,
                "code": row['代码'],
                "name": row['名称'],
                "symbol": row['代码'],
                "market": "HK"
            }
        # 模糊匹配
        fuzzy_match = df[df['名称'].str.contains(keyword, na=False)]
        if not fuzzy_match.empty:
            row = fuzzy_match.iloc[0]
            return {
                "found": True,
                "code": row['代码'],
                "name": row['名称'],
                "symbol": row['代码'],
                "market": "HK"
            }
        return {"found": False}
    except Exception as e:
        return {"found": False, "error": str(e)}


def safe_to_dict(df: pd.DataFrame, max_rows: int = 4) -> list:
    """安全地将 DataFrame 转为 dict 列表，处理 NaN 和 NaT"""
    if df is None or df.empty:
        return []
    subset = df.head(max_rows).copy()
    # 将 NaN/NaT 替换为 None，确保 JSON 序列化不出错
    subset = subset.where(subset.notna(), None)
    # 转换 Timestamp 类型为字符串
    for col in subset.columns:
        if pd.api.types.is_datetime64_any_dtype(subset[col]):
            subset[col] = subset[col].astype(str).replace("NaT", None)
    return subset.to_dict(orient='records')


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
            result["balance_sheet"] = safe_to_dict(df)
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        # 利润表 - 按报告期
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            df = filter_columns(df, A_PROFIT_KEYS)
            result["income_statement"] = safe_to_dict(df)
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        # 现金流量表 - 按报告期
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            df = filter_columns(df, A_CASHFLOW_KEYS)
            result["cash_flow"] = safe_to_dict(df)
    except Exception as e:
        result["cash_flow_error"] = str(e)

    try:
        # 财务指标（新浪）- 需要纯数字代码 + start_year
        code = symbol[2:] if symbol.startswith(('SH', 'SZ')) else symbol
        current_year = str(datetime.datetime.now().year - 3)
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year=current_year)
        if df is not None and not df.empty:
            result["financial_indicator"] = safe_to_dict(df, max_rows=8)
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
            result["balance_sheet"] = safe_to_dict(df)
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        # 港股利润表（年度）
        df = ak.stock_financial_hk_report_em(stock=code, symbol="利润表", indicator="年度")
        if df is not None and not df.empty:
            result["income_statement"] = safe_to_dict(df)
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        # 港股现金流量表（年度）
        df = ak.stock_financial_hk_report_em(stock=code, symbol="现金流量表", indicator="年度")
        if df is not None and not df.empty:
            result["cash_flow"] = safe_to_dict(df)
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
