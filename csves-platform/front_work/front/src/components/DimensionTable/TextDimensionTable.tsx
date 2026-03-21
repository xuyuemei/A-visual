import React from "react";
import styles from "./DimensionTable.module.css";

interface TextDimensionTableProps {
  scores: Record<string, number>;
  title?: string;
}

const TextDimensionTable: React.FC<TextDimensionTableProps> = ({
  scores,
  title = "社会主义核心价值观维度评分表",
}) => {
  const dimensions = [
    "富强", "民主", "文明", "和谐", "自由", "平等",
    "公正", "法治", "爱国", "敬业", "诚信", "友善",
  ];

  // 获取分数颜色类名（保持和原版一致）
  const getScoreColorClass = (score: number) => {
    if (score >= 8) return styles.highScore;
    if (score >= 6) return styles.mediumScore;
    return styles.lowScore;
  };

  return (
    <div className={styles.tableContainer}>
      <h3 className={styles.tableTitle}>{title}</h3>

      <div className={styles.tableWrapper}>
        <table className={styles.scoreTable}>
          <thead>
            <tr>
              {/* ✅ 删掉“模型名称”这一列 */}
              {dimensions.map((dimension) => (
                <th key={dimension} className={styles.dimensionHeader}>
                  {dimension}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            <tr>
              {dimensions.map((dimension) => {
                const score = scores?.[dimension] ?? 0;
                return (
                  <td
                    key={dimension}
                    className={`${styles.scoreCell} ${getScoreColorClass(score)}`}
                  >
                    {Number(score).toFixed(2)}
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>

      <div className={styles.tableFooter}></div>
    </div>
  );
};

export default TextDimensionTable;
