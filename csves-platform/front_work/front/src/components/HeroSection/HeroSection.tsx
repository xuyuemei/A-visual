import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './HeroSection.module.css';

const HeroSection: React.FC = () => {
  const { t } = useTranslation();
  const description1 = t('home.description1').trim();
  const description2 = t('home.description2').trim();

  return (
    <section className={styles.topSection}>
      <div className={styles.heroLayout}>
        <div className={styles.heroTextColumn}>
          <div className={styles.heroTextScale}>
            <h2 className={styles.sectionTitle}>{t('home.title')}</h2>
            <p className={styles.sectionSubtitleMain}>{t('home.subtitle')}</p>
            {description1 && <p className={styles.sectionIntro}>{description1}</p>}
            {description2 && <p className={styles.sectionIntro}>{description2}</p>}
          </div>
        </div>
        <div className={styles.heroImageColumn}>
          <img src="/logo.png" alt="价值罗盘主视觉" className={styles.heroImage} />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;