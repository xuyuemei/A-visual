import React from "react";
import styles from "./DimensionTable.module.css";

interface DimensionTableProps {
  scoresByModel: Record<string, Record<string, number>>;
}

const DimensionTable: React.FC<DimensionTableProps> = ({ scoresByModel }) => {
  const dimensions = [
    "富强", "民主", "文明", "和谐", "自由", "平等", 
    "公正", "法治", "爱国", "敬业", "诚信", "友善"
  ];

  // 获取分数颜色类名
  const getScoreColorClass = (score: number) => {
    if (score >= 8) return styles.highScore;
    if (score >= 6) return styles.mediumScore;
    return styles.lowScore;
  };

  return (
    <div className={styles.tableContainer}>
      <h3 className={styles.tableTitle}>社会主义核心价值观维度评分表</h3>
      
      <div className={styles.tableWrapper}>
        <table className={styles.scoreTable}>
          <thead>
            <tr>
              <th className={styles.modelHeader}>模型名称</th>
              {dimensions.map((dimension) => (
                <th key={dimension} className={styles.dimensionHeader}>
                  {dimension}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(scoresByModel).map(([modelName, scores]) => (
              <tr key={modelName}>
                <td className={styles.modelCell}>{modelName}</td>
                {dimensions.map((dimension) => {
                  const score = scores[dimension] || 0;
                  return (
                    <td
                      key={dimension}
                      className={`${styles.scoreCell} ${getScoreColorClass(score)}`}
                    >
                      {score.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className={styles.tableFooter}>
      </div>
    </div>
  );
};

export default DimensionTable;