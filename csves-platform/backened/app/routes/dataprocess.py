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
from ..services.dataprocess.dataprocess import get_processed_data

bp = Blueprint('dataprocess', __name__)

@bp.route('/api/dataprocess', methods=['POST'])

def dataprocess():
    form=request.form
    input_value = form.get("inputValue")
    selected_model = form.get("selectedModel")
    sheet_data_str = form.get("sheetData")
    result=get_processed_data(input_value, selected_model, sheet_data_str)
    print(result)
    if not result.empty:
        return df_to_celldata(result)
    else:
        return jsonify({"error": "未检测到有效上传内容"}), 400

