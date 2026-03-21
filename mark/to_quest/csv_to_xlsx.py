import pandas as pd
import os

def csv_to_xlsx(csv_path, xlsx_path=None):
    if xlsx_path is None:
        base_name = os.path.splitext(csv_path)[0]
        xlsx_path = base_name + ".xlsx"

    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="gbk")

    df.to_excel(xlsx_path, index=False)
    

if __name__ == "__main__":
    csv_path = "/data/hlt/A-visual/mark/ans500.csv"
    csv_to_xlsx(csv_path)
