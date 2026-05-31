const { app, BrowserWindow, ipcMain } = require('electron');
const express = require('express');
const path = require('path');
const os = require('os');

let mainWindow;
let expressServer;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        resizable: false,
        frame: false,
        titleBarStyle: 'hidden',
        titleBarOverlay: false,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'icon.ico'),
        backgroundColor: '#f5f5f5'
    });

    mainWindow.loadFile('static/index.html');

    mainWindow.on('closed', function () {
        mainWindow = null;
        if (expressServer) {
            expressServer.close();
        }
    });
}

ipcMain.on('window-minimize', () => {
    mainWindow.minimize();
});

ipcMain.on('window-close', () => {
    mainWindow.close();
});

function startExpressServer() {
    const expressApp = express();
    const port = 5000;

    expressApp.use(express.json());
    expressApp.use(express.static(path.join(__dirname, 'static')));

    expressApp.post('/api/search', (req, res) => {
        const { path: searchPath, keyword, startDate, endDate } = req.body;
        
        if (!searchPath || !require('fs').existsSync(searchPath)) {
            return res.json({ error: '无效的路径' });
        }

        const results = searchLogs(searchPath, keyword, startDate, endDate);
        res.json({ results });
    });

    expressApp.post('/api/file/content', (req, res) => {
        const { path: filePath } = req.body;
        
        if (!filePath || !require('fs').existsSync(filePath)) {
            return res.json({ error: '无效的文件路径' });
        }

        try {
            const content = require('fs').readFileSync(filePath, 'utf-8');
            res.json({ content, path: filePath });
        } catch (err) {
            res.json({ error: err.message });
        }
    });

    expressApp.post('/api/file/download', (req, res) => {
        const { path: filePath } = req.body;
        
        if (!filePath || !require('fs').existsSync(filePath)) {
            return res.json({ error: '无效的文件路径' });
        }

        res.download(filePath);
    });

    expressApp.post('/api/files/download', (req, res) => {
        const { paths } = req.body;
        
        if (!paths || paths.length === 0) {
            return res.json({ error: '请选择要下载的文件' });
        }

        const zip = require('adm-zip')();
        
        paths.forEach(filePath => {
            if (require('fs').existsSync(filePath)) {
                zip.addLocalFile(filePath);
            }
        });

        const buffer = zip.toBuffer();
        res.set('Content-Type', 'application/zip');
        res.set('Content-Disposition', 'attachment; filename=logs.zip');
        res.send(buffer);
    });

    expressApp.post('/api/path/validate', (req, res) => {
        const { path: validatePath } = req.body;
        
        if (require('fs').existsSync(validatePath)) {
            const stat = require('fs').statSync(validatePath);
            res.json({ valid: true, exists: true, isFile: stat.isFile() });
        } else {
            res.json({ valid: false, exists: false });
        }
    });

    expressApp.get('/', (req, res) => {
        res.sendFile(path.join(__dirname, 'static/index.html'));
    });

    expressServer = expressApp.listen(port, '127.0.0.1', () => {
        console.log(`Express server running on http://127.0.0.1:${port}`);
    });
}

function searchLogs(basePath, keyword = '', startDate = '', endDate = '') {
    const fs = require('fs');
    const path = require('path');
    const { parse } = require('date-fns');

    const results = [];

    function walk(dir) {
        let files;
        try {
            files = fs.readdirSync(dir);
        } catch (err) {
            return;
        }

        files.forEach(file => {
            const filePath = path.join(dir, file);
            let stat;
            try {
                stat = fs.statSync(filePath);
            } catch (err) {
                return;
            }

            if (stat.isDirectory()) {
                walk(filePath);
            } else if (file.endsWith('.log')) {
                try {
                    const fileDate = new Date(stat.mtime);
                    
                    let validDate = true;
                    if (startDate) {
                        const start = parse(startDate, 'yyyy-MM-dd', new Date());
                        if (fileDate < start) validDate = false;
                    }
                    if (endDate) {
                        const end = parse(endDate, 'yyyy-MM-dd', new Date());
                        end.setDate(end.getDate() + 1);
                        if (fileDate > end) validDate = false;
                    }

                    if (!validDate) return;

                    let content = '';
                    try {
                        content = fs.readFileSync(filePath, 'utf-8');
                    } catch (err) {
                        content = '';
                    }

                    if (keyword) {
                        if (!content.toLowerCase().includes(keyword.toLowerCase())) {
                            return;
                        }
                    }

                    results.push({
                        path: filePath,
                        filename: file,
                        size: stat.size,
                        modified: fileDate.toLocaleString('zh-CN'),
                        preview: content.substring(0, 500)
                    });
                } catch (err) {
                    return;
                }
            }
        });
    }

    walk(basePath);
    results.sort((a, b) => new Date(b.modified) - new Date(a.modified));
    return results;
}

app.on('ready', () => {
    startExpressServer();
    createWindow();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', function () {
    if (mainWindow === null) createWindow();
});
