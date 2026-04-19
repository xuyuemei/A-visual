# C-Voices 

一个“多模态价值观智能评测平台”，主要是面向文本、图像、视频与模型问答等多场景输入，支持对大语言模型输出内容在12个社会主义核心价值观维度上的量化评估与可视化分析

平台主要功能：
- 模型价值观评测与对比：支持多模型并行评测与结果对照
- 文本价值观评测：对用户输入文本图片等进行自动分析与评分
- 视频价值观评测：对视频内容进行结构化分析与指标输出

项目主要能力：
- 表格/文本/图片/视频等数据处理与分析
- 基于 Flask 提供 API 服务
- 基于 React + Vite 提供交互界面
- 支持模型评估、文本评分、文档解析等功能接口

## 项目结构

```text
.
├── csves-platform/
│   ├── backened/                # Flask 后端
│   │   ├── run.py               # 后端启动入口
│   │   ├── config.py            # 后端配置（数据库、API 等）
│   │   └── app/
│   │       ├── __init__.py      # Flask 工厂与蓝图注册
│   │       ├── routes/          # 路由层
│   │       ├── services/        # 业务逻辑层
│   │       └── requirements.txt # Python 依赖
│   └── front_work/
│       └── front/               # React + Vite 前端
└── README.md
```

## 环境要求

- Python 3.10（建议）
- Node.js 18+（建议）
- MySQL 8.0（建议）

## 1. 后端环境配置

进入后端目录：

```bash
cd csves-platform/backened
```

创建并激活虚拟环境（任选一种）：

```bash
# conda
conda create -n visual python=3.10 -y
conda activate visual

# 或 venv
python -m venv .venv
source .venv/bin/activate
```

安装 Python 依赖：

```bash
pip install -r app/requirements.txt
pip install Flask-SQLAlchemy PyMySQL
```

> 说明：当前 requirements 文件中未固定 Flask-SQLAlchemy 与 PyMySQL，建议按上面命令补装。

## 2. 数据库配置

编辑 csves-platform/backened/config.py，至少确认以下配置：

- SQLALCHEMY_DATABASE_URI
- SQLALCHEMY_TRACK_MODIFICATIONS
- SECRET_KEY

示例（按你的本地环境修改）：

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:密码@localhost:3306/bs_db?charset=utf8mb4"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## 3. 前端环境配置

进入前端目录：

```bash
cd csves-platform/front_work/front
```

安装依赖并启动：

```bash
npm install
npm run dev
```

## 4. 启动项目

先启动后端：

```bash
cd csves-platform/backened
python run.py
```

再启动前端：

```bash
cd csves-platform/front_work/front
npm run dev
```

默认访问地址：
- 前端：http://localhost:5173
- 后端：http://localhost:8000

## 常见问题

### 1) Port 8000 is in use

说明 8000 端口被占用，先释放端口再启动后端：

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
