import os
from openai import OpenAI

# 读取智增增 OpenAI 兼容网关配置（不要硬编码密钥）
ZZZ_BASE_URL = os.getenv("ZZZ_BASE_URL", "https://api.zhizengzeng.com/v1")
ZZZ_API_KEY = os.getenv("ZZZ_API_KEY", "sk-zk237a38360c4056d5097a3b10879eeb35a6914611803eeb")

# 统一的模型映射
# 为了不改前端，沿用 "DeepSeek" 作为键，但路由到智增增 provider
API_MODELS = {
    "DeepSeek": {"provider": "zhizengzeng", "model": "deepseek-r1"},
    "GPT-4o": {"provider": "zhizengzeng", "model": "gpt-4o"},
    # 千问系列（通过智增增 OpenAI 兼容网关）
    "Qwen 2.5 7B": {"provider": "zhizengzeng", "model": "qwen2.5-7b-instruct"},
    "Qwen 2.5 32B": {"provider": "zhizengzeng", "model": "qwen2.5-32b-instruct"},
    "Qwen 2.5 72B": {"provider": "zhizengzeng", "model": "qwen2.5-72b-instruct"},
    # 其他模型
    "DeepSeek": {"provider": "zhizengzeng", "model": "deepseek-chat"},
    "Qwen 2.5 7B": {"provider": "zhizengzeng", "model": "qwen2.5-7b-instruct"},
    # 可在此扩展更多模型，例如：
    # "DeepSeek-R1": {"provider": "zhizengzeng", "model": "deepseek-reasoner"},
}


def query_api(model_name, prompt):
    """统一封装不同模型的API调用"""
    info = API_MODELS.get(model_name)
    if not info:
        raise ValueError(f"未知模型: {model_name}")

    provider, model = info["provider"], info["model"]

    if provider == "zhizengzeng":
        if not ZZZ_API_KEY:
            raise RuntimeError("缺少智增增 API 密钥，请在环境变量 ZZZ_API_KEY 中配置")
        client = OpenAI(api_key=ZZZ_API_KEY, base_url=ZZZ_BASE_URL)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    raise ValueError(f"暂不支持的 provider: {provider}")
