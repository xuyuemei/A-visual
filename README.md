## 📦 项目依赖总览表（前后端统一）

| 分类              | 依赖名称                     | 主要功能           | 说明                     |
| --------------- | ------------------------ | -------------- | ---------------------- |
| ✅ **后端核心依赖**    | **Flask**                | Web 框架         | 后端主框架，负责接口与服务逻辑        |
|                 | **Flask-Cors**           | 跨域访问           | 允许 React 前端访问 Flask 接口 |
|                 | **Flask-SQLAlchemy**     | ORM 数据库管理      | 操作 MySQL 数据库的 ORM 映射层  |
|                 | **pymysql**              | MySQL 驱动       | 连接 MySQL 数据库           |
|                 | **requests**             | HTTP 请求库       | 用于访问外部 API（如模型服务）      |
| ⚙️ **数据处理与可视化** | **pandas**               | 数据分析           | 表格清洗、筛选与统计             |
|                 | **numpy**                | 数值计算           | 支撑 pandas / sklearn 计算 |
|                 | **openpyxl**             | Excel 文件处理     | 读取与写入 `.xlsx` 表格       |
|                 | **matplotlib**           | 图表绘制           | 静态图表生成                 |
|                 | **plotly**               | 交互式图表          | 支持交互式可视化（用于前端展示）       |
|                 | **scikit-learn**         | 机器学习           | 提供回归、聚类、分析等算法          |
|                 | **scipy**                | 科学计算           | 数学计算与统计支持              |
| 🧠 **AI 模型扩展**  | **torch**                | 深度学习框架         | 支持模型推理与训练              |
|                 | **torchvision**          | 图像模型扩展         | 图像分析模型支持               |
|                 | **torchaudio**           | 音频模型扩展         | 语音与音频信号处理              |
|                 | **openai**               | 调用 OpenAI API  | 接入 AI 模型生成接口           |
| 🎨 **可选辅助库**    | **Pillow (PIL)**         | 图像处理           | 上传图片、封面生成等             |
|                 | **lxml**                 | 高速 HTML/XML 解析 | BeautifulSoup 的底层解析器   |
|                 | **beautifulsoup4**       | 网页解析           | 用于文本爬取与清洗              |
|                 | **selenium**             | 自动化工具          | 网页截图或自动抓取（可选）          |
|                 | **python-dotenv**        | 环境变量管理         | 安全存储配置项（如密钥）           |
|                 | **tqdm**                 | 进度条显示          | 监控循环或训练进度              |
|                 | **black / flake8**       | 代码规范工具         | 格式化与语法检查               |
| ⚛️ **前端核心依赖**   | **vite**                 | 前端构建工具         | 启动开发服务器（支持 HMR 热更新）    |
|                 | **react / react-dom**    | 前端框架           | 组件化页面渲染                |
|                 | **typescript**           | 类型系统           | 提供类型安全的开发环境            |
|                 | **@vitejs/plugin-react** | React 插件       | 让 Vite 正确处理 `.tsx` 文件  |
| 🧱 **前端功能组件**   | **antd**                 | UI 组件库         | 提供按钮、表格、卡片等前端组件        |
|                 | **@ant-design/icons**    | 图标库            | 搭配 AntD 使用的图标系统        |
|                 | **@ant-design/x**        | 高级输入组件         | 支持 prompt、sender 等复杂交互 |
|                 | **@fortune-sheet/react** | 在线表格组件         | 用于 Excel 数据展示与编辑       |

---

## ⚙️ 环境安装命令参考

**后端环境：**

```bash
# 创建并激活虚拟环境
conda create -n visual python=3.10
conda activate visual

# 安装依赖
pip install -r requirements.txt
pip install flask_sqlalchemy pymysql openpyxl Pillow
```

**前端环境：**

```bash
cd front
yarn install
yarn dev
```

