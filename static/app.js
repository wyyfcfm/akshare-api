// 全局状态
let currentFinancialData = null;
let currentReport = "balance";

// 初始化
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initAPIPanel();
  initMindmapPanel();

  // 初始化 Mermaid
  mermaid.initialize({
    startOnLoad: true,
    theme: "default",
    securityLevel: "loose",
  });
});

// 导航切换
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const panels = document.querySelectorAll(".panel");

  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      const targetTab = item.dataset.tab;

      // 如果没有 data-tab 属性，说明是外部链接，允许正常跳转
      if (!targetTab) {
        return; // 不阻止默认行为，让链接正常跳转
      }

      // 有 data-tab 属性的是内部面板切换
      e.preventDefault();

      // 更新导航状态
      navItems.forEach((nav) => nav.classList.remove("active"));
      item.classList.add("active");

      // 显示对应面板
      panels.forEach((panel) => panel.classList.remove("active"));
      document.getElementById(`${targetTab}-panel`).classList.add("active");

      // 如果切换到思维导图面板,加载列表
      if (targetTab === "mindmap") {
        loadMindmaps();
      }
    });
  });
}

// API面板初始化
function initAPIPanel() {
  const searchBtn = document.getElementById("search-btn");
  const companyInput = document.getElementById("company-input");
  const marketSelect = document.getElementById("market-select");

  // 查询按钮
  searchBtn.addEventListener("click", () => {
    const company = companyInput.value.trim();
    const market = marketSelect.value || null;
    if (company) {
      searchFinancialReport(company, market);
    }
  });

  // 回车键查询
  companyInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      searchBtn.click();
    }
  });

  // 快速查询按钮
  const quickBtns = document.querySelectorAll(".btn-tag");
  quickBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const company = btn.dataset.company;
      const market = btn.dataset.market;
      companyInput.value = company;
      marketSelect.value = market;
      searchFinancialReport(company, market);
    });
  });

  // 财报标签切换
  const reportTabs = document.querySelectorAll(".tab-btn");
  reportTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const reportType = tab.dataset.report;
      currentReport = reportType;

      // 更新标签状态
      reportTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      // 显示对应数据
      if (currentFinancialData) {
        displayReportData(currentFinancialData, reportType);
      }
    });
  });
}

// 查询财报数据
async function searchFinancialReport(company, market) {
  const loading = document.getElementById("loading");
  const resultSection = document.getElementById("result-section");
  const errorMessage = document.getElementById("error-message");

  // 显示加载状态
  loading.style.display = "block";
  resultSection.style.display = "none";
  errorMessage.style.display = "none";

  try {
    const response = await fetch("/api/financial-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ company, market }),
    });

    const result = await response.json();

    if (result.success) {
      currentFinancialData = result.data;
      displayStockInfo(result.data.stock_info);
      displayReportData(result.data, currentReport);
      resultSection.style.display = "block";
    } else {
      showError(result.message);
    }
  } catch (error) {
    showError("查询失败: " + error.message);
  } finally {
    loading.style.display = "none";
  }
}

// 显示股票信息
function displayStockInfo(stockInfo) {
  const stockInfoDiv = document.getElementById("stock-info");
  const marketName = stockInfo.market === "A" ? "A股" : "港股";

  stockInfoDiv.innerHTML = `
        <h3>${stockInfo.name}</h3>
        <div class="info-row">
            <div class="info-item">
                <div class="info-label">股票代码</div>
                <div class="info-value">${stockInfo.code}</div>
            </div>
            <div class="info-item">
                <div class="info-label">市场</div>
                <div class="info-value">${marketName}</div>
            </div>
            <div class="info-item">
                <div class="info-label">交易代码</div>
                <div class="info-value">${stockInfo.symbol || stockInfo.code}</div>
            </div>
        </div>
    `;
}

