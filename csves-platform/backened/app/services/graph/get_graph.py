import io
import base64
import matplotlib.pyplot as plt
from math import pi
import pandas as pd
import inspect
import textwrap
import json
import matplotlib.colors as mcolors
from app.utils.format import celldata_to_df
from app.static.ai_config import TXT2IMAGE, TXT2IMAGE_REVISE, MODEL_TYPE
from app.utils.gpt import ask_gpt


# ===============================
# 🔹 绘制亮蓝雷达图函数（接近图②风格）
# ===============================
def draw_radar(data: dict, model_name: str = "RadarModel", color: str = "#1E88E5"):
    """绘制亮蓝色雷达图并返回 base64"""
    import matplotlib.colors as mcolors

    if not data or len(data) == 0:
        raise ValueError("❌ draw_radar() 接收到空数据，请检查输入。")

    categories = list(data.keys())
    values = list(data.values())
    N = len(categories)

    try:
        values = [float(v) for v in values]
    except ValueError:
        raise ValueError("❌ 雷达图的值必须为数值类型，请检查数据内容。")

    # 闭合曲线
    values += values[:1]
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # ✅ 初始化图像
    plt.figure(figsize=(7, 7), dpi=150, facecolor="white")
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # ✅ 网格样式（浅蓝）
    ax.spines['polar'].set_visible(True)
    ax.spines['polar'].set_color('#DCE8FA')
    ax.grid(color='#DCE8FA', linestyle='solid', linewidth=1.2, alpha=0.8)

    # ✅ 坐标与标签
    plt.xticks(angles[:-1], categories, color='black', size=12, fontname='Arial')
    ax.set_rlabel_position(0)
    plt.yticks(color='#A6BFE3', size=9)
    plt.ylim(min(0, min(values) - 0.5), max(values) + 0.5)

    # ✅ 折线与填充（亮蓝色）
    line_color = "#1E88E5"  # 中亮蓝
    fill_color = mcolors.to_rgba(line_color, alpha=0.35)

    ax.plot(
        angles, values,
        linewidth=3,
        linestyle='solid',
        color=line_color,
        marker='o',
        markersize=7,
        markerfacecolor=line_color,
        markeredgecolor='white',
        markeredgewidth=1.5
    )
    ax.fill(angles, values, color=fill_color)

    # ✅ 标题
    plt.title(
        model_name,
        color=line_color,
        size=17,
        y=1.1,
        fontname='Arial',
        fontweight='bold'
    )

    # ✅ 导出 base64 图片
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor="white")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64


# ===============================
# 🔹 通用图表生成函数
# ===============================
def generate_graph(df, type, selected_model, requirements, color=None, template=None, history_code=None):
    """统一图表生成入口，支持 GPT 自动绘图与手动雷达图"""
    df = celldata_to_df(df)
    print("✅ DataFrame head:\n", df.head())

    # =======================================================
    # ⚡ 新增雷达图逻辑
    # =======================================================
    if type in ["雷达图", "radar"]:
        try:
            # 通常数据为两列：第一列类别，第二列数值
            if df.shape[1] >= 2:
                categories = df.iloc[:, 0].astype(str).tolist()
                try:
                    values = df.iloc[:, 1].astype(float).tolist()
                except Exception:
                    raise ValueError("⚠️ 第二列无法转为数值，请检查数据格式（如空格或文字）")

                data_single = dict(zip(categories, values))
                print("🎯 传入 draw_radar 的数据:", data_single)
            else:
                raise ValueError("雷达图数据格式不正确，至少需要两列（维度名 + 数值）")

            # ✅ 自动处理 color 参数：如果是数组字符串则取第一个颜色
            if isinstance(color, str) and color.startswith("["):
                try:
                    color_list = json.loads(color)
                    if isinstance(color_list, list) and len(color_list) > 0:
                        color = color_list[0]
                    else:
                        color = "#1E88E5"
                except Exception:
                    color = "#1E88E5"

            img_base64 = draw_radar(data_single, model_name="Radar Chart", color=color or "#1E88E5")
            code = "Radar chart generated manually."
            print(f"✅ 雷达图生成成功，颜色 = {color}")
            return img_base64, code

        except Exception as e:
            print("❌ 雷达图生成失败:", e)
            raise

    # =======================================================
    # ⚙️ GPT 自动图表逻辑
    # =======================================================
    data = df.to_dict(orient='list')

    if history_code:
        prompt = TXT2IMAGE_REVISE(data, history_code, requirements)
    else:
        prompt = TXT2IMAGE(data, type, requirements, color)
        if template:
            prompt = f"{prompt}\n请根据【模板】方向与样式给出代码\n{template}"

    print("🧠 Prompt 生成完毕，调用模型:", selected_model)
    ans = ask_gpt(prompt, MODEL_TYPE[selected_model])
    code_start = ans.find("<START>\n") + len("<START>\n")
    code_end = ans.find("<END>", code_start)
    code = ans[code_start:code_end].strip()
    code = textwrap.dedent(code).strip()
    print("🧩 提取到的代码：\n", code)

    # 执行代码并生成图片
    exec_globals = {"BytesIO": io.BytesIO, "base64": base64}
    buf = io.BytesIO()
    exec_locals = {"buf": buf, "df": df}

    wrapped_code = inspect.cleandoc(f"""
import matplotlib
import io
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import pandas as pd
{code}
plt.savefig(buf, format='png', bbox_inches='tight')
buf.seek(0)
plt.close()
    """)

    try:
        exec(wrapped_code, exec_globals, exec_locals)
        print("✅ GPT 图表生成成功！")
    except Exception as e:
        print("❌ GPT 图表执行失败:", e)
        raise

    img_base64 = base64.b64encode(exec_locals["buf"].getvalue()).decode('utf-8')
    return img_base64, code
