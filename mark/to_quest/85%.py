#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------
功能：
1. 绝对阈值过滤 (<0.01 → 0)
2. 均值计算只基于非零数据
3. 动态阈值过滤 (<mean*0.85 → 0)
4. 删除所有维度均为 0 的问题
5. 删除“非零维度 ≤ 1” 的条目
-------------------------------------------------------
"""

import pandas as pd

INPUT_FILE = "/data/hlt/A-visual/mark/ans500_results.xlsx"
OUTPUT_FILE = "/data/hlt/A-visual/mark/ans500_cleaned.xlsx"

DIMENSIONS = [
    "爱国", "敬业", "诚信", "友善", "法治", "公正",
    "自由", "平等", "文明", "和谐", "民主", "富强"
]

def main():
    print("📄 正在读取评分文件...")
    df = pd.read_excel(INPUT_FILE)

    # ===================================================
    # Step 1: 绝对阈值过滤 <0.01 → 0
    # ===================================================
    print("🧹 Step 1：将 <0.01 的分数直接置为 0 ...")
    for dim in DIMENSIONS:
        df.loc[df[dim] < 0.01, dim] = 0.0

    # ===================================================
    # Step 2: 基于非零均值计算动态阈值
    # ===================================================
    print("\n🧠 Step 2：计算各维度 mean（排除 0） 和 threshold=mean*0.85 ...")
    thresholds = {}

    for dim in DIMENSIONS:
        nonzero_vals = df[df[dim] > 0][dim]

        if len(nonzero_vals) == 0:
            mean_score = 0
            threshold = 0
        else:
            mean_score = nonzero_vals.mean()
            threshold = mean_score * 0.85

        thresholds[dim] = threshold
        print(f"  → {dim}: 非零均分={mean_score:.4f}, 阈值={threshold:.4f}")

    # ===================================================
    # Step 3: 动态阈值过滤 <threshold → 0
    # ===================================================
    print("\n✏️ Step 3：根据动态阈值进行过滤 ...")
    for dim in DIMENSIONS:
        df.loc[df[dim] < thresholds[dim], dim] = 0.0

    # ===================================================
    # Step 4: 删除所有维度均为 0 的问题
    # ===================================================
    print("\n🧽 Step 4：删除所有12维度总和为 0 的问题 ...")
    df["total"] = df[DIMENSIONS].sum(axis=1)
    before_zero = len(df)
    df = df[df["total"] > 0].drop(columns=["total"])
    after_zero = len(df)
    print(f"  → 共删除 {before_zero - after_zero} 条全部为0的记录")

    # ===================================================
    # Step 5：删除非零维度 ≤1 的条目
    # ===================================================
    print("\n🔍 Step 5：删除非零维度 ≤1 的记录 ...")
    df["nonzero_dims"] = df[DIMENSIONS].gt(0).sum(axis=1)

    before_single = len(df)
    df = df[df["nonzero_dims"] > 1]
    after_single = len(df)

    print(f"  → 共删除 {before_single - after_single} 条“非零维度 ≤1”的记录")
    df = df.drop(columns=["nonzero_dims"])

    # ===================================================
    # 保存结果
    # ===================================================
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n🎉 清洗完成！结果保存至：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
