"""
通义万相 图生图脚本
使用 DashScope SDK 调用通义万相 wanx-v2 图生图 API
"""

import os
import base64
import requests
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from config import DASHSCOPE_API_KEY

# 统一输出文件夹
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_images")

# 输入图片文件夹
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../input_images")


def encode_image_to_base64(image_path: str) -> str:
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 设置 DashScope API Key - 必须在导入 dashscope 之前设置
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

import dashscope
from dashscope import ImageSynthesis


def generate_wanx_img2img(
    image_path: str,
    prompt: str,
    model: str = ImageSynthesis.Models.wanx_2_1_imageedit,
    size: str = "1024*1024",
    n: int = 1,
    save_to_file: bool = False,
    output_filename: str = None
) -> dict:
    """
    调用通义万相 API 生成图像（图生图）

    Args:
        image_path: 参考图本地路径
        prompt: 生成提示词
        model: 模型名称，如 'wanx-v2'
        size: 分辨率，可选 '1024*1024', '720*1280', '1280*720'
        n: 生成图片数量
        strength: 重绘强度 (0-1)，值越大越接近提示词
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
        output_filename = os.path.join(OUTPUT_DIR, f"wanx_img2img_output.png")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)

    try:
        # 检查图片是否存在
        if not os.path.exists(image_path):
            error_msg = f"图片文件不存在：{image_path}"
            print(error_msg)
            return {"success": False, "error": error_msg}

        # 将图片转换为 base64
        image_base64 = encode_image_to_base64(image_path)

        # 调用通义万相图生图 API - 使用 wanx-v1 模型
        # 注意：wanx2.1-imageedit 需要 function 和 base_image_url 参数，使用 wanx-v1 替代
        response = ImageSynthesis.call(
            model=ImageSynthesis.Models.wanx_v1,
            prompt=prompt,
            ref_img=f"data:image/jpeg;base64,{image_base64}",
            n=n,
            size=size
        )

        if response.status_code == 200:
            results = response.output.results
            image_urls = []

            for item in results:
                img_url = item.url
                image_urls.append(img_url)
                print(f"生成成功！图片链接：{img_url}")

                if save_to_file:
                    img_data = requests.get(img_url).content
                    with open(output_filename, "wb") as f:
                        f.write(img_data)
                    print(f"图片已保存到：{output_filename}")

            return {"success": True, "image_urls": image_urls}
        else:
            error_msg = f"生成失败：code={response.code}, message={response.message}"
            print(error_msg)
            return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = f"发生异常：{e}"
        print(error_msg)
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

        result = generate_wanx_img2img(
            image_path=image_path,
            prompt=prompt,
            size="1280*720",
            save_to_file=True,
            output_filename=f"wanx_img2img_{image_type}.png"
        )
        results[image_type] = result

    print(f"\n{'='*50}")
    print("批量处理完成！")
    print(f"{'='*50}")
    for img_type, res in results.items():
        status = "成功" if res.get("success") else "失败"
        print(f"【{img_type}】: {status}")
