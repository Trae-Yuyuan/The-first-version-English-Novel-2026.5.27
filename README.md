# 26.6.4 英语化小说 C版

AI 驱动的中文小说英语翻译工具，结合四六级重点词汇高亮，实现"兴趣阅读 + 精准备考"。

## 功能

- 输入 DeepSeek API Key
- 拖拽上传中文小说 TXT 文件
- 拖拽上传四六级重点词汇 TXT 文件
- AI 翻译小说为英文，四六级词汇蓝色高亮
- 支持下载译文和全屏阅读器

## 快速开始

### Windows
```powershell
.\scripts\start.ps1
```

### macOS / Linux
```bash
bash scripts/start.sh
```

然后浏览器访问 `http://localhost:5173`

## 手动启动

### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 技术栈

- 前端：React 18 + Vite + NES.css
- 后端：Flask + DeepSeek API
- 样式：NES.css 像素复古风格

## 项目结构

```
├── backend/          # Python Flask 后端
├── frontend/         # React 前端
├── scripts/          # 一键启动脚本
└── .github/          # GitHub Actions CI/CD
```
