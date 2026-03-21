import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './HeroSection.module.css';

const HeroSection: React.FC = () => {
  const { t } = useTranslation();

  return (
    <section className={styles.topSection}>
      <div className={styles.heroLayout}>
        <div className={styles.heroTextColumn}>
          <h2 className={styles.sectionTitle}>{t('home.title')}</h2>
          <p className={styles.sectionSubtitleMain}>{t('home.subtitle')}</p>
          <p className={styles.sectionIntro}>
            {t('home.description1')}
          </p>
          <p className={styles.sectionIntro}>
            {t('home.description2')}
          </p>
        </div>
        <div className={styles.heroImageColumn}>
          <img src="/logo.png" alt="价值罗盘主视觉" className={styles.heroImage} />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;