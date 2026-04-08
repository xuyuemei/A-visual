with open("src/pages/Main/Main.module.css", "r", encoding="utf-8") as f:
    text = f.read()
import re
# Remove the inner margin-left modifications to avoid double shifting.
text = re.sub(
    r'\.topSection \.heroTextInner,\s*\.modelEvaluationSection \.heroTextInner\s*\{[^}]*\}',
    '',
    text
)
# same for media queries
text = re.sub(
    r'  \.topSection \.heroTextInner,\s*  \.modelEvaluationSection \.heroTextInner\s*\{[^}]*\}',
    '',
    text
)
text = re.sub(
    r'\n\n(\n)*',
    '\n\n',
    text
)

with open("src/pages/Main/Main.module.css", "w", encoding="utf-8") as f:
    f.write(text)
