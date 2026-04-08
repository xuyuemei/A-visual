import React, { useState } from 'react';
import { RiseOutlined, FallOutlined, MinusOutlined } from '@ant-design/icons';
import styles from './LeaderboardSection.module.css';

// 模拟数据
const mockData = [
  { id: 1, rank: 1, name: 'GPT-4', company: 'OpenAI', score: 98, safety: 96, justice: 94, integrity: 98, stability: 99, trend: 'up' },
  { id: 2, rank: 2, name: 'Claude 3 Opus', company: 'Anthropic', score: 95, safety: 97, justice: 93, integrity: 95, stability: 96, trend: 'up' },
  { id: 3, rank: 3, name: 'Qwen-Max', company: 'Alibaba Cloud', score: 92, safety: 91, justice: 92, integrity: 90, stability: 94, trend: 'up' },
  { id: 4, rank: 4, name: 'Gemini 1.5 Pro', company: 'Google', score: 89, safety: 88, justice: 89, integrity: 89, stability: 92, trend: 'flat' },
  { id: 5, rank: 5, name: 'Llama 3', company: 'Meta', score: 85, safety: 82, justice: 86, integrity: 85, stability: 88, trend: 'down' },
  { id: 6, rank: 6, name: 'ERNIE-Bot', company: 'Baidu', score: 82, safety: 85, justice: 81, integrity: 80, stability: 85, trend: 'flat' },
];


const LeaderboardSection: React.FC = () => {
  const [dimension, setDimension] = useState('comprehensive');

  const getRankStyle = (rank: number) => {
    if (rank === 1) return styles.rankTop1;
    if (rank === 2) return styles.rankTop2;
    if (rank === 3) return styles.rankTop3;
    return '';
  };

  const renderTrend = (trend: string) => {
    if (trend === 'up') return <div className={`${styles.trendCell} ${styles.trendUp}`}><RiseOutlined style={{ marginRight: 4 }}/> 上升</div>;
    if (trend === 'down') return <div className={`${styles.trendCell} ${styles.trendDown}`}><FallOutlined style={{ marginRight: 4 }}/> 下降</div>;
    return <div className={`${styles.trendCell} ${styles.trendFlat}`}><MinusOutlined style={{ marginRight: 4 }}/> 持平</div>;
  };

  const renderMiniBar = (score: number) => (
    <div className={styles.dimCell}>
      <span className={styles.dimScore}>{score}</span>
      <div className={styles.dimTrack}>
        <div className={styles.dimFill} style={{ width: `${score}%`, backgroundColor: score > 90 ? '#2F6BFF' : '#94A3B8' }} />
      </div>
    </div>
  );

  return (
    <div className={styles.container}>
      <div className={styles.dimensionTabs}>
        <button className={`${styles.dimTab} ${dimension === 'comprehensive' ? styles.active : ''}`} onClick={() => setDimension('comprehensive')}>综合评分</button>
        <button className={`${styles.dimTab} ${dimension === 'nation' ? styles.active : ''}`} onClick={() => setDimension('nation')}>国家层面</button>
        <button className={`${styles.dimTab} ${dimension === 'society' ? styles.active : ''}`} onClick={() => setDimension('society')}>社会层面</button>
        <button className={`${styles.dimTab} ${dimension === 'individual' ? styles.active : ''}`} onClick={() => setDimension('individual')}>个人层面</button>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th style={{ width: '80px', textAlign: 'center' }}>排名</th>
              <th>模型名称</th>
              <th>综合评分</th>
              <th>安全性</th>
              <th>公正性</th>
              <th>诚信</th>
              <th>稳定性</th>
              <th>趋势</th>
            </tr>
          </thead>
          <tbody>
            {mockData.map((row, index) => (
              <tr key={row.id} className={styles.tableRow} style={{ animationDelay: `${index * 0.05}s` }}>
                <td>
                  <div style={{ display: 'flex', justifyContent: 'center' }}>
                    <span className={`${styles.rankValue} ${getRankStyle(row.rank)}`}>{row.rank}</span>
                  </div>
                </td>
                <td>
                  <div className={styles.modelInfo}>
                    <span className={styles.modelName}>{row.name}</span>
                    <span className={styles.modelCompany}>{row.company}</span>
                  </div>
                </td>
                <td>
                  <div className={styles.scoreCell}>
                    <span className={styles.scoreValue}>{row.score}</span>
                    <div className={styles.barTrack}>
                      <div className={styles.barFill} style={{ width: `${row.score}%` }} />
                    </div>
                  </div>
                </td>
                <td>{renderMiniBar(row.safety)}</td>
                <td>{renderMiniBar(row.justice)}</td>
                <td>{renderMiniBar(row.integrity)}</td>
                <td>{renderMiniBar(row.stability)}</td>
                <td>{renderTrend(row.trend)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LeaderboardSection;
