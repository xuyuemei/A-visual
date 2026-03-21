import pandas as pd

# ==== 你自己的输入文件路径 ====
input_file = "shuffle.xlsx"
output_file = "shuffled.xlsx"

# 读取文件
df = pd.read_excel(input_file, dtype=str)

# 保留第一行不动
head = df.iloc[:1]       # 第一行
body = df.iloc[1:]       # 后面所有行

# 随机打乱 body
body_shuffled = body.sample(frac=1, random_state=None).reset_index(drop=True)

# 合并
df_new = pd.concat([head, body_shuffled], ignore_index=True)

# 保存
df_new.to_excel(output_file, index=False)

print("完成！已生成：", output_file)
