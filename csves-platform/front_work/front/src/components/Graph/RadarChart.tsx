import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { useTranslation } from "react-i18next";
import styles from "./RadarChart.module.css";

interface RadarChartProps {
  // 每个模型一组 12 维度得分
  scoresByModel: { [modelName: string]: { [dimension: string]: number } };
}

const RadarChart: React.FC<RadarChartProps> = ({ scoresByModel }) => {
  const { t } = useTranslation();
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = echarts.init(chartRef.current);

    const entries = Object.entries(scoresByModel);
    const isSingle = entries.length <= 1;

    // ✅ 建议固定维度顺序，避免对象 key 顺序偶尔不一致导致轴顺序变化
    const dimensions = [
      "富强", "民主", "文明", "和谐", "自由", "平等",
      "公正", "法治", "爱国", "敬业", "诚信", "友善",
    ];

    const firstScores = entries[0]?.[1] || {};
    const allVals: number[] = [];
    entries.forEach(([, s]) => {
      dimensions.forEach((d) => {
        const v = typeof s?.[d] === "number" ? s[d] : 0;
        allVals.push(v);
      });
    });

    // ✅ 自动决定 max：如果分数整体 <= 1 就按 1；否则按 10（兼容你表格阈值那种 0~10）
    const maxVal = allVals.length ? Math.max(...allVals) : 1;
    const radarMax = maxVal <= 1 ? 1 : 10;

    const indicators = dimensions.map((name) => ({
      name,
      max: radarMax,
    }));

    const buildOption = () => {
      const w = chart.getWidth();
      const h = chart.getHeight();
      const minDim = Math.min(w, h);
      const radiusRatio = 0.67;
      const outer = (minDim * radiusRatio) / 2;
      const cx = w / 2;
      const centerYRatio = 0.57;
      const cy = h * centerYRatio;
      const splitNumber = 5;

      // ✅ 刻度文字（按 max 显示 0.2、0.4… 或 2、4…）
      const ringLabels = Array.from({ length: splitNumber - 1 }, (_, i) => {
        const ratio = (i + 1) / splitNumber; // 1/5..4/5
        const y = cy - outer * ratio;
        const val = radarMax * ratio;
        const text = (radarMax <= 1 ? val.toFixed(2) : val.toFixed(1)).replace(/\.0$/, "");

        return {
          type: "text" as const,
          left: cx - 30,
          top: y - 6,
          style: {
            text,
            fill: "#8a8a8a",
            opacity: 0.9,
            fontSize: 12,
            fontWeight: 400,
            textAlign: "right",
          },
          z: 100,
          zlevel: 100,
          silent: true,
        };
      });

      const palette = ["#1E88E5", "#FB8C00", "#AB47BC", "#43A047", "#F4511E"];

      const seriesData = entries.map(([modelName, scores], idx) => {
        const baseColor = palette[idx % palette.length];
        const value = dimensions.map((d) => (typeof scores?.[d] === "number" ? scores[d] : 0));

        return {
          value,
          // ✅ 关键：单条数据不显示“输入文本”，统一叫“评分”
          name: isSingle ? "评分" : modelName,
          lineStyle: { color: baseColor, width: 2, type: "solid" as const },
          symbol: "circle" as const,
          symbolSize: 6,
          itemStyle: {
            color: baseColor,
            borderWidth: 0,
          },
          areaStyle: {
            color: baseColor + "33",
          },
        };
      });

      return {
        title: {
          text: t('common.socialistCoreValues'),
          left: "center",
          top: 8,
          textStyle: {
            fontSize: 19,
            fontWeight: 700,
            color: "#333",
            fontFamily:
              "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif",
          },
        },

        // ✅ 单条数据隐藏 legend（就不会出现“输入文本”）
        legend: {
          show: !isSingle,
          top: 40,
          data: entries.map(([name]) => name),
        },

        // ✅ tooltip：单条数据时不展示系列名（更干净）
        tooltip: {
          trigger: "item",
          formatter: (params: any) => {
            const value: number[] = params?.value || [];
            const lines = value.map((v, i) => {
              const dv = radarMax <= 1 ? Number(v).toFixed(2) : Number(v).toFixed(2);
              return `${dimensions[i]}：${dv}`;
            });
            return lines.join("<br/>");
          },
        },

        radar: {
          indicator: indicators,
          radius: `${radiusRatio * 100}%`,
          center: ["50%", `${centerYRatio * 100}%`],
          splitNumber,
          shape: "circle" as const,
          axisName: {
            color: "#444",
            fontSize: 16,
            fontWeight: 400,
          },
          splitLine: { lineStyle: { color: "#DCE8FA" } },
          splitArea: { areaStyle: { color: ["#eef3ff", "#f9fbff"] } },
        },

        series: [
          {
            name: "模型得分",
            type: "radar",
            data: seriesData,
          },
        ],

        graphic: ringLabels,
      };
    };

    chart.setOption(buildOption());

    const handleResize = () => {
      chart.resize();
      chart.setOption(buildOption(), true);
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [scoresByModel]);

  return <div ref={chartRef} className={styles.chart}></div>;
};

export default RadarChart;