> 💡 启动后：
>
> * 前端运行在 [http://localhost:5173](http://localhost:5173)
> * 后端运行在 [http://localhost:8000](http://localhost:8000)
> * 通过 Vite 的代理机制 (`vite.config.ts`) 实现前后端通信。

---

## ✅ 一句话总结

> 🔧 **后端** 负责逻辑与数据处理（Flask + pandas + SQLAlchemy）；
> 🎨 **前端** 负责交互与可视化（React + Vite + TypeScript + AntD）；
> 🧠 **AI 扩展** 模块增强了智能化数据分析能力；
> 两端协作形成完整的可视化分析与 AI 助理系统。

---

# 🏗️ Flask 后端项目结构总览

本项目是一个基于 **Flask + MySQL + CORS** 的后端系统，采用模块化架构与工厂模式设计。
它支持与前端（React）通过 RESTful API 通信，实现文件上传、数据处理与图表生成等核心功能。

---

## 🌍 一、总体结构

```plaintext
backend/
├── app/                     ← Flask 应用核心目录
│   ├── __init__.py          ← 工厂模式启动核心
│   ├── routes/              ← 路由层：定义各功能接口 📡
│   ├── services/            ← 业务逻辑层：数据分析与处理 🧠
│   ├── utils/               ← 工具函数层：通用功能与数据格式化 🧰
│   ├── models.py            ← 数据模型层：数据库 ORM 定义 💾
│   ├── config.py            ← 配置文件：数据库、密钥等 ⚙️
│   └── requirements.txt     ← 依赖列表（部署用）📦
│
└── run.py                   ← 启动后端服务的入口文件 🚀
```

❌ 已去掉：`__pycache__`、`node_modules`、`static`、`project_structure.txt` 等辅助或自动生成部分。

---

## 🧩 二、主要模块功能详解

---

### 1️⃣ `run.py` — 后端启动入口 🚀

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(port=8000, debug=True)
```

📘 **作用：**

* 运行 Flask；
* 调用工厂函数 `create_app()`；
* 启动监听端口（例如 [http://localhost:8000）。](http://localhost:8000）。)

🧠 **类比：** 它就像“电源开关”，一按就让整个后端系统运转起来。

---

### 2️⃣ `app/__init__.py` — 工厂模式核心 ⚙️

```python
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_pyfile('../config.py')
    db.init_app(app)

    from .routes import upload, dataprocess, chart, template
    app.register_blueprint(upload.bp)
    app.register_blueprint(dataprocess.bp)
    app.register_blueprint(chart.bp)
    app.register_blueprint(template.bp)
    return app
```

📘 **作用：**

* 创建 Flask 应用；
* 加载数据库与跨域配置；
* 注册所有功能模块的蓝图；
* 返回完整 app 实例给 `run.py` 启动。

🧩 **一句话总结：**

> 它是整个 Flask 项目的“装配工厂”。

---

### 3️⃣ `app/routes/` — 路由层 📡

📘 **作用：** 定义前后端通信接口（URL → 处理函数）。
例如 `/api/upload` 负责上传文件，`/api/dataprocess` 负责数据清洗。


💡 **理解方式：**

> 路由层就像“前台客服”：
>
> * 接收来自前端的请求；
> * 把任务交给“后厨”（services）；
> * 再把结果返回给前端。

---

### 4️⃣ `app/services/` — 业务逻辑层 🧠

📘 **作用：**

* 负责真正的“业务处理”；
* 封装所有计算逻辑、AI分析、数据统计或图表生成；
* 由路由层调用，不直接与前端交互。

```python
import pandas as pd
from app.utils.convert import df_to_celldata

def get_processed_data(input_value, sheet_data):
    df = pd.DataFrame(eval(sheet_data))
    if "清洗" in input_value:
        df = df.dropna()
    elif "筛选" in input_value:
        df = df[df["age"] > 30]
    return df_to_celldata(df)
```

🧠 **类比：**

> 路由层像“服务员”，
> services 就是“厨师”，
> 真正做饭（处理数据）的工作都在这里。

✅ **项目核心功能所在。**

---

### 5️⃣ `app/utils/` — 工具函数层 🧰（详细扩写）

📘 **作用：**
专门存放通用、可复用的“小工具函数”，用于格式转换、数据校验、日志记录等。

这些函数不依赖具体业务模块，**但会被多个 services 调用**。

#### 🔧 常见的功能类型

| 功能类型        | 示例函数                               | 作用说明                             |
| ----------- | ---------------------------------- | -------------------------------- |
| **数据格式转换**  | `df_to_celldata(df)`               | 把 Pandas DataFrame 转成前端可识别的 JSON |
| **图片/文件处理** | `image_to_base64(path)`            | 把图片编码为 Base64 以便前端显示             |
| **异常与日志处理** | `log_error(msg)`                   | 记录系统运行时的错误或警告信息                  |
| **数据校验**    | `check_columns(df, required_cols)` | 检查上传表格是否包含必要字段                   |
| **通用计算**    | `normalize_values(list)`           | 将数据归一化或标准化，供分析算法使用               |


🧠 **理解方式：**

> 工具层就是一个“工具箱”，
> 任何模块都能从里面拿到标准化的小工具，
> 保证系统结构干净、逻辑分明。

---

### 6️⃣ `app/models.py` — 数据模型层 💾

📘 **作用：**
使用 SQLAlchemy ORM 定义数据库表结构，替代繁琐的 SQL 语句操作。

```python
class UserTable(db.Model):
    __tablename__ = 'User_table'
    User_ID = db.Column(db.Integer, primary_key=True)
    User_name = db.Column(db.String(50))
    User_phone = db.Column(db.String(20), unique=True)
    User_level = db.Column(db.String(20), default='普通用户')
```

💡 **优点：**

* 直接用 Python 类读写数据库；
* 代码更简洁、安全；
* 方便数据库迁移。


---

### 7️⃣ `config.py` — 配置文件 ⚙️

📘 **作用：**

* 定义数据库连接信息；
* 控制全局参数（如密钥、调试模式）。

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/visual_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your_secret_key'
```

---

### 8️⃣ `requirements.txt` — 依赖列表 📦

📘 **作用：**
记录所有项目依赖库，一键安装环境：

```
pip install -r requirements.txt
```

✅ **部署阶段必需。**

---

## 🧭 三、最小可运行结构（推荐模板）

```plaintext
backend/
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── upload.py
│   │   ├── dataprocess.py
│   │   └── chart.py
│   ├── services/
│   │   ├── data_process_service.py
│   │   └── chart_service.py
│   ├── utils/
│   │   └── convert.py
│   ├── models.py
│   └── config.py
├── run.py
└── requirements.txt
```

✅ 这是搭建一个 Flask 后端系统的**最小可运行骨架**。

---

## 🧠 四、总结一句话

> Flask 项目可以看作一个层层分工的系统：
>
> * `routes` 负责接收前端请求；
> * `services` 负责处理核心逻辑；
> * `utils` 负责提供工具支撑；
> * `models` 管理数据库；
> * `config` 配置系统环境；
> * `run.py` 启动服务。
>
> 工具函数层虽然不是必需，但能显著提升代码复用性与可维护性，是大型项目不可或缺的“润滑剂”。

---

---


# 🧭 前端项目结构总览（Vite + React ）

本项目的前端基于 **Vite + React + TypeScript** 搭建，
采用组件化 + 模块化架构，结合 Ant Design、FortuneSheet 等库实现可视化数据交互界面。

---

## 🌍 一、总体目录结构（已去掉辅助和构建缓存）

```plaintext
front_work/
└── front/                       ← 前端项目根目录
    ├── public/                  ← 静态资源（不参与打包）📂
    ├── src/                     ← 源代码目录（开发核心）💡
    │   ├── assets/              ← 图片、图标、样式资源
    │   ├── components/          ← 通用组件（可复用 UI 模块）🧩
    │   ├── pages/               ← 页面模块（对应系统功能界面）📄
    │   ├── App.tsx              ← 应用主组件（页面结构入口）⚙️
    │   ├── main.tsx             ← 应用启动入口（挂载 React 根节点）🚀
    │   ├── index.css            ← 全局样式
    │   └── vite-env.d.ts        ← 类型声明文件（TypeScript 辅助）
    │
    ├── index.html               ← 页面入口模板（HTML 容器）🏗️
    ├── vite.config.ts           ← Vite 构建与代理配置文件 ⚡
    ├── tsconfig.json            ← TypeScript 全局配置 📘
    ├── eslint.config.js         ← 代码规范检查（可选）🧹
    ├── package.json             ← 前端依赖与脚本管理 📦
    └── README.md                ← 项目说明文档
```

✅ 仅保留核心开发文件；
❌ 已去掉：`node_modules`、`.lock` 文件、`.gitignore`、`.editorconfig` 等构建或版本管理辅助内容。

---

## ⚙️ 二、核心文件夹说明

---

### 1️⃣ `index.html` —— 前端项目的“容器页面” 🏗️

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>数据可视化系统</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

📘 **作用：**

* `id="root"` 是 React 渲染的挂载点；
* `<script type="module">` 由 **Vite** 处理并加载；
* 本文件不直接显示内容，所有页面内容由 React 渲染。

🧠 类比：

> 它是一个“空画布”，React 负责在上面绘制所有页面。

✅ **必需。**

---

### 2️⃣ `src/main.tsx` —— React 应用启动文件 🚀

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

📘 **作用：**

* 找到 `index.html` 的 `<div id="root">`；
* 将 React 应用（`App.tsx`）渲染进去；
* 加载全局样式 `index.css`。

🧠 类比：

> 它是“引擎启动器”，
> 负责让整个前端程序在浏览器中运行。


---

### 3️⃣ `src/App.tsx` —— 应用主组件 ⚙️

```tsx
import React from "react";
import "./App.css";
import Main from "./pages/Main/Main";

function App() {
  return (
    <div className="App">
      <Main />
    </div>
  );
}

export default App;
```

📘 **作用：**

* React 应用的根组件；
* 定义整个应用的页面框架；
* 一般包含 Header、Sidebar、MainPage 等大区块。

🧠 **理解：**

> App 是“系统外壳”，
> 负责组织所有页面（pages）和组件（components）。


---

### 4️⃣ `src/pages/` —— 页面模块 📄

每个文件夹对应一个独立页面，比如：

```
pages/
 ├── Main/          → 主界面：数据表格 + 图表交互
 ├── Login/         → 登录页（可选）
 └── About/         → 关于页（可选）
```

📘 **作用：**

* 负责页面整体逻辑；
* 通过组件组合形成完整功能区；
* 处理用户交互（如按钮点击、表格修改）；
* 使用 `fetch()` 与 Flask 后端通信。

示例（`Main.tsx`）：

```tsx
import UploadComponent from '../../components/Upload/UploadComponent';
import Graph from '../../components/Graph/Graph';
import DataProcess from '../../components/DataProcess/DataProcess';

const Main = () => {
  return (
    <>
      <UploadComponent />
      <DataProcess />
      <Graph />
    </>
  );
};
```

🧠 **类比：**

> “页面层” 就是用户能看到和操作的那一整页，
> 而里面的小模块都是 “组件”。

✅ **项目主体模块。**

---

### 5️⃣ `src/components/` —— 通用组件层 🧩

📘 **作用：**

* 存放可复用的界面模块（UI 组件 + 功能组件）；
* 每个组件独立一组文件（`.tsx` + `.css`）；
* 可在多个页面中引入使用。

#### 示例结构：

```
components/
 ├── UploadComponent/      → 文件上传区
 ├── Graph/                → 图表展示区
 ├── DataProcess/          → 数据处理交互区
 └── ComparePool/          → 模型选择区
```

#### 示例（DataProcess.tsx）：

```tsx
const submit = async () => {
  const formData = new FormData();
  formData.append("inputValue", inputValue);
  formData.append("sheetData", JSON.stringify(sheetData));

  const response = await fetch("http://localhost:8000/api/dataprocess", {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  console.log("后端返回：", result);
};
```

🧠 **理解：**

> “组件层”是项目的积木工厂，
> 每个组件负责一项功能，组合起来形成完整页面。

✅ **核心层（与 pages 并列）。**



---

### 6️⃣ `vite.config.ts` —— Vite 构建与代理配置 ⚡

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

📘 **作用：**

* 控制 Vite 运行端口；
* 配置前后端代理（解决跨域问题）；
* 插件注册（React 支持、热更新等）。

🧠 **理解：**

> 就像项目的“交通指挥员”，
> 告诉浏览器哪些请求要交给 Flask 处理。

✅ **必需（前后端联调时非常关键）。**

---

### 7️⃣ `package.json` —— 依赖与脚本管理 📦

记录项目依赖和运行命令：

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "antd": "^5.9.0",
    "@fortune-sheet/react": "^1.4.0"
  }
}
```

📘 **作用：**

* 管理项目依赖；
* 定义启动命令；
* 记录框架版本（React、AntD、FortuneSheet 等）。

✅ **必需。**

---

## 🧠 三、最小可运行结构（推荐教学版）

```plaintext
front/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── UploadComponent/
│   │   ├── Graph/
│   │   └── DataProcess/
│   ├── pages/
│   │   └── Main/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   └── vite-env.d.ts
├── index.html
├── vite.config.ts
└── package.json
```

✅ 这是前端部分的“最小可运行骨架”，启动命令为：

```bash
yarn install
yarn dev
```

默认端口：**[http://localhost:5173](http://localhost:5173)**

---

## 🔗 四、前后端联动结构图（可放论文或展示PPT）

```
React (Vite前端)
   ↓ fetch()
