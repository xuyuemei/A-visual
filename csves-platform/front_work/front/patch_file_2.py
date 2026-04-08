import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the side panel section for evidence extracting and remove it
start_idx = content.find('<div className={styles.sidePanelSection}>\n  <div className={styles.sidePanelHeader}>\n    <span className={styles.sidePanelTitle}>证据提取</span>')

if start_idx != -1:
    end_idx = content.find('<div className={styles.sidePanelSection}>\n            <div className={styles.sidePanelHeader}>\n              <span className={styles.sidePanelTitle}>深度分析</span>\n            </div>')
    if end_idx != -1:
        content = content[:start_idx] + content[end_idx:]

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
