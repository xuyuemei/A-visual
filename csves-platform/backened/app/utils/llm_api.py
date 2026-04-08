import os
from openai import OpenAI

# 读取智增增 OpenAI 兼容网关配置（不要硬编码密钥）
ZZZ_BASE_URL = os.getenv("ZZZ_BASE_URL", "https://api.zhizengzeng.com/v1")
ZZZ_API_KEY = os.getenv("ZZZ_API_KEY", "sk-zk237a38360c4056d5097a3b10879eeb35a6914611803eeb")

# 统一的模型映射
API_MODELS = {
    # DeepSeek
    "DeepSeek-Chat": {"provider": "zhizengzeng", "model": "deepseek-chat"},
    "DeepSeek-R1": {"provider": "zhizengzeng", "model": "deepseek-r1"},

    # OpenAI
    "GPT-4o": {"provider": "zhizengzeng", "model": "gpt-4o"},
    "gpt-4.1-mini": {"provider": "zhizengzeng", "model": "gpt-4.1-mini"},

    # Google
    "gemini-2.5-flash": {"provider": "zhizengzeng", "model": "gemini-2.5-flash"},

    # xAI
    "grok-3-mini": {"provider": "zhizengzeng", "model": "grok-3-mini"},

    # Meta
    "llama-3.1-8b-instruct": {
        "provider": "zhizengzeng",
        "model": "llama-3.1-8b-instruct"
    },

    # 字节豆包
    "doubao-seed-2-0-mini-260215": {
        "provider": "zhizengzeng",
        "model": "doubao-seed-2-0-mini-260215"
    },

    # 智谱
    "glm-4.5-air": {"provider": "zhizengzeng", "model": "glm-4.5-air"},

    # 千问
    "Qwen 2.5 7B": {"provider": "zhizengzeng", "model": "qwen2.5-7b-instruct"},
    "Qwen 2.5 32B": {"provider": "zhizengzeng", "model": "qwen2.5-32b-instruct"},
    "Qwen 2.5 72B": {"provider": "zhizengzeng", "model": "qwen2.5-72b-instruct"},
}


def query_api(model_name, prompt):
    """统一封装不同模型的 API 调用"""
    info = API_MODELS.get(model_name)
    if not info:
        raise ValueError(f"未知模型: {model_name}")

    provider = info["provider"]
    model = info["model"]

    if provider == "zhizengzeng":
        if not ZZZ_API_KEY:
            raise RuntimeError("缺少智增增 API 密钥，请在环境变量 ZZZ_API_KEY 中配置")

        client = OpenAI(
            api_key=ZZZ_API_KEY,
            base_url=ZZZ_BASE_URL,
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    raise ValueError(f"暂不支持的 provider: {provider}")