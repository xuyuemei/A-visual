from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch
import json
import time
import os


def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


model_name = "meta-llama/CodeLlama-13b-Instruct-hf"

# 使用 bitsandbytes 加载 4bit 模型配置
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = "<PAD>"  # 避免警告

# 加载原始模型（4bit + 自动 device_map）
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# 不要调用 .resize_token_embeddings()

# 加载 SFT 微调 LoRA 权重
sft_model_id = "./checkpoint/cli-meta-13b-sft-task1-lora16-epoch5/final"
sft_model = PeftModel.from_pretrained(
    model,
    sft_model_id,
    device_map="auto",
    offload_folder="lora_results/lora_sft"
)

# 加载 RL 微调 LoRA 权重
rl_model_id = "policy1-joint-pref-v3-2k-random-data-step94"
rl_model = PeftModel.from_pretrained(
    sft_model,
    f"./checkpoint/{rl_model_id}/",
    device_map="auto",
    offload_folder="lora_results/lora_rl"
)

with open("test.json", "r", encoding="utf-8") as file:
    test_set = json.load(file)

dataset = []
total_num = len(test_set)
start = time.time()

def print_elapsed_time(start):
    elapsed = time.time() - start
    print(f"=== Elapsed time: {time.strftime('%H:%M:%S', time.gmtime(elapsed))} ===")

for index, item in enumerate(test_set):
    input_prompt = f"""<s>[INST] <<SYS>>
You are good at generating complete python code from the given chart description.
<</SYS>>

Your task is to generate a complete python code for the given description. Make sure to include all necessary libraries. 

Description:
{item['description']}

Please generate the corresponding code that generates the plot that has the above description. 

[/INST] 
“””Python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
"""

    inputs = tokenizer(input_prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = rl_model.generate(
            input_ids=inputs["input_ids"],
            do_sample=True,
            top_k=10,
            temperature=0.1,
            top_p=0.95,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_new_tokens=1024,
        )

    value = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(value)
    print(f"=== Step: ({index} / {total_num}) ===")
    print_elapsed_time(start)

    dataset.append(
        {
            "id": item["id"],
            "description": item["description"],
            "generated_output": value,
            "code": item["code"],
        }
    )
    save_to_json(dataset, f"output/{rl_model_id}.json")
