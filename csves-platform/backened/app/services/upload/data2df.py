from ...utils.gpt import ask_gpt
import pandas as pd
from ...static.ai_config import *
import json
import re
import ast

def text2df(text):
    text = text.strip()
    prompt = TEXT2DF+text
    # print("Prompt/n",prompt)
    ans=ask_gpt(prompt, "gpt-4o")
    # print("Answer/n",ans)
    match = re.search(r"\{[\s\S]*\}", ans)
    if match:
        dict_str = match.group()
        # 转换为 Python 字典（注意需要保留中文括号和字符串）
        data = ast.literal_eval(dict_str)
        print(data)
        # ans_dict = json.loads(data)
        df = pd.DataFrame(data)
        print(df)
        return df
    else:
        print("未找到有效字典")
        return None

def image2df(image, image_type):
    prompt = IMAGE2DF
    # print("Prompt/n",prompt)
    ans=ask_gpt(prompt, "gpt-4o", image,image_type)   
    print("Answer/n",ans)
    match = re.search(r"\{[\s\S]*\}", ans)
    if match:
        dict_str = match.group()
        # 转换为 Python 字典（注意需要保留中文括号和字符串）
        data = ast.literal_eval(dict_str)
        # print(data)
        # ans_dict = json.loads(data)
        df = pd.DataFrame(data)
        print(df)
        return df
    else:
        print("未找到有效字典")
        return None
