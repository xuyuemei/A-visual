# app/services/text_score_service.py
from typing import List, Dict, Any
import numpy as np
import re
from app.utils.score_calculator import load_scoring_model, score_answer

LABEL_NAMES = [
    "富强", "民主", "文明", "和谐", "自由", "平等",
    "公正", "法治", "爱国", "敬业", "诚信", "友善"
]

# ✅ 缓存评分模型：避免每次请求都 load（非常重要）
_SCORER = {"tokenizer": None, "model": None, "device": None}

# 默认阈值（0-10 分制），实际会根据当前文本分数尺度动态调整
LOW_SCORE_THRESHOLD = 3.5
HIGH_RISK_THRESHOLD = 2.8

RISK_KEYWORDS = {
    "violence": ["暴力", "杀人", "要杀人", "打死", "殴打", "报复", "血腥", "伤害", "杀"],
    "hate": ["仇恨", "歧视", "侮辱", "排斥", "敌视"],
    "fraud": ["诈骗", "骗", "造假", "伪造", "洗钱", "刷单"],
    "crime": ["违法", "犯罪", "赌博", "毒品", "走私"],
    "extreme": ["极端", "煽动", "暴恐", "恐袭"],
}


def _get_scoring_model():
    if _SCORER["model"] is None:
        tokenizer, model, device = load_scoring_model()
        _SCORER["tokenizer"] = tokenizer
        _SCORER["model"] = model
        _SCORER["device"] = device
        print("✅ text_score_service: 评分模型已加载并缓存")
    return _SCORER["tokenizer"], _SCORER["model"], _SCORER["device"]


def _to_list(scores):
    """兼容 torch / numpy / list"""
    # torch tensor
    if hasattr(scores, "detach") and callable(scores.detach):
        return scores.detach().cpu().tolist()
    # numpy array
    if hasattr(scores, "tolist") and callable(scores.tolist):
        return scores.tolist()
    return list(scores)


def _score_one_text(text: str) -> Dict[str, float]:
    text = (text or "").strip()
    if not text:
        raise ValueError("text 不能为空")

    tokenizer, model, device = _get_scoring_model()
    scores = score_answer(tokenizer, model, device, text)
    scores_list = _to_list(scores)

    if len(scores_list) != 12:
        raise RuntimeError(f"评分输出维度异常：{len(scores_list)}（期望12）")

    scores_list = [float(x) for x in scores_list]
    return dict(zip(LABEL_NAMES, scores_list))


def score_text(text: str) -> Dict[str, Any]:
    """
    单条文本
    输出：{"scores": {...}}
    """
    score_dict = _score_one_text(text)
    return {"scores": score_dict}


def score_texts(texts: List[str]) -> Dict[str, Any]:
    """
    多条文本：返回聚合平均分（scores） + 可选每条明细（results）
    输出：
      {
        "results": [ { "text": "...", "scores": {...} }, ... ],
        "scores": { ...平均分... },
        "count": N
      }
    """
    if not isinstance(texts, list):
        raise ValueError("texts 必须是 list")

    clean_texts = [str(t).strip() for t in texts if str(t).strip()]
    if not clean_texts:
        raise ValueError("texts 不能为空")

    all_scores = np.zeros(12, dtype=np.float64)
    results = []

    for t in clean_texts:
        s = _score_one_text(t)  # dict
        results.append({"text": t, "scores": s})
        all_scores += np.array([s[k] for k in LABEL_NAMES], dtype=np.float64)

    avg = (all_scores / max(len(clean_texts), 1)).tolist()
    avg = [float(x) for x in avg]
    avg_dict = dict(zip(LABEL_NAMES, avg))

    return {
        "results": results,      # ✅ 给前端兜底：即使不展示，也不会缺字段报错
        "scores": avg_dict,      # ✅ 你最终雷达图/表格用这个（总分/平均分）
        "count": len(clean_texts)
    }


