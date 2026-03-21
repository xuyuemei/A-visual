# app/routes/image_analysis.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from app.utils.llm_api import query_api
from app.services.text_score_service import score_text_with_localization

# 创建蓝图
image_analysis_bp = Blueprint("image_analysis", __name__)

# 允许的图片类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _image_to_base64(image: Image.Image, format_name: str):
    buffered = BytesIO()
    image.save(buffered, format=format_name)
    return base64.b64encode(buffered.getvalue()).decode()


def _vision_describe_patch(img_b64: str, format_name: str, patch_prompt: str, max_tokens: int = 220):
    """调用多模态模型描述局部图像区域"""
    from openai import OpenAI

    ZZZ_BASE_URL = os.getenv("ZZZ_BASE_URL", "https://api.zhizengzeng.com/v1")
    # 与整图分析保持一致，避免 patch 调用缺少 Authorization
    ZZZ_API_KEY = os.getenv("ZZZ_API_KEY", "sk-zk237a38360c4056d5097a3b10879eeb35a6914611803eeb")
    if not ZZZ_API_KEY:
        raise ValueError("ZZZ_API_KEY 未配置，无法调用视觉模型")
    client = OpenAI(api_key=ZZZ_API_KEY, base_url=ZZZ_BASE_URL)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": patch_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{format_name.lower()};base64,{img_b64}"},
                },
            ],
        }
    ]

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def _describe_patch_basic(patch: Image.Image):
    """局部区域降级描述：不依赖外部 API，保证定位结果可返回。"""
    arr = np.array(patch.convert("RGB"))
    h, w = arr.shape[:2]

    if arr.size == 0:
        return "局部区域为空，无法提取视觉信息。"

    rgb_mean = arr.mean(axis=(0, 1))
    brightness = float(arr.mean())

    if brightness < 70:
        light_desc = "整体偏暗"
    elif brightness > 180:
        light_desc = "整体偏亮"
    else:
        light_desc = "明暗适中"

    dominant_idx = int(np.argmax(rgb_mean))
    dominant = ["红色", "绿色", "蓝色"][dominant_idx]

    return f"局部区域尺寸{w}x{h}，{light_desc}，主色调偏{dominant}。"


def _generate_candidate_windows(width: int, height: int):
    """生成多尺度、重叠的候选窗口（非固定四宫格）。"""
    windows = []

    # 全图与中心区域
    windows.append((0, 0, width, height))
    cx1, cy1 = int(width * 0.15), int(height * 0.15)
    cx2, cy2 = int(width * 0.85), int(height * 0.85)
    windows.append((cx1, cy1, cx2, cy2))

    # 多尺度滑窗
    scales = [(0.55, 0.55), (0.42, 0.42), (0.30, 0.30), (0.55, 0.35), (0.35, 0.55)]
    for sw, sh in scales:
        win_w = max(int(width * sw), 64)
        win_h = max(int(height * sh), 64)
        step_x = max(int(win_w * 0.4), 32)
        step_y = max(int(win_h * 0.4), 32)

        y = 0
        while y + win_h <= height:
            x = 0
            while x + win_w <= width:
                windows.append((x, y, x + win_w, y + win_h))
                x += step_x
            y += step_y

    # 去重
    uniq = []
    seen = set()
    for w in windows:
        key = (int(w[0]), int(w[1]), int(w[2]), int(w[3]))
        if key not in seen:
            seen.add(key)
            uniq.append(key)
    return uniq


def _iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    if inter == 0:
        return 0.0

    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    union = area_a + area_b - inter
    return inter / max(union, 1)


def _risk_rank(level: str):
    if level == "high":
        return 3
    if level == "medium":
        return 2
    if level == "normal":
        return 1
    return 0


