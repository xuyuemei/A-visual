import torch
import numpy as np
import re
import traceback
from typing import List, Dict, Any
from captum.attr import IntegratedGradients
from app.utils.score_calculator import load_scoring_model, score_answer

LABEL_NAMES = [
    "富强", "民主", "文明", "和谐", "自由", "平等",
    "公正", "法治", "爱国", "敬业", "诚信", "友善"
]

_SCORER = {"tokenizer": None, "model": None, "device": None, "ig": None}

LOW_SCORE_THRESHOLD = 3.5
HIGH_RISK_THRESHOLD = 2.8

RISK_KEYWORDS = {
    "violence": ["暴力", "杀人", "要杀人", "打死", "殴打", "报复", "血腥", "伤害", "杀"],
    "hate": ["仇恨", "歧视", "侮辱", "排斥", "敌视"],
    "fraud": ["诈骗", "骗", "造假", "伪造", "洗钱", "刷单"],
    "crime": ["违法", "犯罪", "赌博", "毒品", "走私"],
    "extreme": ["极端", "煽动", "暴恐", "恐袭"],
}

PUNCTUATIONS = set("，。！？；：（）“”《》、.,!?;:()\"' ")
STOP_WORDS = set(["的", "了", "在", "是", "并", "从", "而", "于", "以", "这", "那", "有"])


# --- 1. 资源管理 ---

def _get_resources():
    if _SCORER["model"] is None:
        tokenizer, model, device = load_scoring_model()
        _SCORER["tokenizer"] = tokenizer
        _SCORER["model"] = model
        _SCORER["device"] = device
        model.eval()

        def forward_func(inputs_embeds):
            outputs = model(inputs_embeds=inputs_embeds)
            logits = outputs.logits if hasattr(outputs, "logits") else outputs
            return logits

        _SCORER["ig"] = IntegratedGradients(forward_func)
        print("✅ text_score_service: 解释器初始化成功")

    return _SCORER["tokenizer"], _SCORER["model"], _SCORER["device"], _SCORER["ig"]


# --- 2. 文本切句与 span 对齐 ---

def _split_text_with_spans(text: str) -> List[Dict[str, Any]]:
    """
    把全文切成句子，并保留每句在原文中的字符区间。
    返回:
    [
        {"text": "...", "start": 0, "end": 12},
        ...
    ]
    """
    if not text:
        return []

    pattern = re.compile(r'.*?(?:[。！？!?；;\n]|$)', re.S)
    results = []

    for m in pattern.finditer(text):
        sent = m.group(0)
        if not sent:
            continue

        start, end = m.start(), m.end()
        stripped = sent.strip()
        if not stripped:
            continue

        left_trim = len(sent) - len(sent.lstrip())
        right_trim = len(sent) - len(sent.rstrip())
        real_start = start + left_trim
        real_end = end - right_trim

        if real_start < real_end:
            results.append({
                "text": text[real_start:real_end],
                "start": real_start,
                "end": real_end
            })

    return results


