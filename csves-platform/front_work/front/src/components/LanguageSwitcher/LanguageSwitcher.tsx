import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tooltip } from 'antd';
import { CustomTranslationIcon } from './CustomTranslationIcon';
import styles from './LanguageSwitcher.module.css';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  
  const handleLanguageChange = () => {
    const nextLang = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(nextLang);
    localStorage.setItem('language', nextLang);
  };
  
  return (
    <Tooltip title={i18n.language === 'zh' ? 'Switch to English' : '切换至中文'} placement="bottom">
      <div 
        className={styles.iconBtn} 
        onClick={handleLanguageChange}
        title="Toggle Language"
      >
        <CustomTranslationIcon currentLang={i18n.language} />
      </div>
    </Tooltip>
  );
};

export default LanguageSwitcher;
