const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', function() {
    const searchPathInput = document.getElementById('searchPath');
    const keywordInput = document.getElementById('keyword');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const searchBtn = document.getElementById('searchBtn');
    const browseBtn = document.getElementById('browseBtn');
    const pathStatus = document.getElementById('pathStatus');
    const resultsList = document.getElementById('resultsList');
    const resultCount = document.getElementById('resultCount');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const downloadSelectedBtn = document.getElementById('downloadSelectedBtn');
    const previewModal = document.getElementById('previewModal');
    const previewTitle = document.getElementById('previewTitle');
    const filePathSpan = document.getElementById('filePath');
    const fileContent = document.getElementById('fileContent');
    const downloadFileBtn = document.getElementById('downloadFileBtn');

    let currentResults = [];
    let selectedFiles = [];

    // 窗口控制函数
    window.minimizeWindow = function() {
        ipcRenderer.send('window-minimize');
    };

    window.closeWindow = function() {
        ipcRenderer.send('window-close');
    };

    // 验证路径
    searchPathInput.addEventListener('blur', function() {
        validatePath(this.value);
    });

    searchPathInput.addEventListener('input', function() {
        pathStatus.textContent = '';
        pathStatus.className = 'status';
    });

    async function validatePath(path) {
        if (!path.trim()) return;
        
        try {
            const response = await fetch('/api/path/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            const data = await response.json();
            
            if (data.exists) {
                pathStatus.textContent = '✓ 路径有效';
                pathStatus.className = 'status valid';
            } else {
                pathStatus.textContent = '✗ 路径不存在';
                pathStatus.className = 'status invalid';
            }
        } catch (error) {
            console.error('Path validation error:', error);
        }
    }

    // 浏览按钮点击
    browseBtn.addEventListener('click', function() {
        const { dialog } = require('electron').remote;
        dialog.showOpenDialog({
            properties: ['openDirectory'],
            title: '选择搜索目录'
        }).then(result => {
            if (!result.canceled && result.filePaths.length > 0) {
                searchPathInput.value = result.filePaths[0];
                validatePath(result.filePaths[0]);
            }
        }).catch(err => {
            console.error('Browse error:', err);
        });
    });

    // 搜索按钮点击
    searchBtn.addEventListener('click', function() {
        const path = searchPathInput.value.trim();
        const keyword = keywordInput.value.trim();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (!path) {
            alert('请输入搜索路径');
            return;
        }

        performSearch(path, keyword, startDate, endDate);
    });

    // 执行搜索
    async function performSearch(path, keyword, startDate, endDate) {
        resultsList.innerHTML = '<div class="loading">搜索中...</div>';
        resultCount.textContent = '找到 0 个文件';
        selectedFiles = [];
        updateDownloadButton();

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path, keyword, startDate, endDate })
            });

            const data = await response.json();
            
            if (data.results !== undefined) {
                currentResults = data.results;
                displayResults(data.results);
            } else {
                showError(data.error || '搜索失败');
            }
        } catch (error) {
            showError('网络错误，请检查服务是否运行');
        }
    }

    // 显示搜索结果
    function displayResults(results) {
        if (results.length === 0) {
            resultsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <p>未找到符合条件的日志文件</p>
                </div>
            `;
            resultCount.textContent = '找到 0 个文件';
            return;
        }

        resultCount.textContent = `找到 ${results.length} 个文件`;
        
        resultsList.innerHTML = results.map((file, index) => `
            <div class="file-item" data-index="${index}" onclick="handleItemClick(${index})">
                <input type="checkbox" class="file-checkbox" data-index="${index}" onclick="handleCheckboxClick(event, ${index})">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <h4>${escapeHtml(file.filename)}</h4>
                    <p title="${escapeHtml(file.path)}">${escapeHtml(file.path)}</p>
                    <div class="file-meta">
                        <span>${formatSize(file.size)}</span>
                        <span>${file.modified}</span>
                    </div>
                    ${file.preview ? `<div class="file-preview">${escapeHtml(file.preview)}</div>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    // 点击文件项
    window.handleItemClick = function(index) {
        const checkbox = document.querySelector(`.file-item[data-index="${index}"] .file-checkbox`);
        toggleSelect(index, !checkbox.checked);
    };
    
    // 点击复选框
    window.handleCheckboxClick = function(event, index) {
        event.stopPropagation();
        const checkbox = document.querySelector(`.file-item[data-index="${index}"] .file-checkbox`);
        toggleSelect(index, checkbox.checked);
    };

    // 切换选择状态
    window.toggleSelect = function(index, checked) {
        const item = document.querySelector(`.file-item[data-index="${index}"]`);
        const checkbox = document.querySelector(`.file-item[data-index="${index}"] .file-checkbox`);
        
        if (checked) {
            checkbox.checked = true;
            item.classList.add('selected');
            if (!selectedFiles.includes(index)) {
                selectedFiles.push(index);
            }
        } else {
            checkbox.checked = false;
            item.classList.remove('selected');
            selectedFiles = selectedFiles.filter(i => i !== index);
        }
        
        updateDownloadButton();
    };

    // 更新下载按钮状态
    function updateDownloadButton() {
        downloadSelectedBtn.disabled = selectedFiles.length === 0;
        downloadSelectedBtn.textContent = selectedFiles.length > 0 
            ? `下载选中 (${selectedFiles.length})` 
            : '下载选中';
    }

    // 全选/取消全选
    selectAllBtn.addEventListener('click', function() {
        const allChecked = selectedFiles.length === currentResults.length;
        
        if (allChecked) {
            selectedFiles.forEach(index => {
                toggleSelect(index, false);
            });
            selectedFiles = [];
        } else {
            currentResults.forEach((_, index) => {
                toggleSelect(index, true);
            });
        }
        
        updateDownloadButton();
    });

    // 下载选中文件
    downloadSelectedBtn.addEventListener('click', function() {
        if (selectedFiles.length === 0) return;

        const paths = selectedFiles.map(index => currentResults[index].path);
        
        showDownloadOptions(paths);
    });
    
    // 显示下载选项
    function showDownloadOptions(paths) {
        const modal = document.createElement('div');
        modal.className = 'download-modal';
        modal.innerHTML = `
            <div class="download-modal-content">
                <div class="download-modal-header">
                    <h3>选择下载方式</h3>
                    <button class="download-modal-close" onclick="closeDownloadModal()">×</button>
                </div>
                <div class="download-modal-body">
                    <p>已选择 ${paths.length} 个文件</p>
                    <div class="download-options">
                        <button class="download-option-btn" onclick="downloadAsOriginal(${JSON.stringify(paths)})">
                            📁 下载原文件${paths.length > 1 ? '（逐个下载）' : ''}
                        </button>
                        <button class="download-option-btn" onclick="downloadAsZip(${JSON.stringify(paths)})">
                            📦 打包为ZIP下载
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.classList.add('show');
    }
    
    // 关闭下载选项对话框
    window.closeDownloadModal = function() {
        const modal = document.querySelector('.download-modal');
        if (modal) {
            modal.remove();
        }
    };
    
    // 下载原文件
    window.downloadAsOriginal = async function(paths) {
        closeDownloadModal();
        for (const path of paths) {
            try {
                const response = await fetch('/api/file/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    downloadBlob(blob, path.split('\\').pop());
                }
                await new Promise(resolve => setTimeout(resolve, 500));
            } catch (error) {
                showError('下载失败');
                break;
            }
        }
    };
    
    // 打包为ZIP下载
    window.downloadAsZip = async function(paths) {
        closeDownloadModal();
        try {
            const response = await fetch('/api/files/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                downloadBlob(blob, 'logs.zip');
            }
        } catch (error) {
            showError('下载失败');
        }
    };

    // 下载文件
    async function downloadFiles(paths) {
        try {
            if (paths.length === 1) {
                const response = await fetch('/api/file/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: paths[0] })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    downloadBlob(blob, paths[0].split('\\').pop());
                }
            } else {
                const response = await fetch('/api/files/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paths })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    downloadBlob(blob, 'logs.zip');
                }
            }
        } catch (error) {
            showError('下载失败');
        }
    }

    // 下载Blob文件
    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // 预览文件
    window.previewFile = function(index) {
        const file = currentResults[index];
        
        previewTitle.textContent = `预览: ${file.filename}`;
        filePathSpan.textContent = file.path;
        downloadFileBtn.onclick = () => downloadFiles([file.path]);
        
        fetch('/api/file/content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: file.path })
        })
        .then(response => response.json())
        .then(data => {
            fileContent.textContent = data.content || '无法读取文件内容';
            previewModal.classList.add('show');
        })
        .catch(error => {
            fileContent.textContent = '无法读取文件内容';
            previewModal.classList.add('show');
        });
    };

    // 关闭模态框
    window.closeModal = function() {
        previewModal.classList.remove('show');
        fileContent.textContent = '';
        filePathSpan.textContent = '';
        previewTitle.textContent = '文件预览';
    };

    // 点击模态框外部关闭
    previewModal.addEventListener('click', function(e) {
        if (e.target === previewModal) {
            closeModal();
        }
    });

    // 双击文件预览
    resultsList.addEventListener('dblclick', function(e) {
        const item = e.target.closest('.file-item');
        if (item && !e.target.classList.contains('file-checkbox')) {
            const index = parseInt(item.dataset.index);
            if (!isNaN(index)) {
                previewFile(index);
            }
        }
    });

    // 显示错误信息
    function showError(message) {
        resultsList.innerHTML = `<div class="error-message">${message}</div>`;
    }

    // 格式化文件大小
    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // HTML转义
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
