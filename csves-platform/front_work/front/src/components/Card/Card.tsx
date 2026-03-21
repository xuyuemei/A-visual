import React from 'react';
import styles from './Card.module.css';

interface CardProps {
  title: string;
  description: string;
  bgImage: string;
  icon: string;
  iconSize?: 'small' | 'normal' | 'large'; // 添加尺寸属性
  tags: string[];
  onMoreClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  title,
  description,
  bgImage, // 这个参数现在不使用，但保留接口
  icon,
  iconSize = 'normal', // 默认尺寸
  tags,
  onMoreClick
}) => {
  return (
    <div className={styles.cardContainer}>
      {/* 卡片头部 */}
      <header className={styles.header}>
        <div className={styles.left}>
          {icon && <img src={icon} alt={title} className={`${styles.icon} ${styles[iconSize]}`} />}
          <div>{title}</div>
        </div>
        <div className={styles.right} onClick={onMoreClick}>
          <div className={styles.moreWords}>
            了解更多
            <span className={styles.arrow}>→</span>
          </div>
        </div>
      </header>
      
      {/* 标签区域 */}
      <div className={styles.tagBox}>
        {tags.map((tag, index) => (
          <div key={index} className={styles.tag}>
            <span className={styles.tagName}>{tag}</span>
          </div>
        ))}
      </div>
      
      {/* 描述区域 */}
      <div className={styles.desc}>
        {description}
      </div>
    </div>
  );
};

export default Card;