// 显示财报数据
function displayReportData(data, reportType) {
  const reportContent = document.getElementById("report-content");

  let reportData = [];
  let reportName = "";

  switch (reportType) {
    case "balance":
      reportData = data.financial.balance_sheet || [];
      reportName = "资产负债表";
      break;
    case "income":
      reportData = data.financial.income_statement || [];
      reportName = "利润表";
      break;
    case "cashflow":
      reportData = data.financial.cash_flow || [];
      reportName = "现金流量表";
      break;
    case "indicator":
      reportData = data.financial.financial_indicator || [];
      reportName = "财务指标";
      break;
  }

  if (!reportData || reportData.length === 0) {
    reportContent.innerHTML = `
            <div class="empty-state">
                <div class="icon">📊</div>
                <h3>暂无${reportName}数据</h3>
                <p>该公司可能没有可用的${reportName}数据</p>
            </div>
        `;
    return;
  }

  // 生成表格
  const headers = Object.keys(reportData[0]);
  let tableHTML = `
        <table class="report-table">
            <thead>
                <tr>
                    ${headers.map((h) => `<th>${h}</th>`).join("")}
                </tr>
            </thead>
            <tbody>
    `;

  reportData.forEach((row) => {
    tableHTML += "<tr>";
    headers.forEach((header) => {
      let value = row[header];
      let cellClass = "";

      // 数字类型判断
      if (
        typeof value === "string" &&
        (value.includes("亿") || value.includes("万") || value.includes("%"))
      ) {
        cellClass = "number";
        // 判断正负
        if (value.includes("-")) {
          cellClass += " negative";
        } else if (value !== null && value !== "" && !value.includes("0.00")) {
          cellClass += " positive";
        }
      }

      if (value === null || value === "") {
        value = "-";
      }

      tableHTML += `<td class="${cellClass}">${value}</td>`;
    });
    tableHTML += "</tr>";
  });

  tableHTML += `
            </tbody>
        </table>
    `;

  reportContent.innerHTML = tableHTML;
}

// 显示错误信息
function showError(message) {
  const errorMessage = document.getElementById("error-message");
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
}

// 思维导图面板初始化
function initMindmapPanel() {
  const backBtn = document.getElementById("back-to-list");
  backBtn.addEventListener("click", () => {
    document.getElementById("mindmap-viewer").style.display = "none";
    document.getElementById("mindmap-list").style.display = "grid";
  });
}

// 加载思维导图列表
async function loadMindmaps() {
  const mindmapList = document.getElementById("mindmap-list");

  try {
    const response = await fetch("/api/mindmaps");
    const data = await response.json();

    if (!data.mindmaps || data.mindmaps.length === 0) {
      mindmapList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📚</div>
                    <h3>暂无思维导图</h3>
                    <p>思维导图目录为空</p>
                </div>
            `;
      return;
    }

    // 生成思维导图卡片
    mindmapList.innerHTML = data.mindmaps
      .map(
        (mindmap) => `
            <div class="mindmap-card" onclick="viewMindmap('${mindmap.filename}')">
                <h3>${mindmap.name}</h3>
                <div class="mindmap-meta">
                    <span>📄 ${mindmap.filename}</span>
                    <span> • </span>
                    <span>${formatFileSize(mindmap.size)}</span>
                </div>
            </div>
        `,
      )
      .join("");
  } catch (error) {
    mindmapList.innerHTML = `
            <div class="empty-state">
                <div class="icon">❌</div>
                <h3>加载失败</h3>
                <p>${error.message}</p>
            </div>
        `;
  }
}

// 查看思维导图
async function viewMindmap(filename) {
  const mindmapList = document.getElementById("mindmap-list");
  const mindmapViewer = document.getElementById("mindmap-viewer");
  const mindmapTitle = document.getElementById("mindmap-title");
  const mindmapContent = document.getElementById("mindmap-content");

  // 显示加载状态
  mindmapList.style.display = "none";
  mindmapViewer.style.display = "block";
  mindmapTitle.textContent = "加载中...";
  mindmapContent.innerHTML =
    '<div class="loading"><div class="spinner"></div><p>加载思维导图...</p></div>';

  try {
    const response = await fetch(`/api/mindmap/${filename}`);
    const data = await response.json();

    mindmapTitle.textContent = filename.replace(".md", "");

    // 使用 marked 解析 Markdown
    const htmlContent = marked.parse(data.content);
    mindmapContent.innerHTML = htmlContent;

    // 重新初始化 mermaid 图表
    mermaid.init(
      undefined,
      mindmapContent.querySelectorAll(".language-mermaid"),
    );
  } catch (error) {
    mindmapTitle.textContent = "加载失败";
    mindmapContent.innerHTML = `
            <div class="empty-state">
                <div class="icon">❌</div>
                <h3>无法加载思维导图</h3>
                <p>${error.message}</p>
            </div>
        `;
  }
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// 工具函数: 将对象数组转换为表格HTML
function arrayToTable(data, title = "") {
  if (!data || data.length === 0) return "<p>暂无数据</p>";

  const headers = Object.keys(data[0]);
  let html = title ? `<h4>${title}</h4>` : "";

  html += '<table class="data-table">';
  html += "<thead><tr>";
  headers.forEach((h) => (html += `<th>${h}</th>`));
  html += "</tr></thead><tbody>";

  data.forEach((row) => {
    html += "<tr>";
    headers.forEach((h) => {
      let value = row[h];
      if (value === null || value === undefined) value = "-";
      html += `<td>${value}</td>`;
    });
    html += "</tr>";
  });

  html += "</tbody></table>";
  return html;
}