Flask 路由层 (routes)
   ↓
业务逻辑层 (services)
   ↓
数据库 / 工具函数 (models & utils)
   ↓
返回 JSON → React 渲染页面
```

---

## ✅ 五、一句话总结

> 🧠 **React 负责界面与交互**，
> ⚙️ **Vite 负责编译与热更新**，
> 🌐 **fetch + RESTful API 实现前后端通信**。
>
> 页面由 `pages` 组织，组件由 `components` 复用，
> 构成一个高内聚、低耦合的现代前端架构。

---


# 🚀 项目介绍：基于 Vite + React 的前端框架

本项目基于 **Vite + React** 搭建，结构清晰、模块化程度高，适合教学演示和前后端分离开发。

---
## ⚙️ 前端部分说明（Vite + React ）

前端使用 **Vite** 作为开发与构建工具，结合 **React** 实现页面交互与逻辑控制。

- **Vite**：负责开发环境的快速启动与构建优化；
- **React**：实现页面组件化、数据驱动渲染；


## 🧱 一、项目启动结构概览

```plaintext
index.html
 ├── <div id="root"></div>         → 提供一个空白容器，是 React 应用的“挂载点”
 └── <script type="module" src="./src/main.tsx">
         → 指定浏览器（通过 Vite）加载入口模块
      ↓
