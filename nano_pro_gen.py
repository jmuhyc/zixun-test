"""
Nano Pro 图像生成 API 调用脚本
使用 Gemini Nano 模型进行图像生成和编辑
"""

import requests
import json
from config import NANO_PRO_API_URL, NANO_PRO_API_KEY


def generate_nano_image(
    prompt: str,
    image_url: str = None,
    width: int = 1024,
    height: int = 1024,
    model: str = "gemini-3-pro-image-preview",
    backend_type: str = "yunyi"
) -> dict:
    """
    调用 Nano Pro API 生成图像

    Args:
        prompt: 生成提示词
        image_url: 可选的输入图片 URL（用于图生图）
        width: 生成图片宽度
        height: 生成图片高度
        model: 模型名称
        backend_type: 后端类型

    Returns:
        包含生成结果的字典
    """
    payload = {
        "version": "1.0.0",
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "backend_type": backend_type
    }

    if image_url:
        payload["image_url"] = [image_url]

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        response = requests.post(NANO_PRO_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        print(f"请求成功！Request ID: {result.get('request_id', 'N/A')}")

        if result.get("results"):
            for img in result["results"]:
                print(f"图片 URL: {img.get('image_url')}")
                print(f"尺寸：{img.get('image_width')}x{img.get('image_height')}")
                print(f"格式：{img.get('image_format')}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # 示例调用
    result = generate_nano_image(
        prompt="Change the style to watercolor painting",
        image_url="https://picsum.photos/seed/test/512/512.jpg",
        width=1024,
        height=1024
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