def _nms_blocks(blocks, image_w, image_h, iou_threshold=0.45, top_k=4):
    """按风险等级+置信进行非极大值抑制，保留关键风险框。"""
    if not blocks:
        return []

    image_area = max(1, image_w * image_h)
    scored = []
    for b in blocks:
        bw = max(1, b["bbox"]["x2"] - b["bbox"]["x1"])
        bh = max(1, b["bbox"]["y2"] - b["bbox"]["y1"])
        area_ratio = (bw * bh) / image_area

        # 过滤过大的框，避免“整图都被框住”
        if area_ratio > 0.55:
            continue

        level = b.get("overall_risk_level", "unknown")
        low_dims = b.get("overall_low_dimensions", []) or []
        severity_bonus = min(len(low_dims), 5) * 0.1
        # 轻度偏好小框：同等级时优先更局部的区域
        size_bonus = max(0.0, 0.2 - area_ratio)
        score = _risk_rank(level) + severity_bonus + size_bonus
        scored.append((score, b))

    scored.sort(key=lambda x: x[0], reverse=True)
    kept = []
    for _, cand in scored:
        cbox = (
            cand["bbox"]["x1"],
            cand["bbox"]["y1"],
            cand["bbox"]["x2"],
            cand["bbox"]["y2"],
        )
        suppress = False
        for kept_item in kept:
            kbox = (
                kept_item["bbox"]["x1"],
                kept_item["bbox"]["y1"],
                kept_item["bbox"]["x2"],
                kept_item["bbox"]["y2"],
            )
            if _iou(cbox, kbox) >= iou_threshold:
                suppress = True
                break
        if not suppress:
            kept.append(cand)
        if len(kept) >= top_k:
            break

    # 若全部被面积过滤，可退化为保留一个最小面积风险框
    if not kept and blocks:
        fallback = sorted(
            blocks,
            key=lambda b: (b["bbox"]["x2"] - b["bbox"]["x1"]) * (b["bbox"]["y2"] - b["bbox"]["y1"]),
        )
        kept = fallback[:1]

    return kept


def localize_image_low_scores(image: Image.Image, format_name: str):
    """
    图片低分定位（MVP）：
    1) 将图像按网格切分
    2) 对每个区域做视觉描述
    3) 将描述送入文本评分器，得到低分维度与风险等级
    """
    width, height = image.size
    patch_results = []
    windows = _generate_candidate_windows(width, height)
    print(f"🔎 自适应候选区域数量: {len(windows)}")

    # 限制候选数量，避免调用过多
    max_windows = 18
    windows = windows[:max_windows]

    for idx, (x1, y1, x2, y2) in enumerate(windows):
            patch = image.crop((x1, y1, x2, y2))
            patch_b64 = _image_to_base64(patch, format_name)
            prompt = (
                "请仅描述这个图像局部区域的可见内容（人物、行为、标语、符号、物体）。"
                "输出简洁中文，不要推测看不到的信息。"
            )

            try:
                desc = _vision_describe_patch(patch_b64, format_name, prompt)
                loc = score_text_with_localization(desc)
                patch_results.append(
                    {
                        "id": f"w{idx}",
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                        "description": desc,
                        "overall_risk_level": loc.get("overall_risk_level", "unknown"),
                        "overall_low_dimensions": loc.get("overall_low_dimensions", []),
                        "scores": loc.get("scores", {}),
                    }
                )
            except Exception as e:
                print(f"⚠️ 候选区域视觉分析失败 [{idx}]，降级本地描述: {e}")
                err_text = str(e)
                is_policy_block = "content_policy_violation" in err_text
                fallback_desc = _describe_patch_basic(patch)
                fallback_loc = score_text_with_localization(fallback_desc)
                patch_results.append(
                    {
                        "id": f"w{idx}",
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                        "description": (
                            "该区域触发内容安全拦截，存在潜在高风险内容，建议人工复核。"
                            if is_policy_block
                            else fallback_desc
                        ),
                        "overall_risk_level": (
                            "high" if is_policy_block else fallback_loc.get("overall_risk_level", "unknown")
                        ),
                        "overall_low_dimensions": (
                            [{"dimension": "文明", "score": 0.0}]
                            if is_policy_block
                            else fallback_loc.get("overall_low_dimensions", [])
                        ),
                        "scores": fallback_loc.get("scores", {}),
                        "fallback_reason": str(e),
                        "policy_blocked": is_policy_block,
                    }
                )

    # 只保留具风险区域，再做 NMS 以得到“哪里有风险就框哪里”
    risk_blocks = [
        b for b in patch_results
        if b.get("overall_risk_level") in ("high", "medium")
    ]
    final_blocks = _nms_blocks(risk_blocks, width, height, iou_threshold=0.45, top_k=4)

    # 若未检出风险，返回空数组，让前端展示“未检出显著风险区域”
    print(f"✅ 定位输出风险框数量: {len(final_blocks)}")
    return final_blocks

