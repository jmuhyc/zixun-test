# 图像生成 API 工具集

包含四个主流图像生成 API 的 Python 调用脚本，支持自动化评分评估。

## 目录结构

```
zixun-test/
├── config.py                    # API Key 配置文件
├── config.example.py            # 配置示例
├── requirements.txt             # 依赖列表
├── score.md                     # 评分细则 (120分制)
│
├── Text-to-Image/               # 文生图生成脚本
│   ├── nano_pro_gen.py          # Nano Pro (Gemini) 图像生成
│   ├── wanx_gen.py              # 通义万相图像生成
│   ├── seedream_gen.py          # 豆包 Seedream 图像生成
│   └── hunyuan_gen.py           # 腾讯混元图像生成
│
├── Image-to-Image/              # 图生图生成脚本
│   ├── wanx_img2img.py          # 通义万相图生图
│   ├── seedream_img2img.py      # 豆包 Seedream 图生图
│   └── hunyuan_img2img.py       # 腾讯混元图生图
│
├── HPSv2_evaluation/            # HPSv2 自动化评分模块
│   ├── hpsv2_scorer.py          # CLIP-based HPSv2 评分器
│   ├── evaluate_hpsv2.py        # 评估脚本
│   └── run_evaluation.py        # 评估入口
│
├── Evaluation-Agent/             # Evaluation Agent 评分模块
│   └── eval_agent/
│       ├── eval_agent_scorer.py # VLM 评分器 (支持通义千问VL/GPT-4V)
│       └── evaluate_agent.py     # 评估脚本
│
├── output_images/               # 生成的图片输出目录
├── input_images/                # 输入参考图片目录
├── report/                      # 评估报告目录
│   └── report.md                # 模型对比报告
└── README.md                    # 本文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

额外依赖（HPSv2 和 Evaluation Agent 评分需要）：

```bash
pip install torch torchvision Pillow transformers CLIP
pip install levenshtein pandas
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

# OpenAI API Key (用于 Evaluation Agent，可选)
OPENAI_API_KEY = "your_openai_key"
```

## 各平台 API Key 获取地址

| 平台 | 获取地址 |
|------|----------|
| 通义万相 | https://dashscope.console.aliyun.com/apiKey |
| 豆包 Ark | https://console.volcengine.com/ark/region:ark+cn-beijing/apikey |
| 腾讯混元 | https://console.cloud.tencent.com/cam/capi |

## 图像生成

### 文生图

```bash
# Nano Pro
python Text-to-Image/nano_pro_gen.py

# 通义万相
python Text-to-Image/wanx_gen.py

# 豆包 Seedream
python Text-to-Image/seedream_gen.py

# 腾讯混元
python Text-to-Image/hunyuan_gen.py
```

### 图生图

```bash
# 通义万相
python Image-to-Image/wanx_img2img.py

# 豆包 Seedream
python Image-to-Image/seedream_img2img.py

# 腾讯混元
python Image-to-Image/hunyuan_img2img.py
```

## 自动化评分

### 评分体系

项目使用两种自动化评分方法：

| 方法 | 基础模型 | 特点 | 成本 |
|------|---------|------|------|
| **HPSv2** | CLIP | 快速、免费、离线运行 | 免费 |
| **Evaluation Agent** | VLM (通义千问VL/GPT-4V) | 智能分析、带文字解释 | API 费用 |

### 使用 HPSv2 评分

```bash
python HPSv2_evaluation/run_evaluation.py
```

### 使用 Evaluation Agent 评分

```bash
# 使用阿里云通义千问VL (默认)
python Evaluation-Agent/eval_agent/evaluate_agent.py --provider dashscope

# 使用 OpenAI GPT-4V
python Evaluation-Agent/eval_agent/evaluate_agent.py --provider openai
```

### 评分细则 (score.md)

评分基于 120 分制，包含 5 个维度：

| 维度 | 满分 | 说明 |
|------|:----:|------|
| 提示词识别度 | 25 | 文字描述理解、元素完整性、关键词突出、多元素稳定性 |
| 功能效果 | 25 | 结构合理性、细节真实、光影逻辑、色彩还原 |
| 一致性 | 20 | 产品/人物/场景一致性 |
| 画面视觉效果 | 15 | 构图版式、色彩光影、整洁度 |
| 图片输出规范 | 5 | 图像清晰度 |

## 评估报告

评估完成后，结果自动追加到 `report/report.md`，包含：

- **Section 1-4**: 测试环境、提示词、参数、人工评分
- **Section 5-7**: 优势劣势、场景建议、问题解决
- **Section 8**: HPSv2 自动化评分
- **Section 9**: Evaluation Agent 评分

## 在代码中调用

### 图像生成

```python
from config import IMAGE_GENERATION_PROMPTS

# 通义万相
from Text-to-Image.wanx_gen import generate_wanx_image
result = generate_wanx_image(prompt=IMAGE_GENERATION_PROMPTS["商品图"], save_to_file=True)

# 豆包 Seedream
from Text-to-Image.seedream_gen import generate_seedream_image
result = generate_seedream_image(prompt=IMAGE_GENERATION_PROMPTS["模特图"], save_to_file=True)

# 腾讯混元
from Text-to-Image.hunyuan_gen import submit_text_to_image_job
result = submit_text_to_image_job(prompt=IMAGE_GENERATION_PROMPTS["场景图"])
```

### HPSv2 评分

```python
from HPSv2_evaluation.hpsv2_scorer import HPSv2Scorer

scorer = HPSv2Scorer()
score = scorer.score_image_text("output_images/wanx_商品图.png", "A majestic black luxury sedan...")
print(f"HPSv2 Score: {score:.4f}")
```

### Evaluation Agent 评分

```python
from Evaluation-Agent.eval_agent.eval_agent_scorer import EvaluationAgentScorer

# 使用通义千问VL
scorer = EvaluationAgentScorer(provider="dashscope")

# 使用 GPT-4V
scorer = EvaluationAgentScorer(provider="openai")

results = scorer.evaluate_full("output_images/wanx_商品图.png", "A majestic black luxury sedan...")
```
