with open('/data/hlt/A-visual/csves-platform/front_work/front/src/pages/Main/Main.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

orig = """            <div className={styles.sectionHeader}>
              <div className={styles.heroEyebrow}>LEADERBOARD / RANKING / PERFORMANCE</div>
              <h2 className={styles.sectionTitle}>{t("navigation.history")}</h2>"""

new_str = """            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>{t("navigation.history")}</h2>"""

content = content.replace(orig, new_str)

with open('/data/hlt/A-visual/csves-platform/front_work/front/src/pages/Main/Main.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

