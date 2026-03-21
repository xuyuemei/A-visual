import React, { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import styles from "./VoiceInputModal.module.css";

type Props = {
  open: boolean;
  onClose: () => void;
  onConfirm: (text: string) => void;
  lang?: string; // "zh-CN"
};

type SpeechRecognitionCtor = new () => SpeechRecognition;

const VoiceInputModal: React.FC<Props> = ({ open, onClose, onConfirm, lang = "zh-CN" }) => {
  const RecognitionCtor = useMemo<SpeechRecognitionCtor | null>(() => {
    if (typeof window === "undefined") return null;
    // ✅ 依赖 src/types/speech.d.ts 的全局声明
    const ctor = (window.SpeechRecognition || window.webkitSpeechRecognition || null) as
      | SpeechRecognitionCtor
      | null;
    return ctor;
  }, []);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const isRecordingRef = useRef(false);
  const manualStopRef = useRef(false);

  const [supported, setSupported] = useState(true);
  const [recording, setRecording] = useState(false);
  const [finalText, setFinalText] = useState("");
  const [interimText, setInterimText] = useState("");
  const [error, setError] = useState<string | null>(null);

  // 初始化 recognition（只做一次）
  useEffect(() => {
    if (!RecognitionCtor) {
      setSupported(false);
      return;
    }

    const rec = new RecognitionCtor();
    rec.lang = lang;
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    rec.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      let finalChunk = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        const txt = res[0]?.transcript ?? "";
        if (res.isFinal) finalChunk += txt;
        else interim += txt;
      }

      if (finalChunk) setFinalText((prev) => (prev + finalChunk).replace(/\s+/g, " "));
      setInterimText(interim.replace(/\s+/g, " "));
    };

    rec.onerror = (e: SpeechRecognitionErrorEvent) => {
      // 常见：not-allowed / service-not-allowed / no-speech / audio-capture
      setError(e?.error ? `语音识别错误：${e.error}` : "语音识别发生错误");
    };

    rec.onend = () => {
      // 浏览器会因静音/策略自动 end；如果仍处于录音态且不是手动 stop，就自动续上
      if (isRecordingRef.current && !manualStopRef.current) {
        try {
          rec.start();
        } catch {
          setTimeout(() => {
            try {
              rec.start();
            } catch {}
          }, 250);
        }
      }
    };

    recognitionRef.current = rec;

    // 组件卸载时：停止并释放
    return () => {
      try {
        rec.onresult = null;
        rec.onerror = null;
        rec.onend = null;
        rec.stop();
      } catch {}
      recognitionRef.current = null;
    };
  }, [RecognitionCtor, lang]);

  // 弹窗开关：关闭时确保停止并清空
  useEffect(() => {
    if (!open) {
      stop();
      setFinalText("");
      setInterimText("");
      setError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const start = async () => {
    setError(null);

    if (!recognitionRef.current) {
      setSupported(false);
      return;
    }

    // 先请求麦克风权限
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("无法获取麦克风权限，请在浏览器设置中允许麦克风访问。");
      return;
    }

    manualStopRef.current = false;
    isRecordingRef.current = true;
    setRecording(true);

    try {
      recognitionRef.current.start();
    } catch {
      // 已 start 可能会抛异常，忽略
    }
  };

  const stop = () => {
    manualStopRef.current = true;
    isRecordingRef.current = false;
    setRecording(false);
    setInterimText("");

    try {
      recognitionRef.current?.stop();
    } catch {}
  };

  const confirm = () => {
    const merged = (finalText + (interimText ? " " + interimText : "")).trim();
    if (!merged) {
      setError("还没有识别到内容，请先开始录入并讲话。");
      return;
    }
    onConfirm(merged);
    onClose();
  };

  const clear = () => {
    setFinalText("");
    setInterimText("");
    setError(null);
  };

  if (!open) return null;

  return (
    <AnimatePresence>
      <motion.div
        className={styles.overlay}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className={styles.modal}
          initial={{ opacity: 0, y: 18, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 10, scale: 0.98 }}
          transition={{ duration: 0.18 }}
        >
          <div className={styles.header}>
            <div>
              <div className={styles.title}>语音输入</div>
              <div className={styles.subtitle}>
                点击开始后持续识别，只有你点“暂停”才会停止（浏览器中途自动停会自动续上）。
              </div>
            </div>

            <button className={styles.closeBtn} onClick={onClose} aria-label="close">
              ✕
            </button>
          </div>

          {!supported && (
            <div className={styles.error}>
              当前浏览器不支持 SpeechRecognition。建议使用 Chrome/Edge 桌面版。
            </div>
          )}

          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.center}>
            <div className={`${styles.mic} ${recording ? styles.micActive : ""}`}>
              <div className={styles.micInner} />
            </div>

            <div className={styles.statusRow}>
              <span className={`${styles.dot} ${recording ? styles.dotOn : ""}`} />
              <span className={styles.statusText}>{recording ? "正在识别中…" : "未开始"}</span>
            </div>
          </div>

          <div className={styles.preview}>
            <div className={styles.previewLabel}>识别内容预览</div>
            <div className={styles.previewBox}>
              <span>{finalText}</span>
              {interimText && <span className={styles.interim}> {interimText}</span>}
              {!finalText && !interimText && <span className={styles.placeholder}>这里会显示识别到的文字…</span>}
            </div>
          </div>

          <div className={styles.actions}>
            {!recording ? (
              <button className={styles.primary} onClick={start} disabled={!supported}>
                开始录入
              </button>
            ) : (
              <button className={styles.primary} onClick={stop}>
                暂停
              </button>
            )}

            <button className={styles.secondary} onClick={clear} disabled={recording}>
              清空
            </button>

            <div className={styles.spacer} />

            <button className={styles.secondary} onClick={onClose}>
              取消
            </button>

            <button className={styles.primary} onClick={confirm} disabled={!supported}>
              确认插入
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default VoiceInputModal;