def _merge_token_pieces(token_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将相邻且连续的 token 片段做轻量合并，减少碎片。
    """
    if not token_evidence:
        return []

    merged = [token_evidence[0].copy()]

    for item in token_evidence[1:]:
        prev = merged[-1]

        can_merge = (
            item["start"] == prev["end"] and
            prev["t"].strip() != "" and
            item["t"].strip() != ""
        )

        if can_merge:
            prev["t"] += item["t"]

            prev_len = max(prev["end"] - prev["start"], 1)
            item_len = max(item["end"] - item["start"], 1)
            total_len = prev_len + item_len

            prev["s"] = round(
                (prev["s"] * prev_len + item["s"] * item_len) / total_len,
                4
            )
            prev["end"] = item["end"]
        else:
            merged.append(item.copy())

    return merged


# --- 3. 核心算法：token 级证据提取 ---

def _compute_visual_evidence(text: str, target_dim_idx: int) -> List[Dict]:
    """
    计算 token 级证据：
    - 使用 offset_mapping 精准对齐原文
    - 直接从原文切片拿 token 文本
    - 抑制标点/虚词噪声
    """
    evidence = []

    try:
        tokenizer, model, device, ig = _get_resources()

        encoded = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            return_offsets_mapping=True
        )

        offset_mapping = encoded.pop("offset_mapping")[0].tolist()
        encoded = {k: v.to(device) for k, v in encoded.items()}

        input_ids = encoded["input_ids"]
        embedding_layer = model.get_input_embeddings()
        input_embeds = embedding_layer(input_ids)

        attributions = ig.attribute(
            input_embeds,
            target=int(target_dim_idx),
            n_steps=24,
            internal_batch_size=1
        )

        if attributions is None:
            return []

        raw_weights = attributions.sum(dim=-1).squeeze(0).detach().cpu().numpy()
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0])

        refined_weights = []
        for token, weight, (start, end) in zip(tokens, raw_weights, offset_mapping):
            if start == end:
                refined_weights.append(0.0)
                continue

            piece_text = text[start:end]
            clean_t = piece_text.strip()

            if (not clean_t) or (clean_t in PUNCTUATIONS) or (clean_t in STOP_WORDS):
                refined_weights.append(float(weight) * 0.15)
            else:
                refined_weights.append(float(weight))

        refined_weights = np.array(refined_weights, dtype=np.float32)

        max_abs = float(np.max(np.abs(refined_weights))) if len(refined_weights) else 0.0
        if max_abs <= 1e-8:
            normalized = refined_weights
        else:
            normalized = refined_weights / max_abs

        final_weights = np.sign(normalized) * (np.abs(normalized) ** 0.85)

        for token, weight, (start, end) in zip(tokens, final_weights, offset_mapping):
            if start == end:
                continue

            if token in [
                tokenizer.cls_token, tokenizer.sep_token, tokenizer.pad_token,
                "<s>", "</s>", "<pad>"
            ]:
                continue

            piece_text = text[start:end]
            if not piece_text:
                continue

            evidence.append({
                "t": piece_text,
                "s": float(round(float(weight), 4)),
                "start": int(start),
                "end": int(end)
            })

        evidence = _merge_token_pieces(evidence)

    except Exception as e:
        print(f"❌ IG计算核心报错: {str(e)}")
        traceback.print_exc()

    return evidence


# --- 4. 句子级证据评分 ---

def _sentence_overlap(tok: Dict[str, Any], sent: Dict[str, Any]) -> int:
    tok_start = tok.get("start", 0)
    tok_end = tok.get("end", 0)
    sent_start = sent["start"]
    sent_end = sent["end"]
    return max(0, min(sent_end, tok_end) - max(sent_start, tok_start))


def _collect_sentence_tokens(tokens_evidence: List[Dict], sent: Dict[str, Any]) -> List[Dict]:
    sent_tokens = []
    for tok in tokens_evidence:
        if _sentence_overlap(tok, sent) > 0:
            sent_tokens.append(tok)
    return sent_tokens


def _score_sentence_evidence(sent_tokens: List[Dict], prefer_positive: bool = True) -> Dict[str, float]:
    """
    对一句话内部的 token 贡献做更稳健的证据评分。
    目标是找“最有说服力”的证据句，而不是简单平均强度最高。
    """
    if not sent_tokens:
        return {
            "score": 0.0,
            "positive_sum": 0.0,
            "negative_sum": 0.0,
            "positive_density": 0.0,
            "top_k_positive_sum": 0.0,
            "token_count": 0.0
        }

    weights = [float(x["s"]) for x in sent_tokens]
    positives = [max(w, 0.0) for w in weights]
    negatives = [-min(w, 0.0) for w in weights]

    positive_sum = sum(positives)
    negative_sum = sum(negatives)

    total_count = max(len(weights), 1)
    pos_count = sum(1 for w in weights if w > 0)
    neg_count = sum(1 for w in weights if w < 0)

    positive_density = pos_count / total_count
    negative_density = neg_count / total_count

    top_k = 3
    top_k_positive_sum = sum(sorted(positives, reverse=True)[:top_k])
    top_k_negative_sum = sum(sorted(negatives, reverse=True)[:top_k])

    # 轻微句长惩罚：太长的句子虽然总和大，但不一定最有说服力
    length_penalty = min(total_count / 18.0, 1.2)

    if prefer_positive:
        final_score = (
            0.50 * positive_sum
            + 0.25 * top_k_positive_sum
            + 0.20 * positive_density
            - 0.18 * negative_sum
            - 0.05 * length_penalty
        )
    else:
        final_score = (
            0.50 * negative_sum
            + 0.25 * top_k_negative_sum
            + 0.20 * negative_density
            - 0.18 * positive_sum
            - 0.05 * length_penalty
        )

    return {
        "score": round(float(final_score), 4),
        "positive_sum": round(float(positive_sum), 4),
        "negative_sum": round(float(negative_sum), 4),
        "positive_density": round(float(positive_density), 4),
        "top_k_positive_sum": round(float(top_k_positive_sum), 4),
        "token_count": float(total_count)
    }


def _normalize_text_for_dedup(text: str) -> str:
    return re.sub(r"[\s\"'“”‘’`]+", "", text or "")


def _is_too_similar(a: str, b: str) -> bool:
    """
    简单去重：如果两个句子去掉空白后，一个明显包含另一个，就认为太相似。
    """
    na = _normalize_text_for_dedup(a)
    nb = _normalize_text_for_dedup(b)

    if not na or not nb:
        return False

    if na == nb:
        return True

    short_len = min(len(na), len(nb))
    if short_len == 0:
        return False

    if na in nb or nb in na:
        return True

    return False


def _aggregate_to_sentences(
    tokens_evidence: List[Dict],
    full_text: str,
    prefer_positive: bool = True,
    top_k: int = 3
) -> List[Dict]:
    """
    将 token 证据聚合为句子级证据。
    返回结构保持不变：
    [
        {"text": str, "score": float, "intensity": float},
        ...
    ]
    """
    sentences = _split_text_with_spans(full_text)
    if not sentences or not tokens_evidence:
        return []

    aggregated = []

    for sent in sentences:
        sent_text = (sent["text"] or "").strip()
        if not sent_text:
            continue

        # 太短的句子一般不适合作为“有说服力证据”
        if len(sent_text) < 8:
            continue

        sent_tokens = _collect_sentence_tokens(tokens_evidence, sent)
        if not sent_tokens:
            continue

        metrics = _score_sentence_evidence(sent_tokens, prefer_positive=prefer_positive)

        # 强度不足则过滤
        if metrics["score"] <= 0:
            continue

        if prefer_positive and metrics["positive_sum"] <= 0:
            continue

        if (not prefer_positive) and metrics["negative_sum"] <= 0:
            continue

        aggregated.append({
            "text": sent_text,
            "score": float(metrics["score"]),
            "intensity": float(
                metrics["positive_sum"] if prefer_positive else metrics["negative_sum"]
            )
        })

    aggregated.sort(key=lambda x: (x["score"], x["intensity"]), reverse=True)

    deduped = []
    for item in aggregated:
        if any(_is_too_similar(item["text"], exist["text"]) for exist in deduped):
            continue
        deduped.append(item)
        if len(deduped) >= top_k:
            break

    return deduped


# --- 5. 辅助功能 ---

def _to_list(scores):
    if hasattr(scores, "detach"):
        return scores.detach().cpu().tolist()
    return scores.tolist() if hasattr(scores, "tolist") else list(scores)


def _score_one_text(text: str) -> Dict[str, float]:
    tokenizer, model, device, _ = _get_resources()
    scores = score_answer(tokenizer, model, device, text)
    scores_list = _to_list(scores)
    return dict(zip(LABEL_NAMES, [float(x) for x in scores_list]))


def _resolve_thresholds(scores: Dict[str, float]):
    max_val = max(float(v) for v in scores.values()) if scores else 0
    return (0.25, 0.15) if max_val <= 1.2 else (LOW_SCORE_THRESHOLD, HIGH_RISK_THRESHOLD)


def _low_dimensions(scores: Dict[str, float], low_threshold: float):
    return sorted(
        [{"dimension": k, "score": round(float(v), 4)} for k, v in scores.items() if float(v) < low_threshold],
        key=lambda x: x["score"]
    )


def _risk_level_from_scores(scores, low_dims_count, high_threshold, low_threshold):
    if not scores:
        return "unknown"
    severe_count = sum(1 for v in scores.values() if float(v) < high_threshold)
    ratio = low_dims_count / len(LABEL_NAMES)
    if severe_count >= 6 or (severe_count >= 4 and ratio >= 0.75):
        return "high"
    if severe_count >= 2 or ratio >= 0.45:
        return "medium"
    return "normal"


def _extract_keyword_hits(text: str):
    raw_hits = []
    for cat, kws in RISK_KEYWORDS.items():
        for kw in kws:
            for m in re.finditer(re.escape(kw), text or ""):
                raw_hits.append({
                    "keyword": kw,
                    "category": cat,
                    "start_char": m.start(),
                    "end_char": m.end()
                })
    return raw_hits


# --- 6. 核心集成接口（保持对前端输出结构不变） ---

def score_text_with_localization(text: str) -> Dict[str, Any]:
    content = (text or "").strip()
    overall_scores = _score_one_text(content)

    low_t, high_t = _resolve_thresholds(overall_scores)
    overall_lows = _low_dimensions(overall_scores, low_t)
    overall_risk = _risk_level_from_scores(overall_scores, len(overall_lows), high_t, low_t)

    visual_evidence = {}

    if overall_scores and content:
        # 只选择最高分维度
        best_dim_name, best_dim_score = max(
            overall_scores.items(),
            key=lambda x: float(x[1])
        )

        best_idx = LABEL_NAMES.index(best_dim_name)

        tokens_ev = _compute_visual_evidence(content, best_idx)

        # 最高分维度，固定找“支撑高分”的正向证据
        top_sentences = _aggregate_to_sentences(
            tokens_ev,
            content,
            prefer_positive=True,
            top_k=3
        )

        visual_evidence[best_dim_name] = {
            "tokens": [{"t": x["t"], "s": x["s"]} for x in tokens_ev],
            "top_sentences": top_sentences
        }

    return {
        "scores": overall_scores,
        "overall_low_dimensions": overall_lows,
        "overall_risk_level": overall_risk,
        "sentence_risks": [],
        "keyword_localizations": _extract_keyword_hits(content),
        "visual_evidence": visual_evidence
    }


# --- 7. 批量处理接口（不改） ---

def score_texts_with_localization(texts: List[str]) -> Dict[str, Any]:
    results = []
    for i, t in enumerate(texts):
        if not str(t).strip():
            continue
        try:
            results.append({
                "index": i,
                "text": t,
                "localization": score_text_with_localization(t)
            })
        except Exception as e:
            print(f"❌ 批量失败: {e}")
    return {"results": results, "count": len(results)}


def score_text(text: str):
    return {"scores": _score_one_text(text)}


def score_texts(texts: List[str]):
    res = [list(_score_one_text(t).values()) for t in texts if t.strip()]
    avg = dict(zip(LABEL_NAMES, np.mean(res, axis=0).tolist())) if res else {}
    return {"results": res, "scores": avg}