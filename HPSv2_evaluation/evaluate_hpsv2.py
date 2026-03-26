"""
HPSv2 Evaluation Script
对所有生成的图片进行 Human Preference Score v2 评分
"""

import os
import sys
import re
from datetime import datetime
from typing import Dict, Optional

# 添加父目录到路径以便导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import IMAGE_GENERATION_PROMPTS
from HPSv2_evaluation.hpsv2_scorer import HPSv2Scorer

# 配置路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_IMAGES_DIR = os.path.join(PROJECT_ROOT, "output_images")
REPORT_PATH = os.path.join(PROJECT_ROOT, "report", "report.md")

# 模型配置 - 按 report.md 中的命名
MODELS = ["nano_pro", "hunyuan", "wanx", "seedream"]
PROMPT_TYPES = ["商品图", "模特图", "场景图"]

# 人工评分 (来自 report.md Section 4.6)
MANUAL_SCORES = {
    "nano_pro": 74,
    "hunyuan": 97,
    "wanx": 94,
    "seedream": 97
}


def get_image_path(model: str, prompt_type: str) -> str:
    """
    获取输出图片的完整路径。
    模型名称映射到实际文件名。
    """
    # 文件名格式: {model}_{prompt_type}.png
    filename = f"{model}_{prompt_type}.png"
    return os.path.join(OUTPUT_IMAGES_DIR, filename)


def load_report_content() -> str:
    """加载现有报告内容。"""
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def save_report_content(content: str):
    """保存报告内容。"""
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def run_hpsv2_evaluation() -> Dict[str, Dict[str, Optional[float]]]:
    """
    对所有生成的图片运行 HPSv2 评分。

    Returns:
        分数字典: {model: {prompt_type: score}}
    """
    print("Initializing HPSv2 Scorer...")
    scorer = HPSv2Scorer()

    results = {}

    print("\n" + "=" * 60)
    print("HPSv2 Image-Text Alignment Evaluation")
    print("=" * 60 + "\n")

    for model in MODELS:
        results[model] = {}
        print(f"\n--- Model: {model} ---")

        for prompt_type in PROMPT_TYPES:
            image_path = get_image_path(model, prompt_type)
            prompt = IMAGE_GENERATION_PROMPTS.get(prompt_type, "")

            if os.path.exists(image_path):
                score = scorer.score_image_text(image_path, prompt)
                results[model][prompt_type] = score
                print(f"  [{prompt_type}] {score:.4f}")
            else:
                results[model][prompt_type] = None
                print(f"  [{prompt_type}] N/A (image not found)")

    return results


def calculate_average(scores: Dict[str, Optional[float]]) -> Optional[float]:
    """计算有效分数的平均值。"""
    valid = [s for s in scores.values() if s is not None]
    if valid:
        return sum(valid) / len(valid)
    return None


def generate_hpsv2_section(hpsv2_scores: Dict[str, Dict[str, Optional[float]]]) -> str:
    """生成 HPSv2 评分报告章节。"""

    section = """
---

## 八、HPSv2 自动化评分 (Human Preference Score v2)

> HPSv2 是一种基于 CLIP 架构的自动化评分方法，用于评估图像与文本提示的一致性。分数范围 0-1，越高表示图像与提示词的匹配度越高。
>
> **评估时间**: {timestamp}

### 8.1 各模型 HPSv2 评分详情

| 模型 | 商品图 | 模特图 | 场景图 | 平均分 |
|------|:------:|:------:|:------:|:------:|
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    for model in MODELS:
        scores = hpsv2_scores.get(model, {})
        product = scores.get("商品图")
        model_p = scores.get("模特图")
        scene = scores.get("场景图")

        p_str = f"{product:.4f}" if product else "N/A"
        m_str = f"{model_p:.4f}" if model_p else "N/A"
        s_str = f"{scene:.4f}" if scene else "N/A"

        avg = calculate_average(scores)
        avg_str = f"{avg:.4f}" if avg else "N/A"

        section += f"| **{model}** | {p_str} | {m_str} | {s_str} | {avg_str} |\n"

    section += """
### 8.2 HPSv2 评分解读

| 分数范围 | 评价 |
|:--------:|:-----|
| > 0.70 | 优秀的图像-文本一致性 |
| 0.50 - 0.70 | 良好的匹配度 |
| 0.30 - 0.50 | 中等一致性 |
| < 0.30 | 较低的一致性 |

### 8.3 与人工评分对比

| 模型 | 人工评分 (120分制) | HPSv2 平均分 | 归一化人工分 | 评价一致性 |
|------|:-----------------:|:------------:|:------------:|:----------:|
"""

    for model in MODELS:
        scores = hpsv2_scores.get(model, {})
        avg = calculate_average(scores)
        hps_avg = avg if avg else 0

        manual = MANUAL_SCORES.get(model, 0)
        manual_normalized = manual / 120

        if hps_avg > 0:
            diff_pct = abs(hps_avg - manual_normalized) / manual_normalized * 100
            if diff_pct < 20:
                consistency = "高度一致"
            elif diff_pct < 40:
                consistency = "基本一致"
            else:
                consistency = "存在差异"
        else:
            consistency = "N/A"

        hps_str = f"{hps_avg:.4f}" if avg else "N/A"
        manual_norm_str = f"{manual_normalized:.4f}"

        section += f"| **{model}** | {manual} | {hps_str} | {manual_norm_str} | {consistency} |\n"

    return section


def update_report(hpsv2_scores: Dict[str, Dict[str, Optional[float]]]):
    """更新报告文件，追加 HPSv2 评分章节。"""

    section = generate_hpsv2_section(hpsv2_scores)

    content = load_report_content()

    # 检查是否已存在 HPSv2 章节
    if "## 八、HPSv2" in content:
        # 替换现有章节
        pattern = r'(---\n\n## 八、HPSv2.*?)(?=\n---|\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + section + content[match.end():]
    else:
        # 追加新章节
        content = content.rstrip() + "\n" + section

    save_report_content(content)
    print(f"\nReport updated: {REPORT_PATH}")


def print_summary(hpsv2_scores: Dict[str, Dict[str, Optional[float]]]):
    """打印评分汇总。"""
    print("\n" + "=" * 60)
    print("HPSv2 Evaluation Summary")
    print("=" * 60)

    for model in MODELS:
        scores = hpsv2_scores.get(model, {})
        avg = calculate_average(scores)
        avg_str = f"{avg:.4f}" if avg else "N/A"
        print(f"  {model}: {avg_str}")

    print("\n" + "-" * 40)
    print("Ranking (by HPSv2 average):")
    ranking = []
    for model in MODELS:
        avg = calculate_average(hpsv2_scores.get(model, {}))
        if avg:
            ranking.append((model, avg))
    ranking.sort(key=lambda x: x[1], reverse=True)

    for i, (model, score) in enumerate(ranking, 1):
        print(f"  {i}. {model}: {score:.4f}")


if __name__ == "__main__":
    print("HPSv2 Evaluation for Text-to-Image Models")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行评估
    hpsv2_scores = run_hpsv2_evaluation()

    # 打印汇总
    print_summary(hpsv2_scores)

    # 更新报告
    update_report(hpsv2_scores)

    print("\nDone!")