main.tsx
 └── 启动 React 应用，并将 App.tsx 挂载到 #root
      ↓
App.tsx
 ├── Header.tsx      → 顶部组件
 ├── Graph.tsx       → 图表展示组件
 ├── Footer.tsx      → 底部信息组件
 └── ...             → 其他页面模块
````

> 从结构上看：
> `index.html` 是网页入口，
> `main.tsx` 是启动引擎，
> `App.tsx` 是应用主体。

---

## ⚙️ 二、Vite 是什么？它在做什么？

### 1️⃣ Vite 的角色

Vite 是一个**前端开发服务器和构建工具**，它的主要功能是：

| 功能          | 说明                                          |
| ----------- | ------------------------------------------- |
| **快速启动**    | 利用 ES 模块 (ESM) 支持，几乎“秒开”开发环境。               |
| **即时编译**    | 使用 ESBuild 将 TypeScript / JSX 转为浏览器可执行的 JS。 |
| **依赖预构建**   | 对第三方依赖（如 React）进行优化缓存，加快加载速度。               |
| **热更新 HMR** | 修改代码后自动刷新页面，立即看到效果。                         |

---

### 2️⃣ Vite 的加载流程

当浏览器访问项目时（例如运行 `npm run dev`）：

```
index.html
   ↓
<script type="module" src="./src/main.tsx">
   ↓
Vite 截获对 main.tsx 的请求
   ↓
将 TypeScript / JSX 实时编译为 JavaScript
   ↓
浏览器加载并执行生成的代码
```

📘 这意味着：

浏览器并不会直接执行 `.tsx` 文件，而是执行由 **Vite 编译后的 JavaScript 模块**。  
Vite 并不会事先打包整个项目，而是“按需加载、即时编译”。  
修改文件后，Vite 只重新编译变化的模块并通过 HMR 推送到浏览器。  

---

### 3️⃣ 💡 小结

> **Vite 是网页的“中控系统”**
> 它负责：
>
> * 模块加载、热更新与依赖编译；
> * 路径解析与依赖管理；
> * 保证系统界面实时更新与调试支持。
> * 作为React+TypeScript的构建工具

---

## ⚛️ 三、React 的作用与运行机制

### 1️⃣ React 的核心思想

