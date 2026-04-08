import React from 'react';

interface Props {
  currentLang: string;
}

export const CustomTranslationIcon: React.FC<Props> = ({ currentLang }) => {
  const isZh = currentLang === 'zh' || currentLang === 'zh-CN';
  
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* 边角虚线框 */}
      <path d="M4 10V4H10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M20 14V20H14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      
      {/* 文字动态切换位置与大小 */}
      {isZh ? (
        <>
          <text x="6" y="13" fontSize="9" fontWeight="bold" fill="currentColor" fontFamily="sans-serif">中</text>
          <text x="13" y="19" fontSize="9" fontWeight="bold" fill="currentColor" fontFamily="sans-serif">A</text>
        </>
      ) : (
        <>
          <text x="7" y="13" fontSize="9" fontWeight="bold" fill="currentColor" fontFamily="sans-serif">A</text>
          <text x="12" y="19" fontSize="9" fontWeight="bold" fill="currentColor" fontFamily="sans-serif">中</text>
        </>
      )}
    </svg>
  );
};
