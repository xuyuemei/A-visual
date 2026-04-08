import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.module.css', 'r', encoding='utf-8') as f:
    content = f.read()

badge_orig = """\.evidenceBadge\s*\{[\s\S]*?font-weight:\s*700;\s*\}"""
badge_new = """.evidenceBadge {
  color: #0f63c9;
  font-size: 13px;
  font-weight: 700;
}"""
content = re.sub(badge_orig, badge_new, content)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.module.css', 'w', encoding='utf-8') as f:
    f.write(content)