React 的核心是 **组件化（Component）**。
它将网页拆分成一个个可复用的功能模块，比如头部、导航栏、图表、底部等。

每个组件：

* 拥有自己的结构（HTML）；
* 拥有自己的样式（CSS）；
* 拥有自己的逻辑（JS/TS）。

  📘 React 做的事是：

* 触发事件（比如点击按钮）；
* 发送网络请求；
* 收到后端返回的数据；
* 更新 state；
* 触发页面重新渲染。

整个过程可以理解为：
```
用户操作 → React 发请求 → Flask 返回数据 → React 更新页面
```

---

### 2️⃣ React 是如何启动的

在 `main.tsx` 中：

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
)
```

📍 运行机制如下：

1. `createRoot()` 找到 `index.html` 的 `<div id="root">`；
2. React 在此节点上创建“虚拟 DOM 根节点”；
3. `<App />` 根组件开始渲染；
4. 页面根据组件结构层层生成；

---

### 3️⃣ React 渲染示意

```
index.html  →  main.tsx  →  App.tsx
                              ↓
                    Header / Graph / Footer ...
```

React 使用 **虚拟 DOM** 比较新旧状态，
只更新变化的部分，避免整页刷新，保证性能。

---

## 🧩 四、两者如何协作

| 阶段        | 执行者                  | 作用                     |
| --------- | -------------------- | ---------------------- |
| **加载阶段**  | `index.html`         | 提供容器和入口脚本              |
| **编译阶段**  | **Vite**             | 动态编译 TS/JSX 模块，交给浏览器执行 |
| **执行阶段**  | `main.tsx`           | 启动 React，挂载应用          |
| **渲染阶段**  | **React**            | 构建虚拟 DOM，渲染 App 及子组件   |
| **热更新阶段** | **Vite + React HMR** | 修改代码后即时更新，无需刷新页面       |

---

## 💬 五、整体运行流程图

```
index.html
   ↓
浏览器请求 main.tsx
   ↓
Vite 实时编译 TypeScript → JavaScript
   ↓
浏览器执行 main.tsx
   ↓
React 启动并挂载 App.tsx
   ↓
App 组织 Header / Graph / Footer 等组件
   ↓
网页内容渲染完成
```

---

## ✅ 六、一句话总结

> 🧠 **Vite 负责加载、编译与调试**，
> ⚛️ **React 负责渲染页面与交互逻辑**。
>
> 它们协作完成了一个从文件 → 模块 → 页面 → 交互的完整网页构建与运行流程。

---

## 📘 七、延伸阅读建议

* [Vite 官方文档](https://vitejs.dev/)
* [React 官方文档](https://react.dev/)
* [React Router 文档](https://reactrouter.com/en/main)


---

---


# 🚀 项目介绍：基于 Flask 的后端框架

本项目后端基于 **Flask** 搭建，采用模块化蓝图（Blueprint）与应用工厂模式（Application Factory）设计，
结合 **Flask-CORS**、**Flask-SQLAlchemy** 等扩展，实现了接口管理、数据库交互与跨域通信等核心功能。

后端与前端（Vite + React + TypeScript）通过 **RESTful API** 进行数据交互，
整体结构清晰、可扩展性强，是一个标准的前后端分离式 Web 应用。

---

## ⚙️ 后端部分说明（Flask + MySQL）

后端主要功能包括：

* **Flask**：提供 Web 服务框架与路由系统；
* **Flask-CORS**：解决跨域访问问题，允许前端调用接口；
* **Flask-SQLAlchemy**：通过 ORM 管理数据库；
* **Blueprint（蓝图）**：实现多模块结构；
* **工厂模式（create_app）**：灵活加载配置与初始化模块。

Flask 的职责是：

> 监听来自前端的请求 → 调用业务逻辑（如文件上传、图表生成、数据处理） → 返回 JSON 响应。

---

## 🧱 一、项目启动结构概览

```plaintext
run.py
 ├── from app import create_app       → 调用工厂函数创建 Flask 应用实例
 ├── app.run(port=8000, debug=True)   → 启动后端服务
      ↓
app/
 ├── __init__.py                      → 核心配置与模块注册（数据库、蓝图、CORS）
 ├── routes/                          → 路由模块（auth, upload, dataprocess, chart, template）
 ├── models.py                        → 定义数据库模型（UserTable, ChartTemplate, HistoryChart 等）
 ├── utils/                           → 工具与格式转换函数
 ├── services/                        → 数据处理与图表生成逻辑
 └── config.py                        → MySQL 数据库与全局配置文件
```

📘 从结构上看：

* `run.py` 是程序入口；
* `app/__init__.py` 是应用核心，负责初始化 Flask、注册数据库和路由；
* `routes/` 文件夹中包含每个业务模块的蓝图；
* `models.py` 定义数据库表结构；
* `services/` 实现复杂的数据计算与图表生成。

---

## ⚙️ 二、Flask 是什么？它在做什么？

### 1️⃣ Flask 的角色

Flask 是一个 **轻量级 Web 应用框架（Web Application Framework）**，
它为开发者提供了一整套构建 Web 服务的基本机制。

| 功能       | 说明                                           |
| -------- | -------------------------------------------- |
| **路由管理** | 通过 `@app.route()` 或 `Blueprint` 管理 URL 与函数映射 |
| **请求处理** | 解析前端发送的 HTTP 请求（GET、POST 等）                  |
| **响应生成** | 返回计算结果或数据库数据（以 JSON 格式）                      |
| **模板渲染** | 可选，用于后台 HTML 页面                              |
| **扩展机制** | 提供插件式模块，如数据库、CORS、日志等                        |

---

### 2️⃣ Flask 的运行流程

当执行命令：

```
python run.py
```

程序运行流程如下：

```
run.py
   ↓