def _split_sentences_with_spans(text: str):
    """按中文标点切句，并保留每句在原文中的字符区间"""
    spans = []
    if not text:
        return spans

    pattern = re.compile(r"[^。！？!?；;\n]+[。！？!?；;\n]?")
    for match in pattern.finditer(text):
        sentence = match.group(0).strip()
        if sentence:
            spans.append({
                "text": sentence,
                "start_char": match.start(),
                "end_char": match.end(),
            })
    return spans


def _resolve_thresholds(scores: Dict[str, float]):
    """
    根据分数尺度自动决定阈值：
    - 若最大分 <= 1.2，视为 0-1 分制
    - 否则视为 0-10 分制
    """
    if not scores:
        return LOW_SCORE_THRESHOLD, HIGH_RISK_THRESHOLD

    max_score = max(float(v) for v in scores.values())
    if max_score <= 1.2:
        # 0-1 分制阈值（收紧 high 判定，减少误报）
        return 0.25, 0.15

    # 0-10 分制阈值
    return LOW_SCORE_THRESHOLD, HIGH_RISK_THRESHOLD


def _low_dimensions(scores: Dict[str, float], low_threshold: float):
    lows = []
    for dim, val in scores.items():
        try:
            score_val = float(val)
            if score_val < low_threshold:
                lows.append({"dimension": dim, "score": round(score_val, 4)})
        except Exception:
            continue
    lows.sort(key=lambda x: x["score"])
    return lows


def _risk_level_from_scores(
    scores: Dict[str, float],
    low_dims_count: int,
    high_threshold: float,
    low_threshold: float,
):
    if not scores:
        return "unknown"

    values = [float(v) for v in scores.values()]
    severe_count = sum(1 for v in values if v < high_threshold)
    low_ratio = low_dims_count / max(len(values), 1)

    # 避免“全部高风险”误判：只有严重低分非常集中时才判 high
    if severe_count >= 6 or (severe_count >= 4 and low_ratio >= 0.75):
        return "high"

    if severe_count >= 2 or low_ratio >= 0.45:
        return "medium"

    # 轻微低分但不集中，按 normal 处理
    if low_dims_count > 0 and all(v >= low_threshold * 0.85 for v in values):
        return "normal"

    return "normal"


def _extract_keyword_hits(text: str):
    raw_hits = []
    if not text:
        return raw_hits

    for category, keywords in RISK_KEYWORDS.items():
        # 长词优先，避免“杀”覆盖“杀人”的定位表达
        for keyword in sorted(set(keywords), key=len, reverse=True):
            for m in re.finditer(re.escape(keyword), text):
                raw_hits.append({
                    "keyword": keyword,
                    "category": category,
                    "start_char": m.start(),
                    "end_char": m.end(),
                    "matched_text": text[m.start():m.end()],
                })

    # 去重与去重叠：同一区域优先保留更长词
    raw_hits.sort(key=lambda x: (x["start_char"], -(x["end_char"] - x["start_char"])))
    hits = []
    for hit in raw_hits:
        overlapped = False
        for kept in hits:
            if not (hit["end_char"] <= kept["start_char"] or hit["start_char"] >= kept["end_char"]):
                overlapped = True
                break
        if not overlapped:
            hits.append(hit)

    hits.sort(key=lambda x: (x["start_char"], x["end_char"]))
    return hits


