"""
OneIG-Bench 图像生成脚本
使用 OneIG-Bench 提示词生成图像（演示版）

使用方式:
    python OneIG-Bench/oneig_gen.py
"""

import os
import sys
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# 添加父目录到路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 路径配置
ONEIG_BENCH_DIR = os.path.join(PROJECT_ROOT, "OneIG-Benchmark")
ONEIG_IMAGES_DIR = os.path.join(ONEIG_BENCH_DIR, "images")
CSV_PATH = os.path.join(ONEIG_BENCH_DIR, "OneIG-Bench-ZH.csv")

# 每类生成数量（演示用）
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


def create_directory_structure():
    """创建目录结构"""
    for category_dir in CATEGORY_MAP.values():
        for model in ["wanx", "seedream", "hunyuan"]:
            dir_path = os.path.join(ONEIG_IMAGES_DIR, category_dir, model)
            os.makedirs(dir_path, exist_ok=True)
    print("[OK] 目录结构已创建")


def load_prompts():
    """加载提示词"""
    df = pd.read_csv(CSV_PATH, dtype=str)
    return df


def generate_wanx_image(prompt: str) -> Image.Image:
    """使用 WanX API 生成图像"""
    try:
        # 设置 API Key
        from config import DASHSCOPE_API_KEY

        os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

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
            print(f"    [ERROR] API error: {response.code}")
            return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None


def generate_seedream_image(prompt: str) -> Image.Image:
    """使用 Seedream API 生成图像"""
    try:
        from config import ARK_API_KEY

        from volcengine.visual.VisualService import VisualService

        visual_service = VisualService()
        # 注意：这是简化版本，实际需要正确的API调用格式
        print(f"    [WARN] Seedream API not fully configured")
        return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None


def generate_hunyuan_image(prompt: str) -> Image.Image:
    """使用 Hunyuan API 生成图像"""
    try:
        from config import TENCENT_SECRET_ID, TENCENT_SECRET_KEY

        # 腾讯云 SDK 调用
        print(f"    [WARN] Hunyuan API not fully configured")
        return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None


def generate_image(prompt: str, model: str = "wanx") -> Image.Image:
    """根据模型生成图像"""
    if model == "wanx":
        return generate_wanx_image(prompt)
    elif model == "seedream":
        return generate_seedream_image(prompt)
    elif model == "hunyuan":
        return generate_hunyuan_image(prompt)
    else:
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("OneIG-Bench 图像生成（演示版）")
    print("=" * 60)
    print(f"\n每类生成数量: {SAMPLES_PER_CATEGORY}")

    # 创建目录结构
    create_directory_structure()

    # 加载提示词
    print("\n>> 加载提示词...")
    df = load_prompts()
    print(f"[OK] 加载了 {len(df)} 个提示词")

    # 选择一个模型进行演示
    model = "wanx"
    print(f"\n>> 使用模型: {model}")
    print(">> 按 Ctrl+C 中断...\n")

    # 按类别生成图像
    total_generated = 0
    for category, category_dir in CATEGORY_MAP.items():
        category_df = df[df["category"] == category].head(SAMPLES_PER_CATEGORY)
        print(f"\n[{category}] -> {category_dir}")

        for idx, row in category_df.iterrows():
            prompt_id = row["id"]
            prompt = row["prompt_cn"][:80] + "..." if len(row["prompt_cn"]) > 80 else row["prompt_cn"]

            print(f"  [{prompt_id}] {prompt}")

            # 生成图像
            img = generate_image(prompt, model)

            if img:
                # 保存图像
                save_path = os.path.join(
                    ONEIG_IMAGES_DIR, category_dir, model, f"{prompt_id}.png"
                )
                img.save(save_path, "PNG")
                print(f"    -> 已保存")
                total_generated += 1
            else:
                # 创建黑图占位
                save_path = os.path.join(
                    ONEIG_IMAGES_DIR, category_dir, model, f"{prompt_id}.png"
                )
                black_img = Image.new("RGB", (1024, 1024), color=(0, 0, 0))
                black_img.save(save_path, "PNG")
                print(f"    -> 已保存(黑图占位)")

    print("\n" + "=" * 60)
    print(f"[DONE] 生成完成，共 {total_generated} 张图像")
    print(f"图像目录: {ONEIG_IMAGES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
