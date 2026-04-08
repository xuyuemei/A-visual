import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ReadOutlined, VideoCameraOutlined, ApiOutlined } from '@ant-design/icons';
import styles from './HomePage.module.css';

gsap.registerPlugin(ScrollTrigger);

const CORE_VALUES = ['富强', '民主', '文明', '和谐', '自由', '平等', '公正', '法治', '爱国', '敬业', '诚信', '友善'];

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  
  const heroRef = useRef<HTMLDivElement>(null);
  const compassWrapperRef = useRef<HTMLDivElement>(null);
  const outerRingRef = useRef<SVGGElement>(null);
  const middleRingRef = useRef<SVGGElement>(null);
  const innerRingRef = useRef<SVGGElement>(null);
  
  const [activeValue, setActiveValue] = useState<string | null>(null);

  useEffect(() => {
    // 强制每次刷新回到顶部，保障100vh初始体验
    window.scrollTo(0, 0);

    // 巨大的罗盘背景反向旋转动画
    if (compassWrapperRef.current) {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: heroRef.current, 
          start: 'top top', 
          end: '+=1000', // 增加滚动距离维持旋转效果
          scrub: 1, 
        },
      });

      const outerRotation = -180; // 外圈逆时针大幅旋转
      const middleRotation = -60; // 中圈较慢逆时针
      const innerRotation = 180;  // 内圈顺时针

      tl.to(compassWrapperRef.current, { scale: 1.05, ease: 'none'}, 0)
        // 外层及内部文字反补逻辑（保证文字端正）
        .to(outerRingRef.current, { rotation: outerRotation, transformOrigin: 'center center', ease: 'none' }, 0)
        .to('.valueNodeContent', { rotation: -outerRotation, transformOrigin: '0px 0px', ease: 'none' }, 0)
        
        // 中层刻度
        .to(middleRingRef.current, { rotation: middleRotation, transformOrigin: 'center center', ease: 'none' }, 0)
        
        // 内层
        .to(innerRingRef.current, { rotation: innerRotation, transformOrigin: 'center center', ease: 'none' }, 0);
    }

    // 鼠标移动轻量 3D 倾斜
    const handleMouseMove = (e: MouseEvent) => {
      if (!compassWrapperRef.current) return;
      const rect = compassWrapperRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left - rect.width / 2) / 60; 
      const y = -(e.clientY - rect.top - rect.height / 2) / 60;
      
      gsap.to(compassWrapperRef.current, {
        rotationY: x,
        rotationX: y,
        ease: 'power2.out',
        duration: 2,
      });
    };

    const compassEl = compassWrapperRef.current;
    if (compassEl) {
      compassEl.addEventListener('mousemove', handleMouseMove);
      compassEl.addEventListener('mouseleave', () => {
        gsap.to(compassWrapperRef.current, { rotationY: 0, rotationX: 0, ease: 'power2.out', duration: 1.5 });
      });
    }

    return () => {
      if (compassEl) {
        compassEl.removeEventListener('mousemove', handleMouseMove);
      }
      ScrollTrigger.getAll().forEach(t => t.kill());
    };
  }, []);

  return (
    <div className={styles.container}>
      
      {/* 
        ========================================
        🔥 1️⃣ 满屏深蓝科技层 Hreo Section (100vh)
        ========================================
      */}
      <section className={styles.hero} ref={heroRef}>
        
        {/* 背景粒子与线框效果 */}
        <div className={styles.gridOverlay}></div>
        
        {/* 巨大的背景罗盘容器 - 居中铺满 */}
        <div className={styles.giantCompassContainer} ref={compassWrapperRef}>
          <svg viewBox="0 0 1000 1000" className={styles.compassSvg}>
            <defs>
              <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
              <filter id="textGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0" stdDeviation="4" floodOpacity="0.8" floodColor="#2F6BFF" />
              </filter>
              
              <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(47, 107, 255, 0.3)" />
                <stop offset="50%" stopColor="rgba(47, 107, 255, 0.6)" />
                <stop offset="100%" stopColor="rgba(47, 107, 255, 0.3)" />
              </linearGradient>
            </defs>

            {/* ------------ 外层环：12价值观文字环 ------------ */}
            <g ref={outerRingRef}>
              {/* 超大虚线卫星轨道 */}
              <circle cx="500" cy="500" r="420" fill="none" stroke="url(#ringGrad)" strokeWidth="2" strokeDasharray="10,15" />
              <circle cx="500" cy="500" r="480" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />
              
              {CORE_VALUES.map((val, i) => {
                const angle = (i * 30 - 90) * (Math.PI / 180);
                const x = 500 + 420 * Math.cos(angle);
                const y = 500 + 420 * Math.sin(angle);
                const isActive = activeValue === val;
                
                return (
                  <g key={val} transform={`translate(${x},${y})`} 
                     onMouseEnter={() => setActiveValue(val)} 
                     onMouseLeave={() => setActiveValue(null)}>
                    {/* 摩天轮抵消层 */}
                    <g className="valueNodeContent">
                      <circle r="6" fill={isActive ? "#FF8A00" : "#2F6BFF"} filter={isActive ? 'url(#neonGlow)' : ''} />
                      <text className={styles.outerText} textAnchor="middle" dy="-18" 
                            fill={isActive ? '#FFFFFF' : 'rgba(255,255,255,0.6)'} 
                            fontSize="18" fontWeight="600" letterSpacing="2"
                            filter={isActive ? 'url(#textGlow)' : ''}>
                        {val}
                      </text>
                    </g>
                  </g>
                );
              })}
            </g>

            {/* ------------ 中层环：数据刻度环 ------------ */}
            <g ref={middleRingRef}>
              <circle cx="500" cy="500" r="320" fill="none" stroke="rgba(47,107,255,0.4)" strokeWidth="20" strokeDasharray="4,8" />
              {/* 装饰游走刻度 */}
              <circle cx="500" cy="500" r="280" fill="none" stroke="rgba(255,138,0,0.8)" strokeWidth="1.5" strokeDasharray="50,200" />
              
              {Array.from({length: 24}).map((_, i) => {
                const angle = (i * 15) * (Math.PI / 180);
                const r = 320;
                const x = 500 + r * Math.cos(angle);
                const y = 500 + r * Math.sin(angle);
                return <circle key={`dot-${i}`} cx={x} cy={y} r={i%6===0 ? 4 : 2} fill={i%6===0 ? "#FF8A00" : "#2F6BFF"} />;
              })}
            </g>

            {/* ------------ 内层环：顺时针动态装饰层 ------------ */}
            <g ref={innerRingRef}>
              <circle cx="500" cy="500" r="230" fill="none" stroke="url(#ringGrad)" strokeWidth="1.5" />
              {/* 一条橙色的装饰断线环绕 */}
              <path d="M 270 500 A 230 230 0 1 1 730 500" fill="none" stroke="#FF8A00" strokeWidth="4" strokeLinecap="round" strokeDasharray="100,500" filter="url(#neonGlow)"/>
            </g>

          </svg>
        </div>

        {/* 覆盖在罗盘正中间的文案区域 */}
        <div className={styles.centerContent}>
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, delay: 0.2 }}
            className={styles.centerCard}
          >
            <h1 className={styles.mainTitle}>C-Voices</h1>
            <h2 className={styles.subTitle}>大模型社会主义核心价值观评估系统</h2>
            <div className={styles.btnGroup}>
              <button className={styles.startBtn} onClick={() => navigate('/main?tab=evaluate')}>
                开始智能评测
              </button>
            </div>
          </motion.div>
        </div>
        
        {/* 向下滚动提示 */}
        <div className={styles.scrollHint}>
          <span>向下滚动探索</span>
          <div className={styles.scrollLine}></div>
        </div>

      </section>


      {/* 
        ========================================
        🔥 2️⃣ 浅色UI前景块（卡片区等往下滚动才出）
        ========================================
      */}
      <div className={styles.contentWrapper}>
        <section className={styles.cardsSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.darkTitle}>智能多模态检测</h2>
            <p className={styles.darkDesc}>结合领先AI技术，打造一站式的内容安全栅栏</p>
          </div>
          
          <div className={styles.cardGrid}>
            <motion.div className={styles.card} whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(47,107,255,0.08)' }} onClick={() => navigate('/main?tab=evaluate')}>
              <div className={styles.cardIcon}><ApiOutlined /></div>
              <h3>模型评测</h3>
              <p>支持接入主流模型，通过海量评测集一键生成价值观雷达图谱。</p>
            </motion.div>

            <motion.div className={styles.card} whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(47,107,255,0.08)' }} onClick={() => navigate('/main?tab=text')}>
              <div className={styles.cardIcon}><ReadOutlined /></div>
              <h3>图文评测</h3>
              <p>基于大规模语料库，精准捕捉大模型文本输出中的价值观偏离点。</p>
            </motion.div>
            
            <motion.div className={styles.card} whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(47,107,255,0.08)' }} onClick={() => navigate('/main?tab=video')}>
              <div className={styles.cardIcon}><VideoCameraOutlined /></div>
              <h3>视频评测</h3>
              <p>对视频内容逐帧分析与语音转写，全面评估多媒体价值观倾向。</p>
            </motion.div>
          </div>
        </section>

        <footer className={styles.footer}>
          <p>&copy; 2026 C-Voices 社会主义核心价值观大模型评测系统</p>
        </footer>
      </div>

    </div>
  );
};

export default HomePage;