from app import create_app
   ↓
create_app() 初始化 Flask 实例
   ↓
加载配置（config.py）并注册 CORS 与数据库
   ↓
注册蓝图模块（upload, dataprocess, chart, template）
   ↓
启动 Web 服务器（http://localhost:8000）
```

📘 这意味着：

> Flask 在后端扮演“中控系统”的角色，
> 负责接收前端请求 → 调用相应业务函数 → 与数据库交互 → 返回结果。

---

## 🧩 三、核心技术模块

| 功能        | Flask 提供的机制           | 在本项目中的体现                            |
| --------- | --------------------- | ----------------------------------- |
| **路由管理**  | `Blueprint`           | 在 `/app/routes/` 中为上传、图表、模板等功能分别建蓝图 |
| **请求响应**  | `request`、`jsonify()` | 接收前端表单、返回 JSON 数据                   |
| **数据库操作** | `Flask-SQLAlchemy`    | 管理用户、图表、模板、收藏等表                     |
| **跨域通信**  | `Flask-CORS`          | 允许 React 前端访问 Flask 接口              |
| **工厂模式**  | `create_app()`        | 动态创建应用并注册各模块                        |

---

## ⚙️ 四、工厂模式（Application Factory）

主文件：`app/__init__.py`

```python
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    # ① 创建 Flask 应用实例
    app = Flask(__name__)

    # ② 启用跨域支持（前后端分离通信需要）
    CORS(app, supports_credentials=True)

    # ③ 加载配置文件
    app.config.from_pyfile('../config.py')

    # ④ 初始化数据库（绑定到当前 app）
    db.init_app(app)

    # ⑤ 导入并注册各功能模块（蓝图）
    from .routes import upload, dataprocess, chart, template
    app.register_blueprint(upload.bp)
    app.register_blueprint(dataprocess.bp)
    app.register_blueprint(chart.bp)
    app.register_blueprint(template.bp)

    # ⑥ 返回完整的应用实例
    return app
```

---


### 🧠 一、什么是“工厂模式”？

在 Flask 中，“**应用工厂（Application Factory）**”是一种非常常见的项目结构模式。
它的核心思想是：**用一个函数来创建并返回 Flask 应用实例，而不是直接定义一个全局 app 对象。**

传统写法（简单项目）通常是：

```python
app = Flask(__name__)
```

而你的项目采用的是：

```python
def create_app():
    app = Flask(__name__)
    ...
    return app
```

📘 **优势：**

| 特点           | 说明                                           |
| ------------ | -------------------------------------------- |
| **模块化与解耦**   | 不同功能（数据库、蓝图、配置）在函数内按需注册，互不干扰。                |
| **可复用性高**    | 测试环境、开发环境可分别创建不同配置的 app 实例。                  |
| **避免循环导入**   | 各模块只在函数内部导入，解决 Flask 项目中最常见的 ImportError 问题。 |
| **符合大型项目结构** | 方便集成多数据库、后台任务、权限验证等复杂逻辑。                     |

---

### ⚙️ 二、`create_app()` 的运行流程详解

当执行 `python run.py` 时：

```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(port=8000, debug=True)
```

🔽 整个调用过程如下：

1️⃣ **加载配置阶段**
`create_app()` 创建 Flask 实例，并从 `config.py` 读取数据库配置，例如：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/visual_db'
```

2️⃣ **初始化扩展阶段**
调用：

```python
db.init_app(app)
CORS(app, supports_credentials=True)
```

完成数据库连接与跨域设置。
这一步让数据库和跨域控制与 Flask 应用绑定在一起。

3️⃣ **注册蓝图阶段**
依次导入各业务模块并注册路由：

```python
app.register_blueprint(upload.bp)
app.register_blueprint(dataprocess.bp)
app.register_blueprint(chart.bp)
app.register_blueprint(template.bp)
```

每个蓝图（Blueprint）负责一个功能域，比如：

* `/api/upload` → 文件上传；
* `/api/dataprocess` → 数据处理；
* `/api/chart` → 图表生成；
* `/api/templates` → 模板查询与新增。

这样 Flask 主应用只负责调度，各模块独立运行、互不干扰。

4️⃣ **返回阶段**
工厂函数返回完整的 Flask 实例，交给 `run.py` 启动开发服务器。

---

### 🧩 三、应用启动流程图

```
run.py
   ↓
from app import create_app
   ↓
create_app() 被调用
   ↓
初始化 Flask 实例
   ↓
加载 config.py 配置
   ↓
绑定数据库 SQLAlchemy
   ↓
启用跨域 CORS
   ↓
注册蓝图模块（upload, dataprocess, chart, template）
   ↓
返回 app 实例
   ↓
app.run(port=8000)
```

📘 **总结一句话：**

