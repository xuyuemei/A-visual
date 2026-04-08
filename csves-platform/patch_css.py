import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.module.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Change evidenceTabs padding
content = re.sub(r'(\.evidenceTabs\s*\{[^}]*padding:\s*)0 16px 12px;', r'\g<1>16px 16px 12px;', content)

# Change padding zero top in sidePanelSection? Wait, .sidePanelSection has overflow:hidden.
# Let's fix the evidenceTab styles completely:
evidence_tab_orig = """\.evidenceTab\s*\{[\s\S]*?transition:\s*all\s*0\.2s\s*ease;\s*\}"""
evidence_tab_new = """.evidenceTab {
  appearance: none;
  border: none;
  background: transparent;
  color: #64748b;
  padding: 4px 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: color 0.2s ease;
}"""
content = re.sub(evidence_tab_orig, evidence_tab_new, content)

evidence_tab_hover_orig = """\.evidenceTab:hover\s*\{[\s\S]*?border-color:\s*#93c5fd;\s*\}"""
evidence_tab_hover_new = """.evidenceTab:hover {
  color: #2563eb;
  background: transparent;
  border: none;
}"""
content = re.sub(evidence_tab_hover_orig, evidence_tab_hover_new, content)

evidence_tab_active_orig = """\.evidenceTabActive\s*\{[\s\S]*?box-shadow:\s*0\s*8px\s*18px\s*rgba\(37,\s*99,\s*235,\s*0\.2\);\s*\}"""
evidence_tab_active_new = """.evidenceTabActive {
  color: #2563eb;
  background: transparent;
  border: none;
  box-shadow: none;
}"""
content = re.sub(evidence_tab_active_orig, evidence_tab_active_new, content)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/EvaluateSection/EvaluateSection.module.css', 'w', encoding='utf-8') as f:
    f.write(content)
