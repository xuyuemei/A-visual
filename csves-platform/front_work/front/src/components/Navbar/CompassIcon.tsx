import React from 'react';

interface CompassIconProps {
  className?: string;
  size?: number;
  color?: string; // Main color for the compass outer ring and spokes
}

const CompassIcon: React.FC<CompassIconProps> = ({ className, size = 32, color = '#2F6BFF' }) => {
  return (
    <svg 
      className={className} 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* 极细的内部背景同心环 */}
      <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="1" opacity="0.1" />
      <circle cx="50" cy="50" r="30" fill="none" stroke={color} strokeWidth="1" opacity="0.1" />
      <circle cx="50" cy="50" r="18" fill="none" stroke={color} strokeWidth="1" opacity="0.1" />

      {/* 外圈蓝色实线框 */}
      <circle cx="50" cy="50" r="48" fill="none" stroke={color} strokeWidth="2.5" />

      {/* 12等分刻度 */}
      {Array.from({ length: 12 }).map((_, i) => (
        <line
          key={`tick-${i}`}
          x1="50" y1="2" x2="50" y2="16"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          transform={`rotate(${i * 30} 50 50)`}
        />
      ))}

      {/* 上半部分蓝色粗圆弧 */}
      {/* 扫过角度 22,48 -> 78,48 半径 28 */}
      <path 
        d="M 22 55 A 28 28 0 0 1 78 55" 
        fill="none" 
        stroke="#2196f3" 
        strokeWidth="16" 
        strokeLinecap="round" 
      />

      {/* 用白色直线对蓝色粗圆弧进行切割分段 */}
      <line x1="50" y1="58" x2="32" y2="24" stroke="#ffffff" strokeWidth="2.5" />
      <line x1="50" y1="58" x2="68" y2="24" stroke="#ffffff" strokeWidth="2.5" />

      {/* 中心的内侧橘色圆弧 */}
      <path 
        d="M 37 55 A 13 13 0 0 1 63 55" 
        fill="none" 
        stroke="#ff8a00" 
        strokeWidth="6" 
        strokeLinecap="round" 
      />
    </svg>
  );
};

export default CompassIcon;
