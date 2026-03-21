#PROMPTS_CONFIG

TEXT2DF='''
你是一位资深的数据分析师，请从所给文本中提取出关键信息并整理为dataframe格式对应的字典返回。
【要求】
1. 所有字段信息必须保留，不能遗漏；
2. 确保字典格式合法，可被 pd.DataFrame() 成功解析；
3. 不要存在嵌套结构，键值应该为列标题；
4. 不要添加额外解释，仅返回格式化后的字典；
5. 特别检查返回结果中含的数据是否与原文所给的数据一致。
【文本】
'''

IMAGE2DF='''
你是一位资深的数据分析师，请从所给附件图片中提取出关键信息并整理为dataframe格式对应的字典返回。
【要求】
1. 所有字段信息必须保留，不能遗漏；
2. 确保字典格式合法，可被 pd.DataFrame() 成功解析；
3. 不要存在嵌套结构，键值应该为列标题；
4. 不要添加额外解释，仅返回格式化后的字典；
5. 特别检查返回结果中含的数据是否与原文所给的数据一致。
'''

def TXT2IMAGE(data,type,requirements,color):
    template = '''
    你是一个资深的Python专家，现在我已经定义好一个名为 df 的 DataFrame，包含了所需的数据。请完善现有Python代码，该代码使用matplotlib根据df绘制{type}。
    【现有代码】
    ```python
    import io
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    import pandas as pd
    data = {data}
    df = pd.DataFrame(data)
   【待完善部分】
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf = io.BytesIO()
    buf.seek(0)
    plt.close()
    ```
    【注意】
    1.不要返回完整的python代码，仅返回【待完善部分】，且【待完善部分】用<START>和<END>包裹返回；
    2.【待完善部分】不能出现已有代码，避免与已给出的代码重复；
    3.不要重新定义或赋值 df（如 df = pd.DataFrame(...)）。我已经在外部定义好了,在【待完善部分】中直接用df指代即可；
    4.代码必须包含必要的导入语句，若已有的导入语句不覆盖【待完善部分】需使用的包，则在【待完善部分】内部补充导入语句。
    【要求】
    {requirements}
    【配色】
    图表配色需从以下颜色中选择：
    {color}
    '''

    return template.format(type=type, data=data, requirements=requirements, color=color)

def TXT2IMAGE_REVISE(data,history_code,requirements):
    return f'''
你是一个资深的Python专家，请根据用户提出的要求，修正通过matplotlib生成图表的Python代码。部分代码已经写死，仅修改并返回【可修改部分】即可。

【原始代码】
```python
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import pandas as pd
data = {data}
df = pd.DataFrame(data)
【可修改部分】
plt.savefig(buf, format='png', bbox_inches='tight')
buf = io.BytesIO()
buf.seek(0)
plt.close()
```
【可修改部分】
{history_code}

【注意】
1.不要返回完整的python代码，仅返回【可修改部分】，且【可修改部分】用<START>和<END>包裹返回；
2.【可修改部分】不能出现写死的原始代码，避免与写死的代码重复；
3.不要重新定义或赋值 df（如 df = pd.DataFrame(...)）。我已经在写死的原始代码中定义好了,在【可修改部分】中直接用df指代即可；
4.代码必须包含必要的导入语句，若已有的导入语句不覆盖【可修改部分】需使用的包，则在【可修改部分】内部补充导入语句。
5.若用户有要求修改字体，则在【可修改部分】重新设置字体，覆盖写死的代码中的字体即可。
【要求】
{requirements}
'''

#MODEL_TYPE_CONFIG
MODEL_TYPE = {
    "1": "deepseek-reasoner",
    "2": "deepseek-v3", 
    "3": "baichuan-13b",
}