# C-Voices A-visual

一个前后端分离的可视化与智能分析平台。

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

```bash
fuser -k 8000/tcp
```

### 2) 数据库连接失败

请检查：
- MySQL 服务是否启动
- config.py 里的账号、密码、库名是否正确
- 本机是否有对应数据库和权限

## 模型文件说明

为保证仓库体积可控并提升克隆、拉取与持续集成效率，以下大体积模型文件未纳入 GitHub 仓库：

- mark/Qwen/
- mark/Qwen_model.pt

上述文件属于可选运行资源，不影响项目代码结构与核心功能说明的阅读。

如需在本地启用相关模型能力，请根据团队内部提供的模型分发方式（如制品库、对象存储或共享盘）获取文件，并放置到对应目录后再启动相关功能。


