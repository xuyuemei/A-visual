import re

with open("src/pages/Main/Main.module.css", "r", encoding="utf-8") as f:
    text = f.read()

# Desktop
text = re.sub(
    r'\.textScoreSection \.heroTextColumn \{[^\}]*\}',
    r'.textScoreSection .heroTextColumn {\n  padding-left: calc(72px + 0.8cm);\n}',
    text,
    count=1
)

text = re.sub(r'\.textScoreSection \.heroImageColumn \{[^\}]*\}', '', text, count=1)

# Mobile
text = re.sub(
    r'\.textScoreSection \.heroTextColumn \{[^\}]*\}',
    r'.textScoreSection .heroTextColumn {\n    padding-left: calc(36px + 0.8cm);\n  }',
    text,
    count=1
)

text = re.sub(r'  \.textScoreSection \.heroImageColumn \{[^\}]*\}\n\n', '', text, count=1)

with open("src/pages/Main/Main.module.css", "w", encoding="utf-8") as f:
    f.write(text)
