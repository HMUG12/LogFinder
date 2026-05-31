# 日志查找器 (Log Finder)
<img width="1672" height="941" alt="20260530131919-31b8ec78-0e48dc23" src="https://github.com/user-attachments/assets/c9d3e6c4-d16d-44da-8c37-a00ea09a1406" />

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Tkinter-GUI-green.svg" alt="GUI Framework">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

为Project neko日志查找而开发的一个功能强大的Windows桌面日志查找器，支持路径日志查找、日期过滤搜索、日志文件提取等功能。
<img width="1254" height="1254" alt="20260530032518-e79e6903-33afcc2e" src="https://github.com/user-attachments/assets/f63965f9-2601-4233-b098-0340255714d2" />

---

## ✨ 功能特性

### 📂 日志搜索
- **路径日志查找**：支持自定义搜索路径，默认路径自动检测当前用户的N.E.K.O日志目录
- **日期过滤**：支持自定义日期范围搜索，默认向前推进1天
- **关键词搜索**：支持关键词过滤，搜索无结果时提示全局搜索
- **文件预览**：双击文件预览内容
- **批量下载**：支持多选文件并打包下载

### 🔧 测试工具
- **N.E.K.O测试日志收集**：支持启动projectneko_server.exe并收集日志
- **Steam模式**：自动构建Steam库路径
- **自定义模式**：手动选择N.E.K.O.exe所在目录
- **无窗口启动**：后台运行，不显示CMD窗口
- **实时日志捕获**：实时显示程序输出

### ⚙️ 设置
- **默认路径配置**：自定义默认搜索路径
- **日期范围设置**：设置默认搜索天数
- **编码格式选择**：支持UTF-8、GBK、GB2312、GB18030、ANSI等编码
- **测试路径配置**：设置Steam盘符和自定义路径

### 📱 用户体验
- **高级灰加白配色**：现代化UI设计
- **窗口大小限制**：固定最小窗口尺寸，确保布局完整
- **自定义窗口控制**：最小化和关闭按钮
- **首次启动更新日志**：展示版本更新内容

---

## 🚀 快速开始

### 系统要求
- Windows 10/11 (64位)
- Python 3.10+ (开发环境)

### 下载与运行

#### 方法一：下载预编译版本
1. 前往 [Releases](https://github.com/yourusername/log-finder/releases) 页面
2. 下载最新版本的 `LogFinder.zip`
3. 解压到任意目录
4. 运行 `LogFinder.exe`

#### 方法二：从源码运行
```bash
# 克隆仓库
git clone https://github.com/yourusername/log-finder.git
cd log-finder

# 安装依赖
pip install -r requirements.txt

# 运行程序
python log_finder.py
```

### 打包成EXE
```bash
# 使用PyInstaller打包
pyinstaller --clean --noupx --windowed --onedir --name=LogFinder --icon="20260530032518-e79e6903-33afcc2e_256x256.ico" log_finder.py

# 或使用打包脚本
build.bat
```

---

## 📖 使用说明

### 日志搜索页面
1. 在路径输入框中输入日志目录路径
2. 设置日期范围（可选，默认为最近1天）
3. 输入关键词进行过滤（可选）
4. 点击"搜索"按钮查找日志文件
5. 双击文件预览内容
6. 选择文件后点击"下载选中文件"批量下载

### 测试页面
1. 选择运行模式：
   - **Steam模式**：选择Steam盘符，自动构建路径
   - **自定义模式**：选择N.E.K.O.exe所在目录
2. 点击"启动并收集日志"按钮
3. 查看实时日志输出
4. 点击"停止"按钮停止程序
5. 点击"下载日志文件"保存日志

### 设置页面
1. 设置默认日志路径
2. 设置默认日期范围
3. 选择日志文件编码格式
4. 设置默认测试路径
5. 点击"保存设置"按钮

---

## 📁 项目结构

```
log-finder/
├── log_finder.py          # 主程序入口
├── LogFinder.spec         # PyInstaller打包配置
├── build.bat              # 一键打包脚本
├── ANTIVIRUS_GUIDE.md     # 防杀软误报指南
├── 20260530032518-e79e6903-33afcc2e_256x256.ico  # 应用图标
├── .gitignore             # Git忽略文件
├── README.md              # 项目说明文档
└── dist/                  # 打包输出目录
    └── LogFinder/         # onedir模式产物
```

---

## 🔧 配置说明

### 默认路径
程序启动时会自动检测以下路径：
- `C:\Users\{用户名}\AppData\Local\N.E.K.O\logs`

### 设置文件
设置保存在程序运行目录的 `log_finder_settings.json` 文件中：
```json
{
  "default_path": "C:\\Users\\用户名\\AppData\\Local\\N.E.K.O\\logs",
  "date_range": "7",
  "encoding": "utf-8-sig",
  "steam_drive": "D:",
  "custom_path": ""
}
```

---

## 🛡️ 安全提示

### 杀软误报处理
由于PyInstaller打包的特性，部分杀毒软件可能会误报。如遇到误报：
1. 将程序添加到杀软信任列表
2. 使用代码签名证书（推荐）
3. 参考 `ANTIVIRUS_GUIDE.md` 向杀软厂商提交误报

---

## 📝 更新日志

### v1.0.0
- ✨ 新增"测试"页面，支持N.E.K.O测试日志收集
- ✨ 支持Steam模式和自定义模式启动项目
- ✨ 设置页面新增编码格式选择
- ✨ 设置页面新增默认测试路径配置
- ✨ 新增首次启动更新日志弹窗
- 🎨 优化UI布局，确保最小窗口尺寸下完整显示
- 🔒 优化打包配置，减少杀软误报
- 🐛 修复双击预览后无法再次打开问题
- 🐛 修复选择下载文件数量不匹配问题
- 🐛 修复UI拖拽重叠问题

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**如果这个项目对你有帮助，请给个 ⭐️！**
