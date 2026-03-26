# API 文档

## 图像生成 API 概览

| API | 供应商 | SDK | 主要用途 |
|-----|--------|-----|---------|
| Nano Pro | Google Gemini | HTTP API | 文本到图像 |
| WanX | 阿里 DashScope | `dashscope` | 文本/图像到图像 |
| Seedream | 字节 Volcengine | `volcengine-python-sdk` | 文本/图像到图像 |
| Hunyuan | 腾讯 | `tencentcloud-sdk` | 文本/图像到图像 |

---

## 1. Nano Pro (Gemini)

**调用方式**: HTTP REST API
**配置文件**: `config.py::NANO_PRO_CONFIG`

### 端点
```
POST https://api.example.com/nano-pro/generate
```

### 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | string | 文本提示词 |
| `model` | string | 模型版本 |
| `width` | int | 输出宽度 |
| `height` | int | 输出高度 |

---

## 2. WanX (阿里 DashScope)

**SDK**: `dashscope`
**配置文件**: `config.py::DASHSCOPE_API_KEY`

### 使用示例
```python
from dashscope import ImageSynthesis

response = ImageSynthesis.call(
    model="wanx-v1",
    prompt="商品展示图",
    size="1024*1024"
)
```

### 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型名称 (`wanx-v1`) |
| `prompt` | string | 文本提示词 |
| `size` | string | 输出尺寸 (`1024*1024`, `512*512`) |
| `n` | int | 生成数量 |

---

## 3. Seedream (字节火山引擎)

**SDK**: `volcengine-python-sdk[ark]`
**配置文件**: `config.py::VOLCENGINE_CONFIG`

### 使用示例
```python
from volcengine.visual.VisualService import VisualService

visual_service = VisualService()
response = visual_service.text_to_image({
    "prompt": "商品展示图",
    "model": "seedream-v3"
})
```

### 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | string | 文本提示词 |
| `model` | string | 模型版本 (`seedream-v3`) |
| `aspect_ratio` | string | 宽高比 (`1:1`, `16:9`) |

---

## 4. Hunyuan (腾讯云)

**SDK**: `tencentcloud-sdk`
**配置文件**: `config.py::TENCENT_CONFIG`

### 使用示例
```python
from tencentcloud.hunyuan.v20230901 import HunyuanClient
from tencentcloud.hunyuan.v20230901.models import TextToImageRequest

request = TextToImageRequest()
request.Prompt = "商品展示图"
```

### 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| `Prompt` | string | 文本提示词 |
| `Model` | string | 模型版本 (`hunyuan-v1`) |
| `Width` | int | 输出宽度 |
| `Height` | int | 输出高度 |

---

## 评测 API

### HPSv2 (CLIP-based)

**依赖**: `torch`, `transformers`, `CLIP`

```python
from HPSv2_evaluation.hpsv2_scorer import HPSv2Scorer

scorer = HPSv2Scorer()
score = scorer.score(image_path, prompt)
```

### Evaluation Agent (VLM-based)

**依赖**: `dashscope` (Qwen-VL) 或 OpenAI API (GPT-4V)

```python
from Evaluation-Agent.eval_agent.evaluate_agent import EvaluationAgent

agent = EvaluationAgent(model="gpt-4v")
result = agent.evaluate(image_path, prompt)
```

---

## 配置说明

所有 API 密钥配置在 `config.py`:

```python
# API 配置
DASHSCOPE_API_KEY = "sk-xxx"           # 阿里 DashScope
VOLCENGINE_CONFIG = {                   # 字节火山引擎
    "api_key": "xxx",
    "region": "cn-beijing"
}
TENCENT_CONFIG = {                      # 腾讯云
    "secret_id": "xxx",
    "secret_key": "xxx",
    "region": "ap-guangzhou"
}

# 图像生成提示词
IMAGE_GENERATION_PROMPTS = {
    "商品图": "高质量的商品展示图，白底，简洁背景",
    "模特图": "时尚模特穿戴展示图，专业摄影",
    "场景图": "生活场景应用图，自然光线"
}
```

---

*最后更新: 2026-03-26*
