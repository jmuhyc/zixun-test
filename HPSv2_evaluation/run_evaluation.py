"""
HPSv2 Evaluation Runner
HPSv2 评估入口脚本
"""

import os
import sys
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HPSv2_evaluation.evaluate_hpsv2 import (
    run_hpsv2_evaluation,
    update_report,
    print_summary,
    MODELS,
    PROMPT_TYPES,
    get_image_path,
    OUTPUT_IMAGES_DIR
)


def check_available_images():
    """检查可用的图片。"""
    print("Checking available images...")
    available = []
    missing = []

    for model in MODELS:
        for prompt_type in PROMPT_TYPES:
            path = get_image_path(model, prompt_type)
            if os.path.exists(path):
                available.append((model, prompt_type))
            else:
                missing.append((model, prompt_type))

    print(f"\nAvailable: {len(available)} images")
    for m, p in available:
        print(f"  - {m}_{p}")

    if missing:
        print(f"\nMissing: {len(missing)} images")
        for m, p in missing:
            print(f"  - {m}_{p}")

    return available


def main():
    """主函数。"""
    print("=" * 60)
    print("Text-to-Image Model HPSv2 Evaluation Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查图片
    available = check_available_images()

    if not available:
        print("\nNo images found for evaluation!")
        print("Please run image generation scripts first:")
        print("  python Text-to-Image/hunyuan_gen.py")
        print("  python Text-to-Image/wanx_gen.py")
        print("  python Text-to-Image/seedream_gen.py")
        return

    print(f"\nFound {len(available)} images for evaluation.")
    print("\n" + "-" * 60)

    # 运行 HPSv2 评估
    hpsv2_scores = run_hpsv2_evaluation()

    # 打印汇总
    print_summary(hpsv2_scores)

    # 更新报告
    update_report(hpsv2_scores)

    print("\nEvaluation complete!")
    print(f"Results saved to: report/report.md")


if __name__ == "__main__":
    main()