> 工厂模式就像一个“项目启动引擎”，
> 把 Flask 应用的每个组件（配置、数据库、蓝图、跨域）
> 组装成一个可运行的完整后端系统。

---

### 💡 四、为什么该项目必须用工厂模式？

因为你的项目是一个典型的**前后端分离 + 多模块 Flask 系统**，
如果使用传统单文件结构（直接写 `app = Flask(__name__)`），会出现以下问题：

* 各个蓝图模块导入时出现循环依赖；
* 数据库初始化与 app 不同步；
* 无法在不同环境（测试/部署）灵活切换配置；
* 不易扩展后续功能（如日志、身份认证）。

工厂模式完美解决了这些问题，让系统：

> 结构更清晰、组件更独立、协作更稳定。

---

### ✅ 五、一句话总结

> 在本系统中，`create_app()` 是整个 Flask 后端的启动核心。
> 它像一个“装配车间”，负责创建 Flask 实例、注册蓝图模块、连接数据库、配置跨域访问。
> 最终由 `run.py` 启动运行，实现前端请求与后端服务的衔接。


---

## ⚙️ 五、蓝图机制（Blueprint）

Flask 蓝图用于拆分业务逻辑，提升项目可维护性。
在你的项目中，每个功能（上传、数据处理、图表生成、模板管理）都是一个独立的蓝图模块。

### 示例 1：文件上传（upload.py）

```python
bp = Blueprint('upload', __name__)

@bp.route('/api/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        return df_to_celldata(df)
    else:
        return jsonify({"error": "未检测到有效上传内容"}), 400
```

📘 **功能说明：**

* 接收前端上传的文件；
* 利用 Pandas 将文件转换为 DataFrame；
* 通过 `df_to_celldata()` 返回 JSON，供前端展示。


---

### 示例 3：图表生成（chart.py）

```python
bp = Blueprint('chart', __name__)

@bp.route('/api/chart', methods=['POST'])
def generate_plot():
    data = request.form.get("data")
    chart_type = request.form.get("type")
    color = request.form.get("color")
    img_base64, code = generate_graph(data, chart_type, color)
    return jsonify({"img_base64": img_base64, "code": code})
```

📘 **功能说明：**
根据用户选择的图表类型与配色参数，调用绘图模块生成图像（Base64 格式）并返回。


---

## ⚙️ 六、数据库模型（Flask-SQLAlchemy）

数据库文件：`app/models.py`

```python
class UserTable(db.Model):
    __tablename__ = 'User_table'
    User_ID = db.Column(db.Integer, primary_key=True)
    User_name = db.Column(db.String(50), nullable=False)
    User_phone = db.Column(db.String(20), unique=True, nullable=False)
    User_level = db.Column(db.String(20), default='普通用户')
    User_credit = db.Column(db.Integer, default=999)
```

示例操作：

```python
# 插入新用户
new_user = UserTable(User_name='Alice', User_phone='13800138000', User_password='123456')
db.session.add(new_user)
db.session.commit()

# 查询模板
templates = ChartTemplate.query.filter_by(Chart_type='bar').all()
```

📘 **说明：**

Flask-SQLAlchemy 提供了面向对象的数据库操作方式：
不必编写 SQL，而是通过 Python 类的属性和方法进行查询与更新。

---

## ⚙️ 七、跨域通信（CORS）

由于前端运行在 Vite 默认端口（5173），后端在 Flask（8000），浏览器会触发跨域限制。
Flask-CORS 扩展通过一行代码解决：

```python
CORS(app, supports_credentials=True)
```

允许前端发送跨域请求，并携带 Cookie 或身份凭证。

---

## 💬 八、整体运行流程图

```
run.py 启动 Flask
   ↓
create_app() 创建应用实例
   ↓
注册蓝图与数据库模块
   ↓
Flask 监听来自前端的请求
   ↓
React + Vite 前端发送 HTTP 请求（/api/upload 等）
   ↓
Flask 蓝图路由处理逻辑
   ↓
数据库交互（SQLAlchemy）
   ↓
返回 JSON 响应给前端
```


---

## ✅ 九、一句话总结

> 🧠 **Flask 负责后端逻辑与数据交互**，
> ⚙️ **SQLAlchemy 管理数据库模型与数据存储**，
> 🌐 **CORS 实现前后端通信**。

Flask 框架通过模块化蓝图、ORM 映射与灵活配置，
支撑起了整个数据可视化系统的后端运行逻辑。

---

## 📘 十、延伸阅读建议