def analyze_image_with_llm(image_file):
    """使用外部大模型分析图片内容"""
    try:
        # 读取图片
        image = Image.open(image_file)
        
        # 获取图片基本信息
        width, height = image.size
        format_name = image.format
        mode = image.mode
        
        # 将图片转换为 base64（用于发送给支持图片的模型）
        img_str = _image_to_base64(image, format_name)
        
        # 构造图片分析提示词
        analysis_prompt = f"""请详细分析这张图片的内容，包括：

1. **主要对象识别**：图片中有什么物体、人物、文字或符号？
2. **场景描述**：这是什么场景或环境？
3. **设计风格**：如果是设计作品，描述其风格特点
4. **颜色特征**：主要色彩搭配和视觉感受
5. **情感表达**：图片传达的情绪或信息
6. **价值观关联**：图片内容可能与哪些社会主义核心价值观相关？

请用中文回答，描述要详细具体，便于后续进行价值观评估。

图片信息：
- 格式：{format_name}
- 尺寸：{width}x{height}
- 颜色模式：{mode}

请基于以上要求，对图片进行全面分析。"""
        
        # 调用支持图片的大模型（使用 GPT-4o，它支持图片分析）
        try:
            # 构造多模态消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{format_name.lower()};base64,{img_str}"
                            }
                        }
                    ]
                }
            ]
            
            # 直接调用 OpenAI 兼容接口（需要支持图片的模型）
            from openai import OpenAI
            import os
            
            ZZZ_BASE_URL = os.getenv("ZZZ_BASE_URL", "https://api.zhizengzeng.com/v1")
            ZZZ_API_KEY = os.getenv("ZZZ_API_KEY", "sk-zk237a38360c4056d5097a3b10879eeb35a6914611803eeb")
            
            client = OpenAI(api_key=ZZZ_API_KEY, base_url=ZZZ_BASE_URL)
            resp = client.chat.completions.create(
                model="gpt-4o",  # 使用支持图片的模型
                messages=messages,
                max_tokens=1000
            )
            
            analysis_result = resp.choices[0].message.content.strip()

            # 低分定位（按网格切块）
            localization = localize_image_low_scores(image, format_name)
            
            return {
                'success': True,
                'analysis': analysis_result,
                'method': 'llm_analysis',
                'localization': localization,
                'details': {
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'model_used': 'gpt-4o'
                }
            }
            
        except Exception as llm_error:
            print(f"LLM 分析失败，降级到基础分析: {llm_error}")
            
            # 降级到基础分析
            return analyze_image_basic(image, width, height, format_name, mode)
            
    except Exception as e:
        return {
            'success': False,
            'error': f'图片分析失败：{str(e)}'
        }

def analyze_image_basic(image, width, height, format_name, mode):
    """基础图片分析（降级方案）"""
    features = []
    
    # 分析尺寸特征
    if width > height:
        orientation = "横向"
    elif height > width:
        orientation = "纵向"
    else:
        orientation = "正方形"
        
    features.append(f"{orientation}图片，尺寸为{width}x{height}像素")
    
    # 分析文件类型特征
    format_features = {
        'PNG': '支持透明通道的图片格式',
        'JPEG': '有损压缩的图片格式',
        'GIF': '支持动画的图片格式',
        'BMP': '未压缩的位图格式',
        'WEBP': '现代高效的图片格式'
    }
    
    format_desc = format_features.get(format_name, f'{format_name}格式图片')
    features.append(format_desc)
    
    # 组合分析结果
    analysis_result = f"这是一张{orientation}的{format_desc}。主要特征包括：{'，'.join(features)}。"
    
    return {
        'success': True,
        'analysis': analysis_result,
        'method': 'basic_analysis',
        'localization': [],
        'details': {
            'width': width,
            'height': height,
            'format': format_name,
            'mode': mode,
            'features': features
        }
    }

@image_analysis_bp.route("/analyze_image", methods=["POST"])
def analyze_image_api():
    """图片内容分析接口"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片文件'}), 400
        
        file = request.files['image']
        filename = request.form.get('filename', 'image')
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型，请上传图片文件'}), 400
        
        # 调用图片分析函数
        result = analyze_image_with_llm(file)
        
        if result['success']:
            return jsonify({
                'success': True,
                'analysis': result['analysis'],
                'localization': result.get('localization', []),
                'details': result.get('details', {})
            })
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

@image_analysis_bp.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'image_analysis',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })
