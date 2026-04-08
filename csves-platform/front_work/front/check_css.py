import re
with open("src/pages/Main/Main.module.css", "r", encoding="utf-8") as f:
    text = f.read()

opens = text.count('{')
closes = text.count('}')
print(f"Opens: {opens}, Closes: {closes}")
