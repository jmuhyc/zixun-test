# 图像生成 API 工具集

包含四个主流图像生成 API 的 Python 调用脚本，API Key 统一管理。

## 目录结构

```
image_generation_api/
├── config.py           # API Key 配置文件
├── nano_pro_gen.py     # Nano Pro (Gemini) 图像生成
├── wanx_gen.py         # 通义万相图像生成
├── seedream_gen.py     # 豆包 Seedream 图像生成
├── hunyuan_gen.py      # 腾讯混元图像生成
└── requirements.txt    # 依赖列表
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置 API Key

编辑 `config.py` 文件，填入各平台的 API Key：

```python
# 通义万相 (DashScope) API Key
DASHSCOPE_API_KEY = "your_dashscope_key"

# 豆包 Seedream (Volcengine Ark) API Key
ARK_API_KEY = "your_ark_key"

# 腾讯混元 API Key
TENCENT_SECRET_ID = "your_secret_id"
TENCENT_SECRET_KEY = "your_secret_key"
```

## 各平台 API Key 获取地址

| 平台 | 获取地址 |
|------|----------|
| 通义万相 | https://dashscope.console.aliyun.com/apiKey |
| 豆包 Ark | https://console.volcengine.com/ark/region:ark+cn-beijing/apikey |
| 腾讯混元 | https://console.cloud.tencent.com/cam/capi |

## 使用方法

### 1. Nano Pro 图像生成

```bash
python nano_pro_gen.py
```

### 2. 通义万相图像生成

```bash
python wanx_gen.py
```

### 3. 豆包 Seedream 图像生成

```bash
python seedream_gen.py
```

### 4. 腾讯混元图像生成

```bash
python hunyuan_gen.py
```

## 在代码中调用

```python
# Nano Pro
from nano_pro_gen import generate_nano_image
result = generate_nano_image(prompt="Your prompt here")

# 通义万相
from wanx_gen import generate_wanx_image
result = generate_wanx_image(prompt="Your prompt here")

# 豆包 Seedream
from seedream_gen import generate_seedream_image
result = generate_seedream_image(prompt="Your prompt here")

# 腾讯混元
from hunyuan_gen import submit_text_to_image_job, describe_text_to_image_job
result = submit_text_to_image_job(prompt="Your prompt here")
```
