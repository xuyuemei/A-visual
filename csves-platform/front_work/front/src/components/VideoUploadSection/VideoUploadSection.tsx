import React, { useState, useCallback } from 'react';
import axios from 'axios';
import RadarChart from '../Graph/RadarChart';
import DimensionTable from '../DimensionTable/DimensionTable';
import styles from './VideoUploadSection.module.css';
// ✅ 新增：历史记录
import { useHistoryStore } from '../history/historyStore';

interface VideoAnalysisResult {
  success: boolean;
  video_info: {
    filename: string;
    duration: number;
    fps: number;
    resolution: string;
    file_size: number;
  };
  frame_analyses: Array<{
    timestamp: number;
    frame_index: number;
    visual_analysis: string;
    analysis_type: string;
  }>;
  audio_analyses: Array<{
    start_time: number;
    end_time: number;
    text: string;
    audio_analysis: string;
    analysis_type: string;
  }>;
  transcript?: string;
  fusion_result: {
    success: boolean;
    fusion_analysis: string;
    all_analyses: any[];
    scores?: { [dimension: string]: number }; // 添加12维度评分
  };
  processing_summary: {
    total_frames: number;
    analyzed_frames: number;
    audio_segments: number;
    has_audio: boolean;
  };
}

const VideoUploadSection: React.FC = () => {
  const { addRecord } = useHistoryStore();
  const [activeView, setActiveView] = useState<"positioning" | "compass">("compass");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<VideoAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  
  const handleFileSelect = useCallback((file: File) => {
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      setError(null);
      setAnalysisResult(null);
    } else {
      setError('请选择有效的视频文件');
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('video', selectedFile);

    try {
      // 模拟进度更新
      let progressInterval: NodeJS.Timeout | null = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const response = await axios.post('/api/analyze_video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5分钟超时
      });

      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      setProgress(100);

      if (response.data.success) {
        setAnalysisResult(response.data);
        setActiveView("compass");
        
        // ✅ 保存到历史记录
        addRecord({
          type: 'video',
          videoInfo: response.data.video_info,
          transcript: response.data.transcript,
          processingSummary: response.data.processing_summary,
          scoresByModel: response.data.fusion_result.scores ? { '视频分析': response.data.fusion_result.scores } : undefined,
        });
        
        console.log("💾 视频分析结果已保存到历史记录");
      } else {
        setError(response.data.error || '分析失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || '上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={styles.container}>
      <div className={styles.uploadSection}>
        <h2 className={styles.title}>视频价值观分析</h2>
        <p className={styles.subtitle}>
          上传视频，系统将自动分析视觉内容和音频对话，进行多模态价值观评估
        </p>

        <div
          className={`${styles.uploadArea} ${dragOver ? styles.dragOver : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className={styles.fileInput}
            disabled={uploading}
          />
          
          <div className={styles.uploadContent}>
            <div className={styles.uploadIcon}>📹</div>
            <p className={styles.uploadText}>
              {selectedFile ? selectedFile.name : '拖拽视频文件到此处或点击选择'}
            </p>
            <p className={styles.uploadHint}>
              支持 MP4, AVI, MOV, MKV 等格式
            </p>
          </div>
        </div>

        {selectedFile && (
          <div className={styles.fileInfo}>
            <p><strong>文件名：</strong>{selectedFile.name}</p>
            <p><strong>文件大小：</strong>{formatFileSize(selectedFile.size)}</p>
          </div>
        )}

        {uploading && (
          <div className={styles.progressSection}>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className={styles.progressText}>
              正在分析视频... {progress}%
            </p>
          </div>
        )}

        {error && (
          <div className={styles.errorSection}>
            <p className={styles.errorText}>{error}</p>
          </div>
        )}

        {!uploading && selectedFile && (
          <button
            className={styles.uploadButton}
            onClick={handleUpload}
          >
            开始分析
          </button>
        )}
      </div>

      {analysisResult && (
        <div className={styles.resultsSection}>
          <h3 className={styles.resultsTitle}>分析结果</h3>

          <div className={styles.viewToggleContainer}>
            <button
              className={`${styles.toggleButton} ${activeView === "compass" ? styles.activeToggle : ""}`}
              onClick={() => setActiveView("compass")}
            >
              价值罗盘
            </button>
            <button
              className={`${styles.toggleButton} ${activeView === "positioning" ? styles.activeToggle : ""}`}
              onClick={() => setActiveView("positioning")}
            >
              信息提取
            </button>
          </div>
          
          <div className={styles.videoInfo}>
            <h4>视频信息</h4>
            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>文件名：</span>
                <span>{analysisResult.video_info.filename}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>时长：</span>
                <span>{formatDuration(analysisResult.video_info.duration)}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>分辨率：</span>
                <span>{analysisResult.video_info.resolution}</span>
              </div>
              <div className={styles.infoItem}>
                <span className={styles.infoLabel}>帧率：</span>
                <span>{analysisResult.video_info.fps} FPS</span>
              </div>
            </div>
          </div>

          <div className={styles.processingSummary}>
            <h4>处理摘要</h4>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryItem}>
                <span className={styles.summaryNumber}>{analysisResult.processing_summary.analyzed_frames}</span>
                <span className={styles.summaryLabel}>分析帧数</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryNumber}>{analysisResult.processing_summary.audio_segments}</span>
                <span className={styles.summaryLabel}>音频片段</span>
              </div>
              <div className={styles.summaryItem}>
                <span className={styles.summaryNumber}>{analysisResult.processing_summary.has_audio ? '有' : '无'}</span>
                <span className={styles.summaryLabel}>音频轨道</span>
              </div>
            </div>
          </div>

          {activeView === "positioning" && (
            <>
              <div className={styles.positioningSection}>
                <h4 className={styles.sectionTitle}>关键帧定位结果</h4>
                {analysisResult.frame_analyses.length > 0 ? (
                  <div className={styles.positioningList}>
                    {analysisResult.frame_analyses.map((frame) => (
                      <div key={`${frame.frame_index}-${frame.timestamp}`} className={styles.positioningItem}>
                        <div className={styles.positioningHeader}>
                          <span>帧 #{frame.frame_index + 1}</span>
                          <span>时间戳：{frame.timestamp.toFixed(2)}s</span>
                        </div>
                        <div className={styles.positioningText}>{frame.visual_analysis}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className={styles.positioningEmpty}>暂无关键帧定位结果</div>
                )}
              </div>
              {analysisResult.transcript && (
                <div className={styles.transcriptSection}>
                  <h4>音频转录</h4>
                  <div className={styles.transcriptContent}>
                    {analysisResult.transcript}
                  </div>
                </div>
              )}
            </>
          )}

          {/* 12维度评分图表 */}
          {activeView === "compass" && analysisResult.fusion_result.scores && (
            <>
              <div className={styles.chartSection}>
                <h4 className={styles.sectionTitle}>价值观雷达图</h4>
                <div className={styles.chartContainer}>
                  <RadarChart scoresByModel={{ '视频分析': analysisResult.fusion_result.scores }} />
                </div>
              </div>
              
              <div className={styles.tableSection}>
                <div className={styles.tableContainer}>
                  <DimensionTable scoresByModel={{ '视频分析': analysisResult.fusion_result.scores }} />
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoUploadSection;
