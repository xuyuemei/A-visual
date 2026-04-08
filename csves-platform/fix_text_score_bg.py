import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/TextScoreSection/TextScoreSection.module.css', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace container background with white and remove before/after pseudo elements
bg_orig = r"""\s*background:\s*radial-gradient[\s\S]*?;\s*\}"""
content = re.sub(bg_orig, "\n  background: #ffffff;\n}", content)

before_orig = r"""\.container::before\s*\{[\s\S]*?\}\s*"""
content = re.sub(before_orig, "", content)

after_orig = r"""\.container::after\s*\{[\s\S]*?\}\s*"""
content = re.sub(after_orig, "", content)

# 2. Increase card width by 2.5cm
card_width_pattern = r"""\.card\s*\{\s*width:\s*100%;\s*max-width:\s*1100px;"""
card_new = """.card {\n  width: 100%;\n  max-width: calc(1100px + 2.5cm);"""
content = re.sub(card_width_pattern, card_new, content)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/TextScoreSection/TextScoreSection.module.css', 'w', encoding='utf-8') as f:
    f.write(content)
