import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher/LanguageSwitcher';
import styles from './Navbar.module.css';

const Navbar: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const isActiveTab = (tab: string) => {
    return location.pathname === `/main?tab=${tab}`;
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.navbarContainer}>
        <div className={styles.navbarLeft}>
          <span className={styles.logoText}>C-Voices</span>
        </div>
        <div className={styles.navbarRight}>
          <button
            className={`${styles.navButton} ${location.pathname === '/' ? styles.active : ''}`}
            onClick={() => handleNavigate('/')}
          >
            {t('navigation.home')}
          </button>
          <button
            className={`${styles.navButton} ${isActiveTab('text') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=text')}
          >
            {t('navigation.textScoring')}
          </button>
          <button
            className={`${styles.navButton} ${isActiveTab('evaluate') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=evaluate')}
          >
            {t('navigation.modelEvaluation')}
          </button>
          <button
            className={`${styles.navButton} ${isActiveTab('video') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=video')}
          >
            {t('navigation.videoEvaluation')}
          </button>
          <button
            className={`${styles.navButton} ${isActiveTab('history') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=history')}
          >
            {t('navigation.history')}
          </button>
          <LanguageSwitcher />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
