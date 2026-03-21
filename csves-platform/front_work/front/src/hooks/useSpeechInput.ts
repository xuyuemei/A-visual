import { useEffect, useMemo, useRef, useState } from "react";

// Chrome: window.webkitSpeechRecognition
type SpeechRecognitionType = any;

export function useSpeechInput(lang: string = "zh-CN") {
  const recognitionRef = useRef<SpeechRecognitionType | null>(null);

  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [finalText, setFinalText] = useState("");
  const [interimText, setInterimText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const SpeechRecognitionCtor = useMemo(() => {
    const w = window as any;
    return w.SpeechRecognition || w.webkitSpeechRecognition || null;
  }, []);

  useEffect(() => {
    setSupported(!!SpeechRecognitionCtor);
  }, [SpeechRecognitionCtor]);

  const start = () => {
    setError(null);
    setFinalText("");
    setInterimText("");

    if (!SpeechRecognitionCtor) {
      setSupported(false);
      setError("当前浏览器不支持语音识别（建议 Chrome）。");
      return;
    }

    // 如果已有实例，先 stop 掉
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      recognitionRef.current = null;
    }

    const recog = new SpeechRecognitionCtor();
    recognitionRef.current = recog;

    recog.lang = lang;
    recog.continuous = false;       // 一次录音一段（更符合你“确认添加”流程）
    recog.interimResults = true;    // 允许临时转写
    recog.maxAlternatives = 1;

    recog.onstart = () => setListening(true);

    recog.onresult = (event: any) => {
      let interim = "";
      let final = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        const transcript = (res?.[0]?.transcript || "").trim();
        if (!transcript) continue;

        if (res.isFinal) final += transcript;
        else interim += transcript;
      }

      if (interim) setInterimText(interim);
      if (final) {
        setFinalText((prev) => (prev ? prev + " " + final : final));
        setInterimText("");
      }
    };

    recog.onerror = (e: any) => {
      // 常见：not-allowed / service-not-allowed / no-speech / network
      setError(`语音识别失败：${e?.error || "unknown"}`);
      setListening(false);
    };

    recog.onend = () => {
      setListening(false);
      setInterimText("");
    };

    try {
      recog.start();
    } catch (e: any) {
      setError(`无法启动语音识别：${e?.message || e}`);
      setListening(false);
    }
  };

  const stop = () => {
    try {
      recognitionRef.current?.stop();
    } catch {}
  };

  const reset = () => {
    setFinalText("");
    setInterimText("");
    setError(null);
  };

  return { supported, listening, finalText, interimText, error, start, stop, reset };
}
