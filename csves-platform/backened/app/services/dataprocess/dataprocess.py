from app.utils.format import celldata_to_df 
from app.static.ai_config import MODEL_TYPE
import openai
import pandas_gpt

def get_processed_data(input_value, selected_model, sheet_data_str):
    # 处理数据的函数
    # 创建自定义OpenAI completer
    def custom_completer(prompt):
        client = openai.OpenAI(
            base_url='https://api.zhizengzeng.com/v1',
            api_key='zk-dcf0b26a7c6965a9e2086e34e6486739'
        )
        
        response = client.chat.completions.create(
            model=MODEL_TYPE[selected_model],
            messages=[
                {"role": "system", "content": "你是一个专业的数据分析师，擅长对问题进行社会主义核心价值观评估。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    # 创建自定义Ask实例
    ask_instance = pandas_gpt.Ask(completer=custom_completer)
    
    selected_model=MODEL_TYPE[selected_model]
    sheet_data_df=celldata_to_df(sheet_data_str)
    print(sheet_data_df)
    df = ask_instance(input_value, sheet_data_df)
    return df
