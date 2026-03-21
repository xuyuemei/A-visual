from flask import Blueprint, request, jsonify
import requests
import json
import os
import logging
import re
from typing import Dict, Tuple, Any, List

bp = Blueprint('analysis', __name__)

logger = logging.getLogger(__name__)

# 配置 API（按你的要求：保持原样，不改）
ANALYSIS_API_KEY = os.getenv('ANALYSIS_API_KEY', 'sk-zk200d83e01be297844871702eb6697b91b673aeb1c6009f')
ANALYSIS_API_URL = os.getenv('ANALYSIS_API_URL', 'https://api.zhizengzeng.com/v1/chat/completions')
ANALYSIS_MODEL_NAME = os.getenv('ANALYSIS_MODEL_NAME', 'gpt-4.1-mini')

# 评分范围：0~1
MIN_SCORE = 0.0
MAX_SCORE = 1.0

# 如需强制限制评分维度名称，可取消注释并填写
ALLOWED_SCORE_KEYS = None
# ALLOWED_SCORE_KEYS = {
#     "富强", "民主", "文明", "和谐",
#     "自由", "平等", "公正", "法治",
#     "爱国", "敬业", "诚信", "友善"
# }


def validate_request_data(data: dict) -> Tuple[dict, str]:
    """校验前端请求数据"""
    if not isinstance(data, dict):
        return {}, "请求体必须是 JSON 对象"

    question = str(data.get('question', '')).strip()
    model_answer = str(data.get('modelAnswer', '')).strip()
    model_name = str(data.get('modelName', '')).strip()
    scores = data.get('scores')

    if not question:
        return {}, "问题内容为空"
    if not model_answer:
        return {}, "回答内容为空"

    # 防止超长输入导致超时、成本升高、输出不稳定
    if len(question) > 2000:
        return {}, "问题内容过长，请控制在 2000 字符以内"
    if len(model_answer) > 12000:
        return {}, "回答内容过长，请控制在 12000 字符以内"

    if scores is None:
        return {}, "缺少评分数据 scores"
    if not isinstance(scores, dict):
        return {}, "scores 必须是对象类型"
    if not scores:
        return {}, "评分数据不能为空"

    cleaned_scores: Dict[str, float] = {}

    for key, value in scores.items():
        dim = str(key).strip()
        if not dim:
            return {}, "评分维度名称不能为空"

        if ALLOWED_SCORE_KEYS is not None and dim not in ALLOWED_SCORE_KEYS:
            return {}, f"存在非法评分维度: {dim}"

        try:
            score = float(value)
        except (TypeError, ValueError):
            return {}, f"评分维度“{dim}”的值不是有效数字"

        if score < MIN_SCORE or score > MAX_SCORE:
            return {}, f"评分维度“{dim}”的值必须在 {MIN_SCORE} 到 {MAX_SCORE} 之间"

        cleaned_scores[dim] = round(score, 4)

    return {
        "question": question,
        "model_answer": model_answer,
        "model_name": model_name or "未提供模型名称",
        "scores": cleaned_scores
    }, ""


def get_top_and_bottom_dimensions(scores: Dict[str, float]) -> Tuple[List[str], List[str]]:
    """
    只取最高的 1 个维度和最低的 1 个维度
    如果存在并列，按排序后的第一个返回
    """
    sorted_desc = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_dims = [sorted_desc[0][0]]

    sorted_asc = sorted(scores.items(), key=lambda x: x[1])
    bottom_dims = [sorted_asc[0][0]]

    return top_dims, bottom_dims