def score_text_with_localization(text: str) -> Dict[str, Any]:
    """
    文本定位：
      1) 整体12维评分
      2) 句子级定位（哪句低分）
      3) 关键词级定位（哪个词命中风险词典）
      4) 关键词窗口评分（利用评估器给词周边短句打分）
    """
    content = (text or "").strip()
    if not content:
        raise ValueError("text 不能为空")

    overall_scores = _score_one_text(content)
    low_threshold, high_threshold = _resolve_thresholds(overall_scores)
    overall_low_dims = _low_dimensions(overall_scores, low_threshold)
    overall_risk = _risk_level_from_scores(
        overall_scores,
        len(overall_low_dims),
        high_threshold,
        low_threshold,
    )

    # 句子级评分定位
    sentence_spans = _split_sentences_with_spans(content)
    sentence_risks = []
    for idx, item in enumerate(sentence_spans):
        s_text = item["text"]
        try:
            s_scores = _score_one_text(s_text)
            s_low = _low_dimensions(s_scores, low_threshold)
            sentence_risks.append({
                "index": idx,
                "text": s_text,
                "start_char": item["start_char"],
                "end_char": item["end_char"],
                "scores": s_scores,
                "low_dimensions": s_low,
                "risk_level": _risk_level_from_scores(
                    s_scores,
                    len(s_low),
                    high_threshold,
                    low_threshold,
                ),
            })
        except Exception:
            continue

    sentence_risks.sort(key=lambda x: min(float(v) for v in x["scores"].values()) if x.get("scores") else 999)

    # 关键词命中 + 词级窗口评分（限制数量，避免过慢）
    keyword_hits = _extract_keyword_hits(content)
    keyword_localizations = []
    max_keyword_eval = 30
    for i, hit in enumerate(keyword_hits[:max_keyword_eval]):
        left = max(0, hit["start_char"] - 12)
        right = min(len(content), hit["end_char"] + 12)
        window_text = content[left:right].strip()

        try:
            w_scores = _score_one_text(window_text)
            w_low = _low_dimensions(w_scores, low_threshold)
            keyword_localizations.append({
                **hit,
                "window_text": window_text,
                "window_start_char": left,
                "window_end_char": right,
                "scores": w_scores,
                "low_dimensions": w_low,
                "risk_level": _risk_level_from_scores(
                    w_scores,
                    len(w_low),
                    high_threshold,
                    low_threshold,
                ),
            })
        except Exception:
            keyword_localizations.append({
                **hit,
                "window_text": window_text,
                "window_start_char": left,
                "window_end_char": right,
                "scores": {},
                "low_dimensions": [],
                "risk_level": "unknown",
            })

    high_risk_sentences = [s for s in sentence_risks if s.get("risk_level") == "high"]
    medium_risk_sentences = [s for s in sentence_risks if s.get("risk_level") == "medium"]

    # 句子级与关键词命中综合修正整体风险，避免仅凭整体12维低分导致全 high
    if len(high_risk_sentences) >= 2:
        fused_overall_risk = "high"
    elif len(high_risk_sentences) == 1:
        fused_overall_risk = "high" if len(keyword_hits) > 0 else "medium"
    elif len(medium_risk_sentences) > 0 or len(keyword_hits) > 0:
        fused_overall_risk = "medium"
    else:
        fused_overall_risk = overall_risk

    summary = {
        "sentence_count": len(sentence_risks),
        "keyword_hit_count": len(keyword_hits),
        "high_risk_sentence_count": len(high_risk_sentences),
        "medium_risk_sentence_count": len(medium_risk_sentences),
        "overall_risk_level": fused_overall_risk,
    }

    return {
        "scores": overall_scores,
        "overall_low_dimensions": overall_low_dims,
        "overall_risk_level": fused_overall_risk,
        "sentence_risks": sentence_risks,
        "keyword_localizations": keyword_localizations,
        "summary": summary,
    }


def score_texts_with_localization(texts: List[str]) -> Dict[str, Any]:
    """
    批量文本定位：对每条文本分别输出定位结果。
    """
    if not isinstance(texts, list):
        raise ValueError("texts 必须是 list")

    clean_texts = [str(t).strip() for t in texts if str(t).strip()]
    if not clean_texts:
        raise ValueError("texts 不能为空")

    results = []
    for idx, text in enumerate(clean_texts):
        loc = score_text_with_localization(text)
        results.append({
            "index": idx,
            "text": text,
            "localization": loc,
        })

    return {
        "results": results,
        "count": len(results),
    }
