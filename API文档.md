# AKShare 财报 API 说明文档

## 📋 项目概述

本项目基于 AKShare 数据源，提供 A股和港股上市公司财报数据的 RESTful API 服务，用于集成到 n8n 工作流或其他自动化系统。

### 主要功能
- 🔍 智能股票搜索（支持公司名称、股票代码）
- 📊 获取完整财务报表数据
- 🌐 支持 A股 和 港股市场
- 🚀 自动数据清洗和格式化
- ⚡ 快速 API 响应

---

## 🔗 数据接口说明

### 1. 资产负债表 (Balance Sheet)

**接口函数**: `ak.stock_balance_sheet_by_report_em()`

**数据源**: 东方财富网

**官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html#id432

**更新频率**: 季度更新（每季度财报发布后）

#### 返回字段 (15个核心字段)

| 字段英文名 | 字段含义 | 单位 | 说明 |
|----------|---------|------|------|
| **SECUCODE** | 证券代码 | - | 格式：600585.SH |
| **SECURITY_NAME_ABBR** | 股票简称 | - | 例如：海螺水泥 |
| **REPORT_DATE** | 报告期 | 日期 | 格式：2025-09-30 |
| **TOTAL_ASSETS** | 总资产 | 元 | 企业拥有或控制的全部资产 |
| **TOTAL_LIABILITIES** | 总负债 | 元 | 企业承担的全部债务 |
| **TOTAL_EQUITY** | 股东权益合计 | 元 | 总资产 - 总负债 |
| **MONETARYFUNDS** | 货币资金 | 元 | 现金及银行存款 |
| **ACCOUNTS_RECE** | 应收账款 | 元 | 应该收但还没收到的款项 |
| **INVENTORY** | 存货 | 元 | 库存商品、原材料等 |
| **FIXED_ASSET** | 固定资产 | 元 | 房屋、机器设备等长期资产 |
| **GOODWILL** | 商誉 | 元 | 并购产生的溢价 |
| **INTANGIBLE_ASSET** | 无形资产 | 元 | 专利、商标、土地使用权等 |
| **SHORT_LOAN** | 短期借款 | 元 | 一年内需偿还的借款 |
| **LONG_LOAN** | 长期借款 | 元 | 一年以上需偿还的借款 |
| **BOND_PAYABLE** | 应付债券 | 元 | 发行的公司债券 |

#### 财务分析要点
- **资产负债率** = 总负债 / 总资产（评估财务风险）
- **流动比率** = 流动资产 / 流动负债（评估短期偿债能力）
- **货币资金充足度** = 货币资金 / 总资产（评估现金储备）

---

### 2. 利润表 (Income Statement)

**接口函数**: `ak.stock_profit_sheet_by_report_em()`

**数据源**: 东方财富网

**官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html#id436

**更新频率**: 季度更新

#### 返回字段 (17个核心字段)

| 字段英文名 | 字段含义 | 单位 | 说明 |
|----------|---------|------|------|
| **SECUCODE** | 证券代码 | - | 格式：600585.SH |
| **SECURITY_NAME_ABBR** | 股票简称 | - | 例如：海螺水泥 |
| **REPORT_DATE** | 报告期 | 日期 | 格式：2025-09-30 |
| **TOTAL_OPERATE_INCOME** | 营业总收入 | 元 | 企业主营业务和其他业务的总收入 |
| **OPERATE_INCOME** | 营业收入 | 元 | 主营业务收入 |
| **OPERATE_COST** | 营业成本 | 元 | 生产销售商品或服务的直接成本 |
| **SALE_EXPENSE** | 销售费用 | 元 | 广告、运输、销售人员工资等 |
| **MANAGE_EXPENSE** | 管理费用 | 元 | 管理部门发生的费用 |
| **FINANCE_EXPENSE** | 财务费用 | 元 | 利息支出等融资成本 |
| **RESEARCH_EXPENSE** | 研发费用 | 元 | 研发投入（部分公司披露）|
| **OPERATE_PROFIT** | 营业利润 | 元 | 营业收入 - 营业成本 - 各项费用 |
| **TOTAL_PROFIT** | 利润总额 | 元 | 营业利润 + 营业外收支 |
| **INCOME_TAX** | 所得税费用 | 元 | 应缴纳的企业所得税 |
| **NETPROFIT** | 净利润 | 元 | 利润总额 - 所得税 |
| **PARENT_NETPROFIT** | 归属母公司净利润 | 元 | 归属于母公司股东的净利润 |
| **BASIC_EPS** | 基本每股收益 | 元/股 | 净利润 / 总股本 |
| **DILUTED_EPS** | 稀释每股收益 | 元/股 | 考虑可转换证券的每股收益 |

