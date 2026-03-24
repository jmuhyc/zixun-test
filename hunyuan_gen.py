"""
腾讯混元图像生成脚本
使用腾讯云 SDK 调用混元 API
"""

import os
import json
import time
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
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_images")


# ================= TC3 签名算法 =================
def sign(key: bytes, msg: str) -> bytes:
    """计算 HMAC-SHA256 签名"""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature(
    secret_id: str,
    secret_key: str,
    host: str,
    action: str,
    version: str,
    region: str,
    payload: dict,
    service: str = "aiart"  # 服务名称，混元生图为 aiart
) -> dict:
    """
    生成 TC3 签名请求头

    Args:
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
        host: API 域名
        action: 接口名称
        version: API 版本
        region: 地域
        payload: 请求体

    Returns:
        包含签名请求头的字典
    """
    timestamp = int(time.time())
    date = datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%d")

    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{ct}\nhost:{host}\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    hashed_request_payload = hashlib.sha256(json.dumps(payload).encode("utf-8")).hexdigest()
    canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"

    algorithm = "TC3-HMAC-SHA256"
    credential_scope = f"{date}/{service}/tc3_request"
    string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    # 计算签名
    secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = sign(secret_date, service)
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization = f"{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    return {
        "Authorization": authorization,
        "Content-Type": ct,
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Region": region,
        "X-TC-Version": version
    }


def submit_text_to_image_job(
    prompt: str,
    resolution: str = "1280:720",
    seed: int = None,
    logo_add: int = 1,
    revise: int = 1,
    images: list = None
) -> dict:
    """
    提交混元文生图任务

    Args:
        prompt: 生成提示词
        resolution: 分辨率，如 '1280:720', '1024:1024'
        seed: 随机种子
        logo_add: 是否添加 Logo (1: 是，0: 否)
        revise: 是否优化 (1: 是，0: 否)
        images: 可选参考图 URL 列表

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
        req = models.SubmitTextToImageJobRequest()
        params = {
            "Prompt": prompt,
            "Resolution": resolution,
            "Seed": seed,
            "LogoAdd": logo_add,
            "Revise": revise
        }
        if images:
            params["Images"] = images
        req.from_json_string(json.dumps(params))

        # 发送请求
        resp = client.SubmitTextToImageJob(req)
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
            print("\n注意：这是异步任务，你需要调用 QueryTextToImageJob 接口轮询获取最终图片 URL。")
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


def query_text_to_image_job(job_id: str, save_to_file: bool = False, output_filename: str = None) -> dict:
    """
    查询混元文生图任务状态

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
        output_filename = os.path.join(OUTPUT_DIR, f"hunyuan_output.png")
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
        req = models.QueryTextToImageJobRequest()
        params = {"JobId": job_id}
        req.from_json_string(json.dumps(params))

        # 发送请求
        resp = client.QueryTextToImageJob(req)
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


if __name__ == "__main__":
    # 示例调用
    user_prompt = "一只戴着墨镜的卡通猫坐在沙滩上喝椰子汁，背景是夕阳大海，高清细节"
    result = submit_text_to_image_job(
        prompt=user_prompt,
        resolution="1280:720"
    )

    # 如果有 JobId，可以查询任务状态
    if result.get("success") and result.get("job_id"):
        job_id = result["job_id"]
        print("\n--- 开始轮询任务状态（最多 60 秒）---")
        # 轮询直到任务完成
        for i in range(12):  # 最多轮询 12 次，每次 5 秒
            time.sleep(5)
            query_result = query_text_to_image_job(job_id, save_to_file=True)
            # 检查是否完成 - SDK 返回的字段是 JobStatusCode
            # 2 表示处理中，5 表示完成（待领取），9 表示成功，10 表示失败
            job_status_code = query_result.get("JobStatusCode", "")
            result_image = query_result.get("ResultImage", [])

            if job_status_code in ["5", "9"] or (result_image and len(result_image) > 0):  # 成功
                print("\n[OK] 任务完成！")
                break
            elif job_status_code == "10":  # 失败
                print("\n[ERROR] 任务失败！")
                break
            else:
                print(f"\n[INFO] 任务仍在处理中，继续等待... (当前状态码：{job_status_code})")
