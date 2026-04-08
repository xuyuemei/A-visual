import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

orig = """<div className={styles.questionHeader}>
    <div className={styles.questionTag}>Q{currentPage + 1}</div>
    <h3 className={styles.questionText}>{currentQuestion?.question || ""}</h3>
  </div>"""

new_str = """<div className={styles.questionHeader} style={{ alignItems: 'baseline' }}>
    <span className={styles.questionTag} style={{ fontSize: '20px' }}>Q{currentPage + 1}</span>
    <h3 className={styles.questionText} style={{ fontSize: '20px' }}>{currentQuestion?.question || ""}</h3>
  </div>"""

content = content.replace(orig, new_str)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

