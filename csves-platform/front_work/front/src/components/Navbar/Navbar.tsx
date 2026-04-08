import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher/LanguageSwitcher';
import CompassIcon from './CompassIcon';
import styles from './Navbar.module.css';

const Navbar: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // 这里的逻辑：超过一定的阈值（比如 100vh 或者 50px），就认为滚动过了，应用白底色。
      // 为防止在某些屏幕上计算出入我们暂定50px就变色，非常灵敏
      if (window.scrollY > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const currentTab = new URLSearchParams(location.search).get('tab');

  const isActiveTab = (tab: string) => {
    return location.pathname === '/main' && currentTab === tab;
  };

  const isHome = location.pathname === '/';
  
  // 如果是首页并且没有滚动，使用透明深色模式；否则使用默认（白色）模式
  const useHomeTheme = isHome && !scrolled;

  return (
    <nav className={`${styles.navbar} ${useHomeTheme ? styles.navbarHome : ''}`}>
      <div className={styles.navbarContainer}>
        <div className={styles.logoContainer} onClick={() => handleNavigate('/')}>
          <CompassIcon size={34} color={useHomeTheme ? '#ffffff' : '#0f63c9'} />
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
            className={`${styles.navButton} ${isActiveTab('evaluate') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=evaluate')}
          >
            {t('navigation.modelEvaluation')}
          </button>
          <button
            className={`${styles.navButton} ${isActiveTab('text') ? styles.active : ''}`}
            onClick={() => handleNavigate('/main?tab=text')}
          >
            {t('navigation.textScoring')}
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