#### 财务分析要点
- **毛利率** = (营业收入 - 营业成本) / 营业收入
- **净利率** = 净利润 / 营业收入
- **费用率** = (销售费用 + 管理费用 + 财务费用) / 营业收入
- **研发强度** = 研发费用 / 营业收入

---

### 3. 现金流量表 (Cash Flow Statement)

**接口函数**: `ak.stock_cash_flow_sheet_by_report_em()`

**数据源**: 东方财富网

**官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html#id440

**更新频率**: 季度更新

#### 返回字段 (10个核心字段)

| 字段英文名 | 字段含义 | 单位 | 说明 |
|----------|---------|------|------|
| **SECUCODE** | 证券代码 | - | 格式：600585.SH |
| **SECURITY_NAME_ABBR** | 股票简称 | - | 例如：海螺水泥 |
| **REPORT_DATE** | 报告期 | 日期 | 格式：2025-09-30 |
| **SALES_SERVICES** | 销售商品、提供劳务收到的现金 | 元 | 经营活动现金流入主要来源 |
| **TOTAL_OPERATE_INFLOW** | 经营活动现金流入小计 | 元 | 日常经营产生的现金流入 |
| **TOTAL_OPERATE_OUTFLOW** | 经营活动现金流出小计 | 元 | 日常经营产生的现金流出 |
| **NETCASH_OPERATE** | 经营活动产生的现金流量净额 | 元 | 流入 - 流出（核心指标）|
| **NETCASH_INVEST** | 投资活动产生的现金流量净额 | 元 | 投资收益或支出 |
| **NETCASH_FINANCE** | 筹资活动产生的现金流量净额 | 元 | 融资或分红产生的现金流 |
| **CCE_ADD** | 现金及现金等价物净增加额 | 元 | 期末现金 - 期初现金 |

#### 财务分析要点
- **经营现金流** > 0：企业经营产生现金流入
- **自由现金流** = 经营现金流 - 资本支出
- **现金流量比率** = 经营现金流 / 流动负债

---

### 4. 财务指标 (Financial Indicators)

**接口函数**: `ak.stock_financial_analysis_indicator()`

**数据源**: 新浪财经

**官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html#id448

**更新频率**: 季度更新

#### 返回字段 (60+ 综合指标)

包含但不限于：
- 盈利能力指标（ROE、ROA、毛利率等）
- 偿债能力指标（流动比率、速动比率等）
- 营运能力指标（存货周转率、应收账款周转率等）
- 成长能力指标（营收增长率、利润增长率等）
- 每股指标（每股收益、每股净资产等）

**说明**: 此接口返回所有可用字段（清除全 NaN 列后），提供最全面的财务分析数据。

---

### 5. 港股财报 (HK Stock Financial Report)

**接口函数**: `ak.stock_financial_hk_report_em()`

**数据源**: 东方财富网

**官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html#id452

**更新频率**: 年度更新

#### 支持报表类型
- 资产负债表（年度）
- 利润表（年度）
- 现金流量表（年度）

**说明**: 港股数据返回所有可用字段，字段名称可能与A股略有不同。

---

## 🌐 API 接口使用

### 1. 搜索股票

**端点**: `GET /api/search`

**参数**:
- `keyword` (必填): 搜索关键词（公司名称或代码）
- `market` (可选): 市场类型 `A` 或 `HK`

**示例**:
```bash
GET /api/search?keyword=海螺水泥
GET /api/search?keyword=腾讯控股&market=HK
```

**响应**:
```json
{
  "found": true,
  "code": "600585",
  "name": "海螺水泥",
  "symbol": "SH600585",
  "market": "A"
}
```

---

### 2. 获取财报数据

**端点**: `POST /api/financial-report`

**请求体**:
```json
{
  "company": "海螺水泥",
  "market": "A"  // 可选：A 或 HK
}
```

