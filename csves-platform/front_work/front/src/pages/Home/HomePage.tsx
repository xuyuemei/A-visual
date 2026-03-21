import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import HeroSection from '../../components/HeroSection/HeroSection';
import Card from '../../components/Card/Card';
import VideoUploadSection from '../../components/VideoUploadSection/VideoUploadSection';
import styles from './HomePage.module.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const features = [
    {
      id: 'text-score',
      title: t('home.textEvaluation'),
      description: t('textScoring.description1'),
      tags: [t('navigation.textScoring'), t('textScoring.title'), t('common.upload')],
      bgImage: '', // 不再使用背景图片
      icon: '/assets/icons/txt-eval.PNG', // 使用你的 PNG 图片
      iconSize: 'small', // 添加尺寸标识
      path: '/main?tab=text'
    },
    {
      id: 'video-analysis',
      title: t('home.videoEvaluation'),
      description: t('videoEvaluation.description1'),
      tags: [t('navigation.videoEvaluation'), t('videoEvaluation.title'), t('common.upload')],
      bgImage: '',
      icon: '/assets/icons/video-eval.png',
      iconSize: 'large',
      path: '/main?tab=video'
    },
    {
      id: 'model-evaluate',
      title: t('home.modelEvaluation'),
      description: t('home.modelEvaluationDescription'),
      tags: [t('navigation.modelEvaluation'), t('evaluate.comparePool.title'), t('textScoring.startScoring')],
      bgImage: '', // 不再使用背景图片
      icon: '/assets/icons/model-eval.PNG', // 使用你的 PNG 图片
      iconSize: 'normal', // 添加尺寸标识
      path: '/main?tab=evaluate'
    }
  ];

  const handleCardClick = (path: string) => {
    navigate(path);
  };

  return (
    <div className={styles.container}>
      {/* Hero Section - 使用 Main 页面的 Honor 样式 */}
      <HeroSection />

      {/* Features Section */}
      <section className={styles.featuresSection}>
        <div className={styles.featuresContainer}>
          <h2 className={styles.sectionTitle}>{t('home.featureModulesTitle')}</h2>
          <p className={styles.sectionSubtitle}>{t('home.featureModulesSubtitle')}</p>
          
          <div className={styles.cardsGrid}>
            {features.map((feature) => (
              <Card
                key={feature.id}
                title={feature.title}
                description={feature.description}
                bgImage={feature.bgImage}
                icon={feature.icon}
                tags={feature.tags}
                onMoreClick={() => handleCardClick(feature.path)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <p>&copy; 2024 社会主义核心价值观智能评测系统. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
