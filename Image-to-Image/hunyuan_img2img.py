"""
腾讯混元图生图脚本
使用腾讯云 SDK 调用混元图生图 API
"""

import os
import json
import time
import hashlib
import hmac
from datetime import datetime, timezone
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.aiart.v20221229 import aiart_client, models
from config import (
    TENCENT_SECRET_ID,
    TENCENT_SECRET_KEY,
    TENCENT_REGION
)

# 统一输出文件夹
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_images")

# 输入图片文件夹
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../input_images")


def submit_image_to_image_job(
    image_url: str,
    prompt: str,
    resolution: str = "1280:720",
    strength: float = 0.7,
    seed: int = None,
    logo_add: int = 1,
    revise: int = 1
) -> dict:
    """
    提交混元图生图任务

    Args:
        image_url: 参考图 URL
        prompt: 生成提示词
        resolution: 分辨率，如 '1280:720', '1024:1024'
        strength: 重绘强度 (0-1)，值越大越接近提示词
        seed: 随机种子
        logo_add: 是否添加 Logo (1: 是，0: 否)
        revise: 是否优化 (1: 是，0: 否)

    Returns:
        包含任务提交结果的字典
    """
    try:
        # 创建认证对象
        cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)

        # 配置 HTTP 选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "aiart.tencentcloudapi.com"

        # 配置客户端选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 创建客户端
        client = aiart_client.AiartClient(cred, TENCENT_REGION, clientProfile)

        if seed is None:
            seed = int(time.time() * 1000) % (2**32)

        # 创建请求对象
        req = models.SubmitImageToImageJobRequest()
        params = {
            "Prompt": prompt,
            "ImageUrl": image_url,
            "Resolution": resolution,
            "Strength": strength,
            "Seed": seed,
            "LogoAdd": logo_add,
            "Revise": revise
        }
        req.from_json_string(json.dumps(params))

        # 发送请求
        resp = client.SubmitImageToImageJob(req)
        result = json.loads(resp.to_json_string())

        print("=== 响应结果 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # SDK 返回的格式：JobId 在根级别
        if "JobId" in result:
            job_id = result["JobId"]
            request_id = result.get("RequestId", "")
            print(f"\n[OK] 任务提交成功！")
            print(f"JobId: {job_id}")
            print(f"RequestId: {request_id}")
            print("\n注意：这是异步任务，你需要调用 QueryImageToImageJob 接口轮询获取最终图片 URL。")
            return {"success": True, "job_id": job_id, "request_id": request_id, "data": result}
        else:
            print("\n[ERROR] 响应格式异常或未包含 JobId")
            return {"success": False, "error": "响应格式异常", "data": result}

    except TencentCloudSDKException as err:
        error_msg = f"SDK 错误：{err}"
        print(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"发生异常：{e}"
        print(error_msg)
        return {"success": False, "error": error_msg}


def query_image_to_image_job(job_id: str, save_to_file: bool = False, output_filename: str = None) -> dict:
    """
    查询混元图生图任务状态

    Args:
        job_id: 任务 ID
        save_to_file: 是否保存图片到本地
        output_filename: 输出文件名（默认保存到 output_images 文件夹）

    Returns:
        包含任务查询结果的字典
    """
    # 创建输出文件夹（如果不存在）
    if save_to_file and not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 默认文件名
    if output_filename is None:
        output_filename = os.path.join(OUTPUT_DIR, f"hunyuan_img2img_output.png")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)

    try:
        # 创建认证对象
        cred = credential.Credential(TENCENT_SECRET_ID, TENCENT_SECRET_KEY)

        # 配置 HTTP 选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "aiart.tencentcloudapi.com"

        # 配置客户端选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 创建客户端
        client = aiart_client.AiartClient(cred, TENCENT_REGION, clientProfile)

        # 创建请求对象
        req = models.QueryImageToImageJobRequest()
        params = {"JobId": job_id}
        req.from_json_string(json.dumps(params))

        # 发送请求
        resp = client.QueryImageToImageJob(req)
        result = json.loads(resp.to_json_string())

        print("=== 任务查询结果 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # SDK 返回的格式：JobStatusCode 和 ResultImage 在根级别
        job_status_code = result.get("JobStatusCode", "")
        result_image_list = result.get("ResultImage", [])

        # 状态码说明：2-处理中，5-待领取（完成），9-成功，10-失败
        if job_status_code in ["5", "9"] or (result_image_list and len(result_image_list) > 0):
            print(f"任务状态：已完成 (状态码：{job_status_code})")

            if result_image_list and len(result_image_list) > 0:
                result_image_url = result_image_list[0]
                print(f"图片 URL: {result_image_url}")

                if save_to_file:
                    img_data = requests.get(result_image_url).content
                    with open(output_filename, "wb") as f:
                        f.write(img_data)
                    print(f"图片已保存到：{output_filename}")
        elif job_status_code == "2":
            print(f"任务状态：处理中")
        elif job_status_code == "10":
            print(f"任务状态：失败")
        else:
            print(f"任务状态：未知 (状态码：{job_status_code})")

        return result

    except TencentCloudSDKException as err:
        error_msg = f"SDK 错误：{err}"
        print(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"发生异常：{e}"
        print(error_msg)
        return {"error": error_msg}


def upload_image_to_cos(image_path: str) -> str:
    """
    将本地图片上传到临时 COS 存储获取 URL
    注意：这是简化实现，实际使用建议配置自己的 COS 存储桶

    Args:
        image_path: 本地图片路径

    Returns:
        图片 URL
    """
    # 简化实现：使用腾讯云的临时上传接口或替换为实际的图片 URL
    # 实际使用时，建议配置自己的 COS 存储桶来上传图片
    print(f"提示：请将图片 {image_path} 上传到您的 COS 存储桶，或使用图床服务获取 URL")
    return ""


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

    # 注意：混元图生图需要图片 URL，你需要先将图片上传到 COS 或图床
    # 这里假设你有一个图床服务可以获取图片 URL
    # 实际使用时，请替换为你的实际图片 URL

    # 示例：使用公开的图床或自己的 COS 存储桶
    # 为了演示，这里使用占位 URL，实际使用时请替换
    image_urls = {
        "商品图": "https://example.com/商品图.jpg",  # 请替换为实际 URL
        "模特图": "https://example.com/模特图.jpg",  # 请替换为实际 URL
        "场景图": "https://example.com/场景图.jpg"   # 请替换为实际 URL
    }

    results = {}
    for image_type, image_file in image_files.items():
        print(f"\n{'='*50}")
        print(f"开始处理【{image_type}】...")
        print(f"{'='*50}\n")

        # 使用对应类型的提示词
        prompt = IMAGE_GENERATION_PROMPTS.get(image_type, IMAGE_GENERATION_PROMPTS["商品图"])

        # 获取图片 URL（实际使用时请替换为真实的 URL）
        image_url = image_urls.get(image_type)

        if not image_url:
            print(f"[ERROR] 未找到【{image_type}】的图片 URL，请先上传到 COS 或图床")
            results[image_type] = {"success": False, "error": "图片 URL 未配置"}
            continue

        result = submit_image_to_image_job(
            image_url=image_url,
            prompt=prompt,
            resolution="1280:720",
            strength=0.7
        )

        # 如果有 JobId，查询任务状态
        if result.get("success") and result.get("job_id"):
            job_id = result["job_id"]
            print(f"\n--- 轮询任务状态（最多 60 秒）---")
            for i in range(12):
                time.sleep(5)
                query_result = query_image_to_image_job(
                    job_id,
                    save_to_file=True,
                    output_filename=f"hunyuan_img2img_{image_type}.png"
                )
                job_status_code = query_result.get("JobStatusCode", "")
                result_image = query_result.get("ResultImage", [])

                if job_status_code in ["5", "9"] or (result_image and len(result_image) > 0):
                    print(f"\n[OK] 【{image_type}】任务完成！")
                    results[image_type] = {"success": True, "job_id": job_id}
                    break
                elif job_status_code == "10":
                    print(f"\n[ERROR] 【{image_type}】任务失败！")
                    results[image_type] = {"success": False, "error": "任务失败"}
                    break
                else:
                    print(f"\n[INFO] 【{image_type}】仍在处理中... (当前状态码：{job_status_code})")
        else:
            results[image_type] = result

    print(f"\n{'='*50}")
    print("批量处理完成！")
    print(f"{'='*50}")
    for img_type, res in results.items():
        status = "成功" if res.get("success") else "失败"
        print(f"【{img_type}】: {status}")
