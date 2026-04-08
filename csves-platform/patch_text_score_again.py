import re

file_path = '/data/hlt/A-visual/csves-platform/front_work/front/src/components/TextScoreSection/TextScoreSection.module.css'
with open(file_path, 'r', encoding='utf-8') as f:
    text_css = f.read()

# 1. Container back to pure white
text_css = text_css.replace('background: linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #faf5ff 100%);', 'background: #ffffff;')

# 2. Card background a subtle distinct color to break the "pure white all over" complaint
text_css = text_css.replace('background: rgba(255, 255, 255, 0.95);', 'background: #f8fafc;')

# 3. Text area background to white or another pleasant tint to pop from the f8fafc card
text_css = text_css.replace('background: rgba(251, 252, 255, 0.92);', 'background: #ffffff;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text_css)