**响应结构**:
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
      "balance_sheet": [...],      // 资产负债表（最近3年，约12-16条）
      "income_statement": [...],   // 利润表（最近3年，约12-16条）
      "cash_flow": [...],          // 现金流量表（最近3年，约12-16条）
      "financial_indicator": [...]  // 财务指标（最近3年数据）
    }
  },
  "message": "获取成功"
}
```

---

## 📊 数据特点

### 历史数据深度
**返回最近3年 + 最新季度的数据**（例如2026年2月，返回2023、2024、2025年的数据）

根据测试结果（以海螺水泥为例）：
- **资产负债表**: 约12-16条记录（最近3年季度数据）
- **利润表**: 约12-16条记录（最近3年季度数据）
- **现金流量表**: 约12-16条记录（最近3年季度数据）
- **财务指标**: 最近3年数据（所有季度）

**说明**: 
- A股每年4个季度报告（Q1/Q2/Q3/年报），3年约12条记录
- 数据自动过滤，只保留指定年份范围内的数据
- 既包含完整财报，又避免历史数据过多

### 数据完整性
- ✅ 所有字段均来自官方披露的财报数据
- ✅ 自动过滤全 NaN 字段
- ✅ 保留核心财务指标（API 返回）
- ⚠️ 部分历史数据可能存在 NaN（正常现象）

### 数据时效性
- 📅 季报：每季度末后约1个月更新
- 📅 年报：每年4月30日前更新
- 🔄 实时从数据源获取最新数据

---

## 💡 使用场景

### 1. 财务分析自动化
- 定期获取上市公司财报数据
- 自动计算财务比率和指标
- 生成财务健康度报告

### 2. 投资决策支持
- 对比多家公司财务数据
- 跟踪关键指标变化趋势
- 发现投资机会或风险

### 3. n8n 工作流集成
- 定时任务自动获取财报
- 触发条件监控（如 ROE 变化）
- 财报数据推送通知

### 4. 数据分析和可视化
- 导出数据到 Excel/CSV
- 生成财务趋势图表
- 构建财务数据仪表盘

---

## ⚠️ 注意事项

### 数据说明
1. **NaN 值的含义**:
   - 该字段在该报告期未披露
   - 该字段不适用于该行业（如银行无存货）
   - 历史早期报告可能缺少某些字段

2. **字段差异**:
   - A股和港股字段名称可能不同
   - 不同行业披露的字段有差异
   - 会计准则变更可能影响字段定义

3. **数据延迟**:
   - 数据来源于第三方网站
   - 可能存在1-2天的延迟
   - 重大修正需等待数据源更新

### 性能优化
- ✅ 已过滤冗余字段（从300+减少到15-17个核心字段）
- ✅ 响应体积优化，适合 API 传输
- ✅ 自动处理 JSON 不兼容值（NaN/Inf）

### 合规使用
- 📖 数据仅供个人研究和学习使用
- 📖 请遵守数据源网站的使用条款
- 📖 商业使用需获得相应授权

---

## 🔧 技术架构

### 技术栈
- **框架**: FastAPI
- **数据源**: AKShare
- **数据处理**: Pandas
- **部署**: Uvicorn

### 数据流程
```
用户请求 → API 接口 → 搜索股票代码 
→ 调用 AKShare 接口 → 数据清洗 
→ 字段过滤 → JSON 格式化 → 返回响应
```

### 字段过滤策略
1. 保留核心财务字段（预定义列表）
2. 移除完全为 NaN 的列
3. 清理 JSON 不兼容值（NaN → null）
4. 格式化日期时间字段

---

## 📞 快速开始

### 启动服务
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动 API 服务
python main.py

# 服务运行在 http://localhost:8000
```

### 测试数据
```bash
# 运行测试脚本查看完整数据结构
python test_data.py
```

### API 文档
访问 http://localhost:8000/docs 查看交互式 API 文档（Swagger UI）

---

## 📈 示例：财务分析

### 计算关键财务比率
```python
# 资产负债率
debt_ratio = TOTAL_LIABILITIES / TOTAL_ASSETS

# 净利率
net_margin = PARENT_NETPROFIT / OPERATE_INCOME

# 经营现金流占比
ocf_ratio = NETCASH_OPERATE / PARENT_NETPROFIT

# ROE（净资产收益率）
roe = PARENT_NETPROFIT / TOTAL_EQUITY
```

### 趋势分析
```python
# 获取近4个季度数据
recent_data = financial_data['income_statement'][:4]

# 计算营收同比增长率
revenue_growth = (Q4_revenue - Q4_last_year_revenue) / Q4_last_year_revenue * 100

# 计算净利润同比增长率
profit_growth = (Q4_profit - Q4_last_year_profit) / Q4_last_year_profit * 100
```

---

## 📚 相关资源

- [AKShare 官方文档](https://akshare.akfamily.xyz/)
- [东方财富网](https://www.eastmoney.com/)
- [新浪财经](https://finance.sina.com.cn/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 📝 更新日志

### v1.0.0 (2026-02-14)
- ✅ 实现 A股财报数据接口
- ✅ 实现港股财报数据接口
- ✅ 智能股票搜索功能
- ✅ 数据清洗和格式化
- ✅ 字段过滤优化
- ✅ API 文档完善

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2026-02-14
