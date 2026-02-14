// ===== 全局变量 =====
let allFiles = [];
let currentFile = null;

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    // 配置 Marked
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (err) {}
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });
    
    // 配置 Mermaid
    mermaid.initialize({ 
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
    });
    
    // 加载文件列表
    loadFileList();
});

// ===== 加载文件列表 =====
async function loadFileList() {
    const fileListEl = document.getElementById('fileList');
    const fileCountEl = document.getElementById('fileCount');
    
    try {
        fileListEl.innerHTML = '<div class="loading">加载中...</div>';
        
        const response = await fetch('/api/markdown/list');
        const data = await response.json();
        
        allFiles = data.files || [];
        fileCountEl.textContent = allFiles.length;
        
        if (allFiles.length === 0) {
            fileListEl.innerHTML = '<div class="loading">未找到 Markdown 文件</div>';
            return;
        }
        
        renderFileList(allFiles);
        
    } catch (error) {
        console.error('加载文件列表失败:', error);
        fileListEl.innerHTML = '<div class="loading">加载失败，请刷新重试</div>';
    }
}

// ===== 渲染文件列表 =====
function renderFileList(files) {
    const fileListEl = document.getElementById('fileList');
    
    if (files.length === 0) {
        fileListEl.innerHTML = '<div class="loading">未找到匹配的文件</div>';
        return;
    }
    
    fileListEl.innerHTML = files.map(file => {
        const sizeKB = (file.size / 1024).toFixed(1);
        return `
            <div class="file-item" onclick="loadMarkdownFile('${file.path}')" data-path="${file.path}">
                <div class="file-item-name">${escapeHtml(file.name)}</div>
                <div class="file-item-path">${escapeHtml(file.path)}</div>
                <div class="file-item-size">${sizeKB} KB</div>
            </div>
        `;
    }).join('');
}

// ===== 搜索过滤 =====
function filterFiles() {
    const searchInput = document.getElementById('searchInput');
    const keyword = searchInput.value.toLowerCase().trim();
    
    if (!keyword) {
        renderFileList(allFiles);
        return;
    }
    
    const filtered = allFiles.filter(file => {
        return file.name.toLowerCase().includes(keyword) || 
               file.path.toLowerCase().includes(keyword);
    });
    
    renderFileList(filtered);
}

// ===== 加载 Markdown 文件 =====
async function loadMarkdownFile(path) {
    const welcomeScreen = document.getElementById('welcomeScreen');
    const documentView = document.getElementById('documentView');
    const markdownContent = document.getElementById('markdownContent');
    const docTitle = document.getElementById('docTitle');
    const docPath = document.getElementById('docPath');
    const docSize = document.getElementById('docSize');
    
    try {
        // 显示加载状态
        welcomeScreen.style.display = 'none';
        documentView.style.display = 'flex';
        markdownContent.innerHTML = '<div class="loading">加载中...</div>';
        
        // 更新选中状态
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.path === path) {
                item.classList.add('active');
            }
        });
        
        // 获取文件内容
        const response = await fetch(`/api/markdown/content?path=${encodeURIComponent(path)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        currentFile = data;
        
        // 更新文档信息
        docTitle.textContent = data.filename;
        docPath.textContent = data.path;
        docSize.textContent = `${(data.size / 1024).toFixed(1)} KB`;
        
        // 渲染 Markdown
        renderMarkdown(data.content);
        
    } catch (error) {
        console.error('加载文件失败:', error);
        markdownContent.innerHTML = `
            <div class="loading" style="color: #dc3545;">
                ❌ 加载失败: ${escapeHtml(error.message)}
            </div>
        `;
    }
}

// ===== 渲染 Markdown =====
async function renderMarkdown(content) {
    const markdownContent = document.getElementById('markdownContent');
    
    try {
        // 1. 使用 marked 转换为 HTML
        let html = marked.parse(content);
        
        // 2. 渲染到页面
        markdownContent.innerHTML = html;
        
        // 3. 代码高亮
        markdownContent.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        // 4. 渲染 Mermaid 图表
        const mermaidBlocks = markdownContent.querySelectorAll('code.language-mermaid');
        for (let i = 0; i < mermaidBlocks.length; i++) {
            const block = mermaidBlocks[i];
            const code = block.textContent;
            const pre = block.parentElement;
            
            try {
                const { svg } = await mermaid.render(`mermaid-${i}`, code);
                const div = document.createElement('div');
                div.className = 'mermaid';
                div.innerHTML = svg;
                pre.replaceWith(div);
            } catch (err) {
                console.error('Mermaid 渲染失败:', err);
            }
        }
        
        // 5. 生成目录
        generateTOC();
        
        // 6. 滚动到顶部
        markdownContent.scrollTop = 0;
        
        // 7. 处理内部链接
        setupInternalLinks();
        
    } catch (error) {
        console.error('渲染 Markdown 失败:', error);
        markdownContent.innerHTML = `
            <div class="loading" style="color: #dc3545;">
                ❌ 渲染失败: ${escapeHtml(error.message)}
            </div>
        `;
    }
}

// ===== 生成目录 =====
function generateTOC() {
    const markdownContent = document.getElementById('markdownContent');
    const tocContent = document.getElementById('tocContent');
    
    const headings = markdownContent.querySelectorAll('h1, h2, h3, h4');
    
    if (headings.length === 0) {
        tocContent.innerHTML = '<p style="color: #999; font-size: 13px;">暂无目录</p>';
        return;
    }
    
    let tocHTML = '<ul>';
    
    headings.forEach((heading, index) => {
        const level = heading.tagName.toLowerCase();
        const text = heading.textContent;
        const id = `heading-${index}`;
        
        // 为标题添加 ID
        heading.id = id;
        
        tocHTML += `
            <li>
                <a href="#${id}" class="toc-${level}" onclick="scrollToHeading('${id}'); return false;">
                    ${escapeHtml(text)}
                </a>
            </li>
        `;
    });
    
    tocHTML += '</ul>';
    tocContent.innerHTML = tocHTML;
}

// ===== 滚动到标题 =====
function scrollToHeading(id) {
    const heading = document.getElementById(id);
    if (heading) {
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ===== 切换目录显示 =====
function toggleTOC() {
    const toc = document.getElementById('tableOfContents');
    toc.classList.toggle('show');
}

// ===== 处理内部链接 =====
function setupInternalLinks() {
    const markdownContent = document.getElementById('markdownContent');
    const links = markdownContent.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToHeading(targetId);
        });
    });
}

// ===== 工具函数 =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== 键盘快捷键 =====
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + F: 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
    
    // Ctrl/Cmd + T: 切换目录
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        toggleTOC();
    }
});
