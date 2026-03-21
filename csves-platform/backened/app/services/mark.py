#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate_api_responses.py
-----------------------------------------
从500问题Excel随机抽5个 -> 调用各大模型API生成回答 -> 用训练好的Qwen_model.pt评分
-----------------------------------------
"""

import os
import random
import torch
import numpy as np
import pandas as pd
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# ========== 配置 ==========
QUESTION_FILE = "/data/hlt/A-visual/mark/500_question_answer.xlsx"
MODEL_PATH = "/data/hlt/A-visual/mark/Qwen_model.pt"
BASE_MODEL = "/data/hlt/A-visual/mark/Qwen/Qwen/Qwen2.5-0.5B-Instruct"

os.environ["DEEPSEEK_API_KEY"] = "sk-71308322ca5748aaa2d1d935861a3e93"

# 可配置大模型名称
API_MODELS = {
    # "GPT4-o": {"provider": "openai", "model": "gpt-4o"},
    "DeepSeek": {"provider": "deepseek", "model": "deepseek-chat"},
    # "Claude3": {"provider": "anthropic", "model": "claude-3-opus-20240229"},
    # "Qwen": {"provider": "dashscope", "model": "qwen-plus"},   # 可选扩展
    # "GLM": {"provider": "zhipu", "model": "glm-4-air"},       # 可选扩展
}

NUM_LABELS = 12
MAX_LEN = 512

# ========== 初始化评分模型 ==========
def load_scoring_model():
    print("加载评分模型中 ...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=NUM_LABELS, problem_type="multi_label_classification"
    )

    # 修复Qwen pad_token问题
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.pad_token_id

    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    if any(k.startswith("module.") for k in state_dict.keys()):
        state_dict = {k.replace("module.", "", 1): v for k, v in state_dict.items()}
    model.load_state_dict(state_dict, strict=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print("✅ 评分模型加载完成")
    return tokenizer, model, device


# ========== 随机抽取问题 ==========
def get_random_questions(n=5):
    df = pd.read_excel(QUESTION_FILE)
    text_col = next(
        (c for c in df.columns if any(k in c.lower() for k in ["问题"])), None
    )
     # 如果找不到，就默认第一列为问题列
    if text_col is None:
        text_col = df.columns[0]
    samples = df.sample(n)
    return samples[text_col].tolist()


# ========== 调用不同模型API生成回答 ==========
def query_api(model_name, prompt):
    """支持多API的统一调用"""
    info = API_MODELS[model_name]
    provider, model = info["provider"], info["model"]

    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    elif provider == "deepseek":
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    elif provider == "anthropic":
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(model=model, max_tokens=500, messages=[{"role": "user", "content": prompt}])
        return resp.content[0].text.strip()

    else:
        raise ValueError(f"未知模型类型: {model_name}")


# ========== 用训练好的Qwen评分 ==========
def score_answer(tokenizer, model, device, text):
    inputs = tokenizer(text, truncation=True, max_length=MAX_LEN, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
    return probs  # shape=(12,)


# ========== 主函数 ==========
def main():
    tokenizer, model, device = load_scoring_model()
    questions = get_random_questions(n=5)

    results = []
    for q in questions:
        print(f"\n🧩 问题：{q}")
        answers = {}
        for name in API_MODELS:
            try:
                ans = query_api(name, q)
                print(f"  {name} 回答: {ans[:80]}...")
                score = score_answer(tokenizer, model, device, ans)
                answers[name] = {"answer": ans, "scores": score.tolist()}
            except Exception as e:
                print(f"  ❌ {name} 生成失败: {e}")
                answers[name] = {"answer": None, "scores": None}
        results.append({"question": q, "answers": answers})

    # 保存结果
    import json
    out_path = "/data/hlt/A-visual/mark/api_eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存所有结果到 {out_path}")


if __name__ == "__main__":
    main()
