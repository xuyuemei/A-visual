from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO
from docx import Document


doc_parse_bp = Blueprint("doc_parse", __name__)


ALLOWED_DOC_EXT = {"doc", "docx"}


def _extract_paragraphs_from_docx(file_storage) -> list[str]:
    """从上传的 docx 上传文件中提取段落文本列表。"""
    # 读取全部字节并包装成 BytesIO，避免 SpooledTemporaryFile seekable 问题
    file_bytes = file_storage.read()
    document = Document(BytesIO(file_bytes))
    paragraphs = []
    for p in document.paragraphs:
        text = (p.text or "").strip()
        if text:
            paragraphs.append(text)
    return paragraphs


@doc_parse_bp.route("/parse_doc_text", methods=["POST"])
def parse_doc_text():
    """解析上传的 doc/docx 文件，按段落返回文本数组。

    返回格式：{"texts": ["段落1", "段落2", ...]}
    """
    if "file" not in request.files:
        return jsonify({"error": "缺少文件字段 file"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename or "")

    if not filename:
        return jsonify({"error": "文件名为空"}), 400

    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_DOC_EXT:
        return jsonify({"error": "仅支持 .doc 或 .docx 文件"}), 400

    try:
        # 目前先只处理 docx，doc 可以后续用其他库扩展
        if ext == "docx":
            texts = _extract_paragraphs_from_docx(file)
        else:
            return jsonify({"error": "当前仅实现 .docx 解析"}), 400

        if not texts:
            return jsonify({"error": "文档内容为空"}), 400

        return jsonify({"texts": texts}), 200
    except Exception as e:
        return jsonify({"error": f"文档解析失败: {str(e)}"}), 500
