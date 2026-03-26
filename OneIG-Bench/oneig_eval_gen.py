"""
OneIG-Bench 评测图像生成器
使用 OneIG-Bench 提示词生成图像并保存为正确的 ID

演示：生成少量图像用于评测

使用方式:
    python OneIG-Bench/oneig_eval_gen.py
"""

import os
import sys
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import time

# 添加父目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 路径配置
# OneIG-Benchmark 在项目根目录
ONEIG_BENCH_DIR = "d:/code/zixun-test2/OneIG-Benchmark"
ONEIG_IMAGES_DIR = os.path.join(PROJECT_ROOT, "OneIG-Bench", "images")
CSV_PATH = os.path.join(ONEIG_BENCH_DIR, "OneIG-Bench-ZH.csv")

# 演示：每类生成数量
SAMPLES_PER_CATEGORY = 3

# 类别映射
CATEGORY_MAP = {
    "Anime_Stylization": "anime",
    "Portrait": "human",
    "General_Object": "object",
    "Text_Rendering": "text",
    "Knowledge_Reasoning": "reasoning",
    "Multilingualism": "multilingualism",
}

# 模型配置
MODELS = ["wanx"]  # 可添加 "seedream", "hunyuan"


def setup_api_key():
    """设置 API Key"""
    try:
        from config import DASHSCOPE_API_KEY

        os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY
        return True
    except Exception as e:
        print(f"[ERROR] Cannot load API key: {e}")
        return False


def create_directory_structure():
    """创建目录结构"""
    for category_dir in CATEGORY_MAP.values():
        for model in MODELS:
            dir_path = os.path.join(ONEIG_IMAGES_DIR, category_dir, model)
            os.makedirs(dir_path, exist_ok=True)
    print("[OK] 目录结构已创建")


def generate_wanx_image(prompt: str, retry: int = 3) -> Image.Image:
    """使用 WanX API 生成图像"""
    for attempt in range(retry):
        try:
            from dashscope import ImageSynthesis

            response = ImageSynthesis.call(
                model="wanx-v1",
                prompt=prompt,
                size="1024*1024",
                n=1,
            )

            if response.status_code == 200:
                image_url = response.output.results[0].url
                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data)).convert("RGB")
                return img
            else:
                print(f"    [WARN] Attempt {attempt + 1}: {response.message}")
        except Exception as e:
            print(f"    [ERROR] Attempt {attempt + 1}: {e}")

        if attempt < retry - 1:
            time.sleep(2)

    # 返回黑图作为失败占位
    return Image.new("RGB", (1024, 1024), color=(0, 0, 0))


def generate_for_category(
    df: pd.DataFrame, category: str, category_dir: str, model: str
):
    """为一类生成图像"""
    category_df = df[df["category"] == category].head(SAMPLES_PER_CATEGORY)
    generated = 0

    print(f"\n[{category}] -> {category_dir}/{model}/")

    for idx, row in category_df.iterrows():
        prompt_id = row["id"].zfill(3)  # 确保3位ID (e.g., "000")
        prompt = row["prompt_cn"]

        # 截断过长提示词（API可能有长度限制）
        display_prompt = prompt[:60] + "..." if len(prompt) > 60 else prompt
        print(f"  [{prompt_id}] {display_prompt}")

        # 生成图像
        img = generate_wanx_image(prompt)

        # 保存为正确的 ID
        save_path = os.path.join(
            ONEIG_IMAGES_DIR, category_dir, model, f"{prompt_id}.png"
        )
        img.save(save_path, "PNG")
        generated += 1

        # 避免 API 限流
        time.sleep(1)

    return generated


def main():
    """主函数"""
    print("=" * 60)
    print("OneIG-Bench 评测图像生成器")
    print("=" * 60)

    # 设置 API
    if not setup_api_key():
        print("[FAIL] API key not available")
        return

    # 创建目录
    create_directory_structure()

    # 加载提示词
    print("\n>> 加载提示词...")
    df = pd.read_csv(CSV_PATH, dtype=str)
    print(f"[OK] 共 {len(df)} 个提示词")

    # 统计
    total_prompts = SAMPLES_PER_CATEGORY * len(CATEGORY_MAP)
    print(f"[INFO] 将生成 {total_prompts} 个图像 ({SAMPLES_PER_CATEGORY}个/类 x {len(CATEGORY_MAP)}类)")
    print(f"[INFO] 模型: {', '.join(MODELS)}")

    # 生成图像
    total_generated = 0
    for model in MODELS:
        print(f"\n>> 生成模型: {model}")
        for category, category_dir in CATEGORY_MAP.items():
            count = generate_for_category(df, category, category_dir, model)
            total_generated += count

    print("\n" + "=" * 60)
    print(f"[DONE] 生成完成: {total_generated} 张图像")
    print(f"[INFO] 图像目录: {ONEIG_IMAGES_DIR}")
    print("\n>> 下一步: 运行 OneIG-Bench 评测")
    print("=" * 60)


if __name__ == "__main__":
    main()