* [Flask 官方文档](https://flask.palletsprojects.com/)
* [Flask-SQLAlchemy 官方文档](https://flask-sqlalchemy.palletsprojects.com/)
* [Flask-CORS 官方文档](https://flask-cors.readthedocs.io/)
* [Blueprint 模块化设计指南](https://flask.palletsprojects.com/en/latest/blueprints/)

---


---

# 🚀 项目介绍：前后端通信

本项目采用 **Vite + React + TypeScript + Flask** 的前后端分离架构。
前端负责页面渲染与用户交互，后端负责数据处理与接口响应。
两者通过 **RESTful API** 与 **HTTP 请求（fetch）** 完成通信，实现了从数据上传、处理到图表生成的完整流程。

---

## ⚙️ 一、整体通信结构概览

```
React (Vite 前端)
   ↓ 发送 fetch() 请求
Flask (Python 后端)
   ↓ 蓝图 Blueprint 匹配路由
   ↓ 调用对应功能模块（upload / dataprocess / chart / template）
   ↓ jsonify() 返回 JSON 数据
React
   ↓ 解析响应，更新页面显示
```

> 📘 前后端之间通过网络协议（HTTP）通信。
> 前端用 `fetch()` 发送请求，Flask 用 `request` 接收数据，再用 `jsonify()` 返回结果。

---

## 🧩 二、RESTful API 通信机制

项目后端采用 **RESTful API** 风格，即“每个功能对应一个固定的接口地址（URL）”，前端通过请求不同的 URL 来访问资源。

| 模块功能 | 接口 URL             | 请求方式       | 返回类型 | 功能说明               |
| ---- | ------------------ | ---------- | ---- | ------------------ |
| 文件上传 | `/api/upload`      | POST       | JSON | 上传 Excel、CSV、图片等文件 |
| 数据处理 | `/api/dataprocess` | POST       | JSON | 进行表格清洗、筛选、统计分析     |
| 图表生成 | `/api/chart`       | POST       | JSON | 根据表格数据生成图表         |
| 模板管理 | `/api/templates`   | GET / POST | JSON | 查询或新增图表模板          |

📘 每个接口都在 Flask 的蓝图中实现，保持结构清晰、模块独立。

---

## ⚛️ 三、前端发送请求（以 DataProcess 为例）

在 `src/components/DataProcess/DataProcess.tsx` 中，用户点击“发送”后，会通过 `fetch()` 将输入指令和表格数据发送到 Flask：

```tsx
const formData = new FormData();
formData.append("inputValue", inputValue);
formData.append("selectedModel", selectedModel);
formData.append("sheetData", JSON.stringify(sheetData));

const response = await fetch("http://localhost:8000/api/dataprocess", {
  method: "POST",
  body: formData,
});
```

> ⚙️ `fetch()` 是浏览器内置的 HTTP 请求函数，
> 这里向 Flask 的 `/api/dataprocess` 接口发起了一个 POST 请求。

---

## 🧠 四、后端接收与处理（Flask Blueprint）

Flask 在 `app/routes/dataprocess.py` 中定义对应接口：

```python
@bp.route('/api/dataprocess', methods=['POST'])
def dataprocess():
    form = request.form
    input_value = form.get("inputValue")
    selected_model = form.get("selectedModel")
    sheet_data_str = form.get("sheetData")

    result = get_processed_data(input_value, selected_model, sheet_data_str)
    if not result.empty:
        return df_to_celldata(result)
    else:
        return jsonify({"error": "未检测到有效上传内容"}), 400
```

📘 **处理流程说明：**

1️⃣ 接收前端发送的表单数据（`request.form`）
2️⃣ 调用数据处理函数 `get_processed_data()`
3️⃣ 将 Pandas 结果表转换成 JSON 格式
4️⃣ 通过 `jsonify()` 将结果返回给前端

---

## 🔄 五、前端接收响应并更新界面

收到 Flask 的 JSON 响应后，前端更新可视化表格：

```tsx
const result = await response.json();

ref.current?.updateSheet([
  {
    id: "2",
    name: "处理数据",
    celldata: result?.celldata,
    order: 0,
  },
]);
```

📘 前端利用 FortuneSheet 组件渲染返回的数据，实现即时的表格刷新。

---

## 🌍 六、跨域访问（CORS）

因为前端在 `localhost:5173`，后端在 `localhost:8000`，
两者端口不同，浏览器默认禁止跨域访问。
项目通过 `Flask-CORS` 实现跨域支持：

```python
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    ...
```

📘 **作用说明：**

* 允许前端访问后端接口；
* 支持携带登录凭证；
* 解决跨端口通信问题。

---

## 🧾 七、完整通信流程示例（以数据处理模块为例）

```
① 用户在 React 前端输入数据处理指令
② DataProcess.tsx 将指令 + 表格数据封装为 FormData
③ fetch("http://localhost:8000/api/dataprocess") 发出 POST 请求
④ Flask 蓝图 dataprocess.py 接收数据
⑤ 调用 get_processed_data() 完成分析
⑥ jsonify() 返回 JSON 响应
⑦ React 前端接收 JSON 并更新 Workbook 页面
```

---

## 🧭 八、通信验证与调试方法

### ✅ 浏览器端：

1. 打开前端页面；
2. 按下 **F12 → Network 面板**；
3. 观察到：

   ```
   POST http://localhost:8000/api/dataprocess
   ```

   * 请求方式：POST
   * Initiator：fetch
   * 状态码：200
   * 响应内容：JSON（celldata）

### ✅ 后端控制台：

```
127.0.0.1 - - [31/Oct/2025 16:28:41] "POST /api/dataprocess HTTP/1.1" 200 -
```

表示请求已被 Flask 接收并成功处理。

---

## ✅ 九、一句话总结

> 🧠 **React 前端** 用 `fetch()` 发请求；
> ⚙️ **Flask 后端** 通过 `request` 接收并 `jsonify()` 返回结果；
> 🌐 **CORS** 确保跨域访问正常；
> 💡 形成了从用户输入 → 数据上传 → 后端处理 → 页面更新的完整通信闭环。

---





这是一个项目的READM文件，请你先详细地阅读，再仔细地为我讲解全部内容