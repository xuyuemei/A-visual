import re

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/HeroSection/HeroSection.module.css', 'r', encoding='utf-8') as f:
    hero_css = f.read()

hero_css = re.sub(r'margin-left:\s*0\.7cm;', 'margin-left: 1.5cm;', hero_css)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/HeroSection/HeroSection.module.css', 'w', encoding='utf-8') as f:
    f.write(hero_css)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/TextScoreSection/TextScoreSection.module.css', 'r', encoding='utf-8') as f:
    text_css = f.read()

# Make the container have a nice gradient instead of just pure white
text_css = text_css.replace('background: #ffffff;', 'background: linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #faf5ff 100%);')
# Make the inner card stand out slightly more if the background is tinted
text_css = text_css.replace('background: rgba(255, 255, 255, 0.86);', 'background: rgba(255, 255, 255, 0.95);')

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/components/TextScoreSection/TextScoreSection.module.css', 'w', encoding='utf-8') as f:
    f.write(text_css)

