import re

with open("src/components/HistorySection/HistorySection.tsx", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("prevPage(record, activeAnswerModel)", "prevPage()")
text = text.replace("nextPage(record, activeAnswerModel)", "nextPage()")

with open("src/components/HistorySection/HistorySection.tsx", "w", encoding="utf-8") as f:
    f.write(text)
