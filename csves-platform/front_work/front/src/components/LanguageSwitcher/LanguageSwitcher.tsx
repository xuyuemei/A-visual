import React from 'react';
import { Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { GlobalOutlined } from '@ant-design/icons';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  
  const languages = [
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
  ];
  
  const handleLanguageChange = (lang: string) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
  };
  
  return (
    <Select
      value={i18n.language}
      onChange={handleLanguageChange}
      style={{ 
        width: 120, 
        marginRight: '16px',
        height: '40px'
      }}
      suffixIcon={<GlobalOutlined />}
      placeholder="Language"
      size="middle"
    >
      {languages.map(lang => (
        <Select.Option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </Select.Option>
      ))}
    </Select>
  );
};

export default LanguageSwitcher;
