from flask import Blueprint,Flask, request, jsonify
import pandas as pd
import io
from PIL import Image
import json
from flask_cors import CORS
from ..services.upload.data2df import *
import base64
from ..static.examplefile import example_files
from ..utils.format import df_to_celldata

bp = Blueprint('upload', __name__)

@bp.route('/api/upload', methods=['POST'])

def upload():
    print(request)   # 打印整个 request
    print(request.form)  # 打印文本表单
    print(request.files) # 打印上传的文件

    if 'text' in request.form:
        # 处理文本输入
        text = request.form['text']
        lines = text.strip()
        df = text2df(lines)
        print(df_to_celldata(df))
        return df_to_celldata(df)
    
    elif 'exampleFile' in request.form:
        text = request.form['exampleFile']
        return df_to_celldata(example_files[text])

    elif 'file' in request.files:
        # 处理文件上传
        file = request.files['file']
        filename = file.filename.lower()

        try:
            if filename.endswith(('.xlsx', '.xls')):
                print("print(xlsx))",file)
                df = pd.read_excel(file)
                print("print(df)",df)
            elif filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif filename.endswith('.json'):
                # 注意json有可能是数组或者字典，要做不同处理
                content = json.load(file)
                if isinstance(content, list):
                    df = pd.DataFrame(content)
                elif isinstance(content, dict):
                    df = pd.DataFrame([content])
                else:
                    return jsonify({"error": "不支持的 JSON 结构"}), 400
            elif filename.endswith(('.png', '.jpg', '.jpeg')):
                # 图片不直接转DataFrame，可以先转像素矩阵
                print(file)
                # file = request.files['image']  # 获取上传的 FileStorage 对象
                # 读取文件内容并编码为 base64
                img_bytes = file.read()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                df = image2df(img_base64,filename.split('.')[-1])
            else:
                return jsonify({"error": "不支持的文件类型"}), 400

            return df_to_celldata(df)

        except Exception as e:
            print("Error:", e)
            return jsonify({"error": f"文件解析失败: {str(e)}"}), 500

    else:
        return jsonify({"error": "未检测到有效上传内容"}), 400

