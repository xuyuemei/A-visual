import os

# 数据库配置
SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://root:123456@localhost:3306/bs_db?charset=utf8mb4"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)

# OpenAI API配置 (用于视频分析)
ZZZ_BASE_URL = os.getenv("ZZZ_BASE_URL", "https://api.zhizengzeng.com/v1")
ZZZ_API_KEY = os.getenv("ZZZ_API_KEY", "sk-zk237a38360c4056d5097a3b10879eeb35a6914611803eeb")
