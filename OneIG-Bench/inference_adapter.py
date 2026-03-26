"""
OneIG-Bench 适配器
将 zixun-test 项目的图像适配到 OneIG-Bench 格式

前置条件:
- 已运行图像生成脚本，output_images/ 中有生成的图像
- 已安装 OneIG-Bench 依赖

使用方式:
    python OneIG-Bench/inference_adapter.py
"""

import os
import shutil

import pandas as pd
from PIL import Image

# 路径配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_IMAGES_DIR = os.path.join(PROJECT_ROOT, "output_images")
ONEIG_IMAGES_DIR = os.path.join(PROJECT_ROOT, "OneIG-Bench", "images")
ONEIG_BENCH_CSV = os.path.join(PROJECT_ROOT, "OneIG-Bench", "OneIG-Bench-ZH.csv")

# OneIG-Bench 类别映射
# 当前项目类别 -> OneIG-Bench 类别
CATEGORY_MAPPING = {
    "商品图": "object",  # 商品图属于 General Object
    "模特图": "human",  # 模特图属于 Portrait
    "场景图": "object",  # 场景图属于 General Object
}

# 模型名称映射
MODEL_MAPPING = {
    "wanx": "wanx",
    "seedream": "seedream",
    "hunyuan": "hunyuan",
}


def create_oneig_directory_structure():
    """创建 OneIG-Bench 所需的目录结构"""
    categories = ["anime", "human", "object", "text", "reasoning", "multilingualism"]
    models = list(MODEL_MAPPING.values())

    for category in categories:
        for model in models:
            dir_path = os.path.join(ONEIG_IMAGES_DIR, category, model)
            os.makedirs(dir_path, exist_ok=True)

    print("[OK] OneIG-Bench 目录结构已创建")


def load_oneig_bench_prompts():
    """加载 OneIG-Bench 提示词"""
    if os.path.exists(ONEIG_BENCH_CSV):
        df = pd.read_csv(ONEIG_BENCH_CSV, dtype=str)
        return df
    return None


def get_image_category(filename):
    """从文件名推断 OneIG-Bench 类别"""
    for chinese_name, oneig_category in CATEGORY_MAPPING.items():
        if chinese_name in filename:
            return oneig_category
    return "object"  # 默认类别


def get_model_name(filename):
    """从文件名推断模型名称"""
    for model_prefix, model_name in MODEL_MAPPING.items():
        if model_prefix in filename.lower():
            return model_name
    return None


def adapt_existing_images():
    """将现有图像适配到 OneIG-Bench 格式"""
    if not os.path.exists(OUTPUT_IMAGES_DIR):
        print("[FAIL] output_images/ 目录不存在")
        return

    if not os.path.exists(ONEIG_BENCH_CSV):
        print("[FAIL] OneIG-Bench-ZH.csv 不存在，跳过提示词匹配")
        use_prompt_matching = False
    else:
        use_prompt_matching = True
        prompts_df = load_oneig_bench_prompts()

    # 获取所有图像文件
    image_extensions = [".png", ".jpg", ".jpeg", ".webp"]
    image_files = []
    for f in os.listdir(OUTPUT_IMAGES_DIR):
        if any(f.lower().endswith(ext) for ext in image_extensions):
            image_files.append(f)

    print(f"\n>> 找到 {len(image_files)} 个图像文件")

    adapted_count = 0
    for filename in image_files:
        model_name = get_model_name(filename)
        if model_name is None:
            print(f"  [WARN] 无法识别模型: {filename}")
            continue

        category = get_image_category(filename)

        # 构建目标路径
        # 使用文件名的 id（这里简化处理，实际使用时可能需要更精确的匹配）
        source_path = os.path.join(OUTPUT_IMAGES_DIR, filename)

        # 简化：使用文件名作为 id
        # 实际 OneIG-Bench 使用 CSV 中的 id
        if use_prompt_matching:
            # 尝试匹配提示词
            # 这里需要读取 config.py 中的 IMAGE_GENERATION_PROMPTS
            # 由于 config.py 包含密钥，我们使用文件名推断
            pass

        # 对于适配，我们直接将图像复制到对应目录
        # 使用序号命名（如 001.png）
        existing_in_dir = os.listdir(
            os.path.join(ONEIG_IMAGES_DIR, category, model_name)
        )
        next_id = len(existing_in_dir) + 1
        new_filename = f"{next_id:03d}.png"
        target_path = os.path.join(ONEIG_IMAGES_DIR, category, model_name, new_filename)

        try:
            shutil.copy2(source_path, target_path)
            print(f"  [OK] {filename} -> {category}/{model_name}/{new_filename}")
            adapted_count += 1
        except Exception as e:
            print(f"  [FAIL] 复制失败 {filename}: {e}")

    print(f"\n[OK] 成功适配 {adapted_count} 个图像到 OneIG-Bench 格式")


def main():
    """主函数"""
    print("=" * 60)
    print("OneIG-Bench 适配器")
    print("=" * 60)

    # 1. 创建目录结构
    print("\n>> 创建 OneIG-Bench 目录结构...")
    create_oneig_directory_structure()

    # 2. 适配现有图像
    print("\n>> 适配现有图像...")
    adapt_existing_images()

    print("\n" + "=" * 60)
    print("适配完成！")
    print(f"图像目录: {ONEIG_IMAGES_DIR}")
    print("\n下一步: 运行 OneIG-Bench 评测")
    print("=" * 60)


if __name__ == "__main__":
    main()
