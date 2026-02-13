# AKShare Financial API

为 n8n 工作流提供 A股/港股 财报数据的 API 服务。

## 功能

- 支持 A 股和港股
- 自动搜索股票代码
- 获取资产负债表、利润表、现金流量表、财务指标

## API 接口

### POST /api/financial-report

获取公司财报数据。

**请求体：**
```json
{
  "company": "海螺水泥",
  "market": "A"  // 可选: "A" (A股), "HK" (港股), 不填则自动搜索
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "stock_found": true,
    "stock_info": {
      "code": "600585",
      "name": "海螺水泥",
      "symbol": "SH600585",
      "market": "A"
    },
    "financial": {
      "balance_sheet": [...],
      "income_statement": [...],
      "cash_flow": [...],
      "financial_indicator": [...]
    }
  },
  "message": "获取成功"
}
```

### GET /api/search?keyword=腾讯&market=HK

搜索股票代码。

## 部署到 Railway

1. Fork 或 Push 到 GitHub
2. 在 Railway 创建项目，连接 GitHub 仓库
3. 自动部署，获取公网 URL

## 本地运行

```bash
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8000/docs 查看 API 文档。
