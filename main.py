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


def get_a_stock_financial(symbol: str) -> dict:
    """获取 A 股财报数据"""
    result = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": [],
        "financial_indicator": []
    }

    try:
        # 资产负债表
        df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            result["balance_sheet"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        # 利润表
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            result["income_statement"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        # 现金流量表
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            result["cash_flow"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["cash_flow_error"] = str(e)

    try:
        # 财务指标
        code = symbol[2:] if symbol.startswith(('SH', 'SZ')) else symbol
        df = ak.stock_financial_analysis_indicator(symbol=code)
        if df is not None and not df.empty:
            result["financial_indicator"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["financial_indicator_error"] = str(e)

    return result


def get_hk_stock_financial(code: str) -> dict:
    """获取港股财报数据"""
    result = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": []
    }

    try:
        df = ak.stock_hk_financial_report_em(stock=code, symbol="资产负债表")
        if df is not None and not df.empty:
            result["balance_sheet"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["balance_sheet_error"] = str(e)

    try:
        df = ak.stock_hk_financial_report_em(stock=code, symbol="利润表")
        if df is not None and not df.empty:
            result["income_statement"] = df.head(8).to_dict(orient='records')
    except Exception as e:
        result["income_statement_error"] = str(e)

    try:
        df = ak.stock_hk_financial_report_em(stock=code, symbol="现金流量表")
        if df is not None and not df.empty:
            result["cash_flow"] = df.head(8).to_dict(orient='records')
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
