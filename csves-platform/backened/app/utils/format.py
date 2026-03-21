import pandas as pd
from flask import Blueprint,Flask, request, jsonify
import pandas as pd
import json

def df_to_celldata(df: pd.DataFrame):
    # 构造表头
    celldata = []
    if isinstance(df, pd.Series):
         df = df.to_frame().T  # 转为一行的 DataFrame

    for col_name in df.columns:
        celldata.append({
            "r": 0,
            "c": df.columns.get_loc(col_name),
            "v": { "v": str(col_name) }
        })  
    for r in range(df.shape[0]):
        for c in range(df.shape[1]):
            value = df.iat[r, c]
            celldata.append({
                "r": r+1,
                "c": c,
                "v": { "v": str(value) }
            })

    result = { "celldata": celldata }
    # 最终格式
    return jsonify(result),200

def celldata_to_df(sheet_data_str):
    celldata = json.loads(sheet_data_str)

    # 获取最大行和列
    max_row = max(cell["r"] for cell in celldata) + 1
    max_col = max(cell["c"] for cell in celldata) + 1

    # 初始化空表格
    table = [["" for _ in range(max_col)] for _ in range(max_row)]

    # 填充单元格数据
    for cell in celldata:
        row, col = cell["r"], cell["c"]
        value = cell["v"].get("v", "")
        table[row][col] = value

    # 构建 DataFrame
    df = pd.DataFrame(table[1:], columns=table[0])
    return df
