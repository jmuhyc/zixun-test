"""
通义万相图像生成脚本
使用 DashScope SDK 调用通义万相 API
"""

import os
import requests
from config import DASHSCOPE_API_KEY, IMAGE_GENERATION_PROMPTS

# 统一输出文件夹
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_images")

# 设置 DashScope API Key - 必须在导入 dashscope 之前设置
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

import dashscope
from dashscope import ImageSynthesis


def generate_wanx_image(
    prompt: str,
    model: str = "wanx-v1",
    size: str = "1024*1024",
    n: int = 1,
    save_to_file: bool = False,
    output_filename: str = None
) -> dict:
    """
    调用通义万相 API 生成图像

    Args:
        prompt: 生成提示词
        model: 模型名称，可选 'wanx-v1', 'wanx2.0-turbo' 等
        size: 分辨率，可选 '1024*1024', '720*1280', '1280*720'
        n: 生成图片数量
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
        output_filename = os.path.join(OUTPUT_DIR, f"wanx_output.png")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)
    try:
        response = ImageSynthesis.call(
            model=model,
            prompt=prompt,
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
    # 批量生成 config.py 中统一的三组提示词图片
    results = {}
    for image_type, user_prompt in IMAGE_GENERATION_PROMPTS.items():
        print(f"\n{'='*50}")
        print(f"开始生成【{image_type}】...")
        print(f"{'='*50}\n")

        result = generate_wanx_image(
            prompt=user_prompt,
            save_to_file=True,
            output_filename=f"wanx_{image_type}.png"
        )
        results[image_type] = result

    print(f"\n{'='*50}")
    print("批量生成完成！")
    print(f"{'='*50}")
    for img_type, res in results.items():
        status = "成功" if res.get("success") else "失败"
        print(f"【{img_type}】: {status}")
