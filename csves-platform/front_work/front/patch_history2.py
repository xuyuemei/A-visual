import re
with open("src/components/HistorySection/HistorySection.tsx", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "<RadarChart scoresByModel={record.scoresByModel} />",
    "<RadarChart scoresByModel={record.scoresByModel || {}} />"
)
text = text.replace(
    "<DimensionTable scoresByModel={record.scoresByModel} />",
    "<DimensionTable scoresByModel={record.scoresByModel || {}} />"
)

with open("src/components/HistorySection/HistorySection.tsx", "w", encoding="utf-8") as f:
    f.write(text)
