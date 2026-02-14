# 📊 AKShare 财报数据可视化平台

为 n8n 工作流提供 A股/港股 财报数据的 API 服务,并提供现代化的可视化界面。

**🌐 在线访问**: https://web-production-b3d5b.up.railway.app/

## ✨ 功能特性

### 🖥️ 可视化界面 (NEW!)
- 🎨 现代化的 Web 界面
- 📊 财报数据可视化查询和展示
- 🧠 投资学习思维导图在线查看
- 📚 完整的 API 文档页面
- 📱 响应式设计,支持移动端

### 🔌 API 服务
- 支持 A 股和港股
- 自动搜索股票代码
- 获取资产负债表、利润表、现金流量表、财务指标
- 数据格式化(自动单位转换、关键指标计算)

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

## 🚀 快速开始

### 在线使用

直接访问: https://web-production-b3d5b.up.railway.app/

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python3 main.py

# 3. 访问界面
# 可视化界面: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

## 📖 文档

- [前端使用说明](./前端使用说明.md) - 界面使用指南
- [API 文档](./API文档.md) - 接口技术文档
- [部署指南](./DEPLOYMENT.md) - Railway 部署说明
- [项目总览](./项目总览.md) - 完整项目介绍

## 🎯 使用示例

### 方式 1: Web 界面

1. 打开浏览器访问主页
2. 在"接口测试"输入公司名称(如"茅台")
3. 点击查询,查看财报数据
4. 切换标签查看不同报表

### 方式 2: API 调用

```bash
curl -X POST https://web-production-b3d5b.up.railway.app/api/financial-report \
  -H "Content-Type: application/json" \
  -d '{"company": "茅台", "market": "A"}'
```

## 📸 界面预览

- ✅ 财报数据查询界面
- ✅ 思维导图查看器
- ✅ API 文档页面
- ✅ 深色主题侧边栏
- ✅ 响应式布局
