# 部署指南

## 🚀 Railway 部署

### 方法一: Git Push 自动部署 (推荐)

1. **提交代码到 Git**
```bash
git add .
git commit -m "添加可视化前端界面"
git push origin main
```

2. **Railway 自动部署**
   - Railway 会自动检测到代码变更
   - 自动重新构建和部署
   - 等待几分钟完成部署

3. **访问界面**
   - 打开 https://web-production-b3d5b.up.railway.app/
   - 应该看到新的可视化界面

### 方法二: Railway CLI 部署

```bash
# 安装 Railway CLI (如未安装)
npm i -g @railway/cli

# 登录
railway login

# 部署
railway up
```

## 📦 本地测试

### 1. 安装依赖

```bash
# 如果还没有安装
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方法 1: 直接运行
python3 main.py

# 方法 2: 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 方法 3: 使用测试脚本(会自动打开浏览器)
python3 test_frontend.py
```

### 3. 访问界面

打开浏览器访问: http://localhost:8000

## ✅ 验证部署

### 检查清单

- [ ] 主页能正常访问
- [ ] 接口测试功能正常(尝试搜索"茅台")
- [ ] 思维导图列表能显示
- [ ] 思维导图内容能正常渲染
- [ ] API文档页面显示正常
- [ ] 响应式布局在手机上正常

### 测试 API

```bash
# 测试健康检查
curl https://web-production-b3d5b.up.railway.app/health

# 测试思维导图列表
curl https://web-production-b3d5b.up.railway.app/api/mindmaps

# 测试财报查询
curl -X POST https://web-production-b3d5b.up.railway.app/api/financial-report \
  -H "Content-Type: application/json" \
  -d '{"company": "茅台", "market": "A"}'
```

## 🔧 故障排查

### 1. 页面显示 404

**原因**: 静态文件未正确挂载

**解决**:
- 检查 `static/` 目录是否存在
- 确认 `index.html`, `styles.css`, `app.js` 都在 static 目录中
- 查看 Railway 日志确认文件是否上传

### 2. 思维导图不显示

**原因**: 思维导图目录未上传或路径错误

**解决**:
- 确认 `思维导图/` 目录已提交到 Git
- 检查 `.gitignore` 是否排除了该目录
- 确认目录中有 `.md` 文件

### 3. 接口调用失败

**原因**: CORS 配置或后端服务问题

**解决**:
- 检查 Railway 日志查看错误信息
- 确认 AKShare 依赖已正确安装
- 测试基础 API 接口是否正常

### 4. 样式丢失

**原因**: CSS 文件路径错误

**解决**:
- 确认 HTML 中引用路径为 `/static/styles.css`
- 检查浏览器控制台是否有 404 错误
- 清除浏览器缓存重试

## 📝 更新内容说明

本次更新添加了以下文件:

```
akshare-api/
├── static/                      # 新增: 静态文件目录
│   ├── index.html              # 前端主页面
│   ├── styles.css              # 样式文件
│   └── app.js                  # JavaScript 交互逻辑
├── main.py                      # 更新: 添加静态文件支持和思维导图API
├── 前端使用说明.md              # 新增: 使用文档
├── DEPLOYMENT.md                # 新增: 部署指南
└── test_frontend.py            # 新增: 本地测试脚本
```

## 🎯 主要改动

### main.py
- 添加 `StaticFiles` 挂载
- 修改根路由返回 HTML 页面
- 新增 `/api/mindmaps` 接口(获取思维导图列表)
- 新增 `/api/mindmap/{filename}` 接口(获取思维导图内容)

### 新增功能
- 📊 财报数据可视化查询
- 🧠 思维导图在线查看
- 📚 API 文档展示
- 🎨 现代化 UI 设计

## 💡 提示

### Git 提交建议

```bash
# 查看变更
git status

# 添加所有文件
git add .

# 提交(使用有意义的提交信息)
git commit -m "feat: 添加可视化前端界面

- 添加财报数据查询界面
- 添加思维导图查看功能
- 添加API文档页面
- 优化用户体验"

# 推送到远程
git push origin main
```

### 环境变量

Railway 上确保设置了必要的环境变量:
- `PORT` - 已由 Railway 自动设置
- 其他自定义环境变量(如有)

## 📞 技术支持

如遇到问题:
1. 查看 Railway 部署日志
2. 检查浏览器控制台错误
3. 参考 `前端使用说明.md`
4. 联系开发者

---

**祝部署顺利! 🎉**
