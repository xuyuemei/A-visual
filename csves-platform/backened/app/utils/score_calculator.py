import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_MODEL = "/data/hlt/A-visual/mark/Qwen/Qwen/Qwen2.5-0.5B-Instruct"
MODEL_PATH = "/data/hlt/A-visual/mark/Qwen_model.pt"
NUM_LABELS = 12
MAX_LEN = 512

_tokenizer, _model, _device = None, None, None

def load_scoring_model():
    """加载Qwen评分模型（只加载一次）"""
    global _tokenizer, _model, _device
    if _model is not None:
        return _tokenizer, _model, _device

    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    _model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=NUM_LABELS, problem_type="multi_label_classification"
    )
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token
        _model.config.pad_token_id = _tokenizer.pad_token_id

    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    if any(k.startswith("module.") for k in state_dict.keys()):
        state_dict = {k.replace("module.", "", 1): v for k, v in state_dict.items()}
    _model.load_state_dict(state_dict, strict=False)

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _model.to(_device)
    _model.eval()
    print("✅ Qwen评分模型加载完成")
    return _tokenizer, _model, _device


def score_answer(tokenizer, model, device, text):
    """对文本生成12维度评分"""
    inputs = tokenizer(text, truncation=True, max_length=MAX_LEN, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
    return probs.tolist()
