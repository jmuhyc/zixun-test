"""
豆包 Seedream 图像生成脚本
使用 Volcengine Ark SDK 调用豆包模型 API
"""

import os
import requests
from config import ARK_API_KEY

# 统一输出文件夹
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_images")


def generate_seedream_image(
    prompt: str,
    model: str = "doubao-seedream-5-0-260128",
    size: str = "2K",
    output_format: str = "png",
    watermark: bool = False,
    save_to_file: bool = False,
    output_filename: str = None
) -> dict:
    """
    调用豆包 Seedream API 生成图像

    Args:
        prompt: 生成提示词
        model: 模型 ID
        size: 图片尺寸，可选 '2K' 等
        output_format: 输出格式，如 'png', 'jpg'
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
        output_filename = os.path.join(OUTPUT_DIR, f"seedream_output.png")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)
    try:
        from volcenginesdkarkruntime import Ark

        # 检查 API Key 是否配置
        if not ARK_API_KEY:
            error_msg = "未配置 ARK_API_KEY，请在 config.py 中填写"
            print(error_msg)
            return {"success": False, "error": error_msg}

        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=ARK_API_KEY,
            max_retries=2,
            timeout=60
        )

        images_response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            output_format=output_format,
            response_format="url",
            watermark=watermark
        )

        if images_response.data:
            img_url = images_response.data[0].url
            print(f"生成成功！图片链接：{img_url}")

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
    # 示例调用
    user_prompt = "充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子，色彩拼接丰富，眼部焦点锐利，景深较浅，具有 Vogue 杂志封面的美学风格，采用中画幅拍摄，工作室灯光效果强烈。"
    result = generate_seedream_image(
        prompt=user_prompt,
        save_to_file=True
    )
    print(result)
