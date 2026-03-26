"""
豆包 Seedream 图生图脚本
使用 Volcengine Ark SDK 调用豆包 Seedream 5.0 图生图 API
"""

import os
import base64
import requests
import sys
from PIL import Image
import io

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from config import ARK_API_KEY

# 统一输出文件夹
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_images")

# 输入图片文件夹
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../input_images")

# Seedream API 限制：最大像素 36000000 (约 6000x6000)
MAX_PIXELS = 36000000


def encode_image_to_base64(image_path: str) -> str:
    """将图片转换为 base64 编码，如果图片太大则自动缩放"""
    # 检查图片尺寸
    with Image.open(image_path) as img:
        width, height = img.size
        total_pixels = width * height

        print(f"原图尺寸：{width}x{height} = {total_pixels:,} 像素")

        if total_pixels > MAX_PIXELS:
            # 计算缩放比例
            scale = (MAX_PIXELS / total_pixels) ** 0.5
            new_width = int(width * scale * 0.95)  # 留 5% 余量
            new_height = int(height * scale * 0.95)

            print(f"图片超过 API 限制 ({MAX_PIXELS:,} 像素)，自动缩放到：{new_width}x{new_height}")

            # 缩放图片
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 保存到内存并转换为 base64
            buffer = io.BytesIO()
            img_resized.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode("utf-8")
        else:
            print("图片尺寸符合 API 要求，直接处理")
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")


def generate_seedream_img2img(
    image_path: str,
    prompt: str,
    model: str = "doubao-seedream-5-0-260128",
    size: str = "2K",
    output_format: str = "png",
    strength: float = 0.7,
    watermark: bool = False,
    save_to_file: bool = False,
    output_filename: str = None
) -> dict:
    """
    调用豆包 Seedream API 生成图像（图生图）

    Args:
        image_path: 参考图本地路径
        prompt: 生成提示词
        model: 模型 ID
        size: 图片尺寸，可选 '2K' 等
        output_format: 输出格式，如 'png', 'jpg'
        strength: 重绘强度 (0-1)，值越大越接近提示词
        watermark: 是否添加水印
        save_to_file: 是否保存图片到本地
        output_filename: 输出文件名（默认保存到 output_images 文件夹）

    Returns:
        包含生成结果的字典
    """
    # 创建输出文件夹（如果不存在）
    if save_to_file and not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 默认文件名
    if output_filename is None:
        output_filename = os.path.join(OUTPUT_DIR, f"seedream_img2img_output.png")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)

    try:
        from volcenginesdkarkruntime import Ark

        # 检查 API Key 是否配置
        if not ARK_API_KEY:
            error_msg = "未配置 ARK_API_KEY，请在 config.py 中填写"
            print(error_msg)
            return {"success": False, "error": error_msg}

        # 检查图片是否存在
        if not os.path.exists(image_path):
            error_msg = f"图片文件不存在：{image_path}"
            print(error_msg)
            return {"success": False, "error": error_msg}

        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=ARK_API_KEY,
            max_retries=2,
            timeout=120
        )

        # 将图片转换为 base64
        image_base64 = encode_image_to_base64(image_path)

        # 调用图生图 API - 使用 generate 方法并传入 image 参数
        images_response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            output_format=output_format,
            response_format="url",
            watermark=watermark,
            image=f"data:image/jpeg;base64,{image_base64}"
        )

        if images_response.data:
            img_url = images_response.data[0].url
            print(f"图生图成功！图片链接：{img_url}")

            if save_to_file:
                img_data = requests.get(img_url).content
                with open(output_filename, "wb") as f:
                    f.write(img_data)
                print(f"图片已保存到：{output_filename}")

            return {"success": True, "image_url": img_url}
        else:
            error_msg = "生成失败：未返回图片数据"
            print(error_msg)
            return {"success": False, "error": error_msg}

    except ImportError:
        error_msg = "缺少依赖：请安装 volcengine-python-sdk，运行 pip install 'volcengine-python-sdk[ark]'"
        print(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"发生异常：{e}"
        print(error_msg)
        print(f"提示：请检查 API Key 是否正确，以及网络连接是否畅通")
        return {"success": False, "error": error_msg}


if __name__ == "__main__":
    # 批量处理 input_images 目录下的三张图片
    # 使用 config.py 中统一的提示词
    from config import IMAGE_GENERATION_PROMPTS

    # 图片类型与文件名的映射
    image_files = {
        "商品图": "商品图.jpg",
        "模特图": "模特图.jpg",
        "场景图": "场景图.jpg"
    }

    results = {}
    for image_type, image_file in image_files.items():
        print(f"\n{'='*50}")
        print(f"开始处理【{image_type}】...")
        print(f"{'='*50}\n")

        image_path = os.path.join(INPUT_DIR, image_file)

        # 使用对应类型的提示词
        prompt = IMAGE_GENERATION_PROMPTS.get(image_type, IMAGE_GENERATION_PROMPTS["商品图"])

        result = generate_seedream_img2img(
            image_path=image_path,
            prompt=prompt,
            save_to_file=True,
            output_filename=f"seedream_img2img_{image_type}.png",
            strength=0.7
        )
        results[image_type] = result

    print(f"\n{'='*50}")
    print("批量处理完成！")
    print(f"{'='*50}")
    for img_type, res in results.items():
        status = "成功" if res.get("success") else "失败"
        print(f"【{img_type}】: {status}")
