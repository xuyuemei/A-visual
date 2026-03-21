import pandas as pd
import numpy as np

# ======== 配置 ========
input_file = "2024.1_2024.11.xlsx"   # 你要处理的文件
output_file = "cleaned2.xlsx"      # 输出文件名

print("开始执行清洗...")

# ======== 1. 读取 Excel（一次性读取，不使用 chunksize）========
df = pd.read_excel(input_file, dtype=str)

print(f"原始数据行数：{len(df)}")

# ======== 2. 填补空值，避免 NA 导致报错 ========
df = df.replace({np.nan: ""})

# ======== 3. 删除内容为空的行 ========
df = df[df["内容"].str.strip() != ""]

print(f"删除内容为空后：{len(df)}")

# ======== 4. 删除内容少于 300 字的行 ========
df = df[df["内容"].str.len() >= 300]
print(f"删除内容 <300 字后：{len(df)}")

# ======== 5. 删除明显无效标题（版头、广告等） ========
bad_keywords = [
    "本版", "责编", "广告", "声明", "刊登", "登报", "出版",
    "目录", "目次", "人民日报社论", "人民日报评论", 
    "人民日报要闻", "人民日报记者", "人民日报评论员",
]

pattern = "|".join(bad_keywords)
df = df[~df["标题"].str.contains(pattern, regex=True, na=False)]

print(f"删除无效标题后：{len(df)}")

# ======== 6. 按内容去重（保留第一条）=====
df = df.drop_duplicates(subset=["内容"], keep="first")
print(f"按内容去重后：{len(df)}")

# ======== 7. 导出结果 ========
df.to_excel(output_file, index=False, engine="openpyxl")

print("清洗完成！")
print(f"最终保留：{len(df)} 条")
print(f"输出文件：{output_file}")
