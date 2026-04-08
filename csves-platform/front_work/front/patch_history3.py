import re

for filename in ["src/pages/History/History.tsx", "src/pages/History/HistoryChart.tsx"]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        text = text.replace("<API.ChartQueryRequest>", "<any>")
        text = text.replace("<API.Chart[]>", "<any[]>")
        text = text.replace("useRef<ActionType>()", "useRef<any>(undefined)")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Failed to process {filename}: {e}")
