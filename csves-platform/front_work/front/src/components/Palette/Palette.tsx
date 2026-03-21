import styles from './Palette.module.css';
import React, { useState } from 'react';
import { Button, Popover, Col, Divider, Row } from 'antd';

interface OverlappingCirclesProps {
  count?: number;
  getColor: (index: number) => string;
}

interface PaletteProps {
  onColorSelect?: (colors: string[]) => void;
}


// import styles from './Palette.module.css';

const OverlappingCircles: React.FC<OverlappingCirclesProps> = ({
  count = 4,
  getColor
}) => {
  const circles = Array.from({ length: count });

  return (
    <div className={`flex justify-center ${styles.overlappingHover}`}>
      <div
        className="relative h-6"
        style={{
          width: `${count * 1}rem`,
        }}
      >
        {circles.map((_, index) => (
          <div
            key={index}
            className="w-6 h-6 rounded-full absolute top-0"
            style={{
              left: `${index * 1}rem`,
              backgroundColor: getColor(index),
              zIndex: index,
            }}
          />
        ))}
      </div>
    </div>
  );
};

// 默认颜色
const defaultColorList = ['#EAF3EA', '#ECF3FD', '#E1D5E7', '#CCE4FF'];

const paletteDictionary: Record<string, string[][]> = {
  学术风格: [
    ['#EAF3EA', '#ECF3FD', '#E1D5E7', '#CCE4FF'],
    ['#FFF1CC', '#F0A209', '#FBE6E6','#F5F5F5'],
    ['#4472C9', '#F8D973', '#7ABE48','#32C1B5'],
    ['#EFF3FB', '#A4A0B7', '#799EB9','#CEC7E6'],
  ],
  商务风格: [
    ['#C5E0B4', '#66A9D9', '#81D8F8','#FFD966'],
    ['#005C97', '#363795', '#a8c0ff','#F8C8D0'],
    ['#1561D1', '#1358BD', '#014F9C','#064C97'],
    ['#4C4C4C', '#D9D9D9', '#F2F2F2','#888c9c'],
  ],
  简约风格: [
    ['#FFFFFF', '#E0E0E0', '#C0C0C0'],
    ['#F5F5F5', '#A9A9A9', '#808080'],
    ['#000000', '#444444', '#888888'],
    ['#000000', '#444444', '#888888'],
  ],
  童趣风格: [
    ['#ff7f7f', '#fbbd9e', '#f9d48a', '#f6e7c1'],
    ['#e9f4a3', '#80cba4', '#4965b0','#fbda83'],
    ['#cc4a74', '#eb7852', '#fcb431','#f36f43'],
    ['#c4a5de', '#f6cae5', '#96cccb','#cc4a74'],
  ],
};

const Palette: React.FC<PaletteProps> = ({ onColorSelect }) => {
  const [selectedStyle, setSelectedStyle] = useState('学术风格');
  const [selectedColors, setSelectedColors] = useState(defaultColorList);

  const handleSelect = (styleName: string, colorList: string[]) => {
  setSelectedStyle(styleName);
  setSelectedColors(colorList);
  onColorSelect?.(colorList); // 调用传入的回调函数
  };


  const content = (
    <div style={{ width: 250, padding: 5, height: 200, overflowY: 'auto' }}>
      {Object.entries(paletteDictionary).map(([styleName, colorArrayList]) => (
        <div key={styleName}>
          <Divider orientation="left" style={{ borderColor: '#C0C0C0' }}>
            {styleName}
          </Divider>
          <Row gutter={[16, 24]}>
            {colorArrayList.map((colorList, index) => (
              <Col span={12} key={index}>
                <div
                  onClick={() => {
                    handleSelect(styleName, colorList)
                  }}
                  // className={styles.hoverCard}
                  style={{ cursor: 'pointer' }}
                >
                  <OverlappingCircles getColor={(i) => colorList[i % colorList.length]} />
                </div>
              </Col>
            ))}
          </Row>
        </div>
      ))}
    </div>
  );

  return (
    <Popover content={content} placement="right">
      <Button
        style={{
          width: 180,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          borderRadius: 4,
        }}
      >
        <div className="flex justify-center items-center w-full">
          <OverlappingCircles getColor={(i) => selectedColors[i % selectedColors.length]} />
          <span style={{ marginLeft: '16px', marginRight: '16px' }}>{selectedStyle}</span>
        </div>
      </Button>
    </Popover>
  );
};

export default Palette;
