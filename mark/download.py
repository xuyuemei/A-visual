import torch
from modelscope import Model, AutoTokenizer, AutoModelForCausalLM
import argparse
# 模型下载
from modelscope import snapshot_download
import os
import re
import json
import csv
import itertools

model_dir = snapshot_download('Qwen/Qwen2.5-0.5B-Instruct', cache_dir='/data/hlt/A-visual/mark/Qwen')
# model_dir = '/data/hl/Multi-LLM/LLMs/llama3-8b/LLama3-8b'
model = AutoModelForCausalLM.from_pretrained(model_dir, device_map='auto', torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(model_dir)
print("Loaded model")
# print(model)



prompt = f"""The English word university in Chinese is:"""
device = model.device
inputs = tokenizer(prompt, return_tensors="pt").to(device)
logits = model.generate(inputs.input_ids, attention_mask=inputs.attention_mask, num_beams=4,
                        max_new_tokens=10, pad_token_id=tokenizer.eos_token_id, early_stopping=True)
out = tokenizer.decode(logits[0].tolist(), skip_special_tokens=True)
print(out)