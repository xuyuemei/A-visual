import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove answerHeader entirely
start_idx = content.find('<div className={styles.answerHeader}>')
end_idx = content.find('<div className={styles.answerContentMain}>')
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + content[end_idx:]

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