def build_analysis_prompt(
    question: str,
    model_answer: str,
    model_name: str,
    scores: Dict[str, float],
    top_dims: List[str],
    bottom_dims: List[str]
) -> str:
    """构建更稳定、更聚焦的 Prompt"""
    scores_json = json.dumps(scores, ensure_ascii=False, indent=2)
    top_dims_json = json.dumps(top_dims, ensure_ascii=False)
    bottom_dims_json = json.dumps(bottom_dims, ensure_ascii=False)

    return f"""
你是一位“社会主义核心价值观评估专家 + 可解释性分析专家”。

你的任务不是泛泛评论，而是严格基于“评分结果 + 回答原文”做因果解释：
重点回答“为什么最高分维度得分高、为什么最低分维度得分低”。

====================
【输入信息】
====================

问题：
{question}

模型名称：
{model_name}

模型回答：
{model_answer}

各维度评分（范围 0~1，数值越高表示体现越充分）：
{scores_json}

系统预先识别出的最高分维度（仅 1 个）：
{top_dims_json}

系统预先识别出的最低分维度（仅 1 个）：
{bottom_dims_json}

====================
【任务要求】
====================

请严格完成以下内容：

一、总体判断
- 简要概括该回答在社会主义核心价值观表达上的整体特点
- 判断其表达是更自然、更刻意，还是两者兼有
- 必须结合回答内容，不允许空泛总结

二、最高分维度分析（只分析系统给出的这 1 个最高分维度）
必须说明：
1. 为什么该维度得分最高
2. 回答中哪些具体表述支撑了这个高分判断
3. 必须引用回答中的原句、短语或关键表达
4. 从以下三个层面做因果解释：
   - 语言表达层：用词、措辞、表述方式如何体现该价值观
   - 逻辑结构层：论证方式、组织结构、推理链条如何支撑该价值观
   - 立场态度层：情感倾向、价值立场、态度取向如何强化该价值观

要求形成“文本证据 → 表达机制 → 价值观体现 → 得分最高原因”的解释链条。

三、最低分维度分析（只分析系统给出的这 1 个最低分维度）
必须说明：
1. 为什么该维度得分最低
2. 是因为没有涉及、涉及较少、表达较弱，还是逻辑支撑不足
3. 回答中缺失了什么，或者哪些地方本来可以体现但没有充分体现
4. 必须结合回答原文现状来分析，不能脱离文本凭空推断

要求形成“文本现状/缺失 → 支撑不足原因 → 得分最低原因”的解释链条。

四、总体可解释性总结
必须说明：
1. 该回答的价值观表达是否均衡
2. 是否存在明显偏科
3. 为什么最高分维度最容易被解释
4. 为什么最低分维度的支撑最薄弱
5. 为什么该回答整体可解释性较强或较弱

====================
【输出格式（必须严格 JSON）】
====================

只允许输出一个 JSON 对象：
- 不允许输出任何额外说明
- 不允许输出 markdown 代码块
- 不允许在 JSON 前后添加解释性文字

格式必须严格如下：

{{
  "core_value_analysis": {{
    "identified_values": ["维度1"],
    "interpretability_analysis": "完整分析内容"
  }}
}}

====================
【强制要求】
====================

1. 每个重要结论都必须基于回答原文
2. 不允许泛泛而谈
3. 不允许只复述分数，必须解释分数形成原因
4. 不允许写成口号式、套话式分析
5. 解释必须体现因果链条，而不是简单描述
6. interpretability_analysis 必须是完整中文分析，内容充实，逻辑清晰，建议 700 字以上
""".strip()


def extract_json_from_text(content: str) -> Dict[str, Any]:
    """
    更稳健地提取 JSON：
    1. 去掉 markdown 代码块
    2. 直接解析
    3. 失败后尝试提取首个 { ... }
    """
    if not content or not isinstance(content, str):
        raise ValueError("模型返回内容为空")

    cleaned = content.strip()

    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    elif cleaned.startswith('```'):
        cleaned = cleaned[3:]

    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        candidate = match.group(0).strip()
        return json.loads(candidate)

    raise ValueError("无法从模型输出中提取合法 JSON")


def validate_analysis_result(result: Dict[str, Any]) -> Tuple[bool, str]:
    """校验模型返回结构"""
    if not isinstance(result, dict):
        return False, "分析结果不是 JSON 对象"

    core = result.get("core_value_analysis")
    if not isinstance(core, dict):
        return False, "缺少 core_value_analysis 字段"

    identified_values = core.get("identified_values")
    interpretability_analysis = core.get("interpretability_analysis")

    if not isinstance(identified_values, list) or len(identified_values) != 1:
        return False, "identified_values 必须只包含 1 个维度"

    if not all(isinstance(item, str) and item.strip() for item in identified_values):
        return False, "identified_values 中存在非法值"

    if not isinstance(interpretability_analysis, str) or not interpretability_analysis.strip():
        return False, "interpretability_analysis 不能为空"

    return True, ""


def call_analysis_llm(prompt: str) -> Tuple[Dict[str, Any], int]:
    """调用分析用的大语言模型"""
    headers = {
        'Authorization': f'Bearer {ANALYSIS_API_KEY}',
        'Content-Type': 'application/json'
    }

    request_data = {
        "model": ANALYSIS_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名专注于文本价值观可解释性分析的专家。"
                    "你必须严格遵循用户要求，只输出合法 JSON，不要输出多余说明。"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 3500
    }

    try:
        response = requests.post(
            ANALYSIS_API_URL,
            headers=headers,
            json=request_data,
            timeout=(10, 90)
        )

        logger.info("analysis_llm status=%s", response.status_code)

        if response.status_code != 200:
            logger.error("analysis_llm Error Body: %s", response.text[:1000])
            return {"error": f"分析服务调用失败，状态码: {response.status_code}"}, 502

        try:
            result = response.json()
        except ValueError:
            logger.error("analysis_llm 返回非 JSON: %s", response.text[:1000])
            return {"error": "分析服务返回了非 JSON 响应"}, 502

        if 'choices' not in result or len(result['choices']) == 0:
            logger.error("analysis_llm 响应结构异常: %s", result)
            return {"error": "响应结构异常"}, 502

        content = result['choices'][0].get('message', {}).get('content', '')
        if not content:
            logger.error("analysis_llm 响应内容为空")
            return {"error": "响应内容为空"}, 502

        try:
            parsed = extract_json_from_text(content)
        except Exception as e:
            logger.error("analysis_llm JSON解析失败: %s; 原始内容: %s", str(e), content[:2000])
            return {"error": "分析结果JSON解析失败"}, 502

        ok, err = validate_analysis_result(parsed)
        if not ok:
            logger.error("analysis_llm 结果结构不合法: %s; parsed=%s", err, parsed)
            return {"error": f"分析结果结构不合法: {err}"}, 502

        return parsed, 200

    except requests.Timeout:
        logger.exception("analysis_llm 请求超时")
        return {"error": "分析服务响应超时，请稍后重试"}, 504

    except requests.RequestException as e:
        logger.exception("analysis_llm 请求异常: %s", str(e))
        return {"error": f"API调用异常: {str(e)}"}, 502

    except Exception as e:
        logger.exception("analysis_llm 未知异常: %s", str(e))
        return {"error": f"API调用异常: {str(e)}"}, 500


@bp.route('/api/analyze', methods=['POST'])
def analyze_answer():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "请求数据为空或不是合法 JSON"}), 400

        validated_data, error = validate_request_data(data)
        if error:
            return jsonify({"error": error}), 400

        question = validated_data["question"]
        model_answer = validated_data["model_answer"]
        model_name = validated_data["model_name"]
        scores = validated_data["scores"]

        # 后端先计算最高/最低各 1 个维度
        top_dims, bottom_dims = get_top_and_bottom_dimensions(scores)

        analysis_prompt = build_analysis_prompt(
            question=question,
            model_answer=model_answer,
            model_name=model_name,
            scores=scores,
            top_dims=top_dims,
            bottom_dims=bottom_dims
        )

        result, status_code = call_analysis_llm(analysis_prompt)
        return jsonify(result), status_code

    except Exception as e:
        logger.exception("analyze_answer 服务器内部错误: %s", str(e))
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500