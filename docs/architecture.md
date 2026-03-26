# 架构文档

## 项目架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      zixun-test                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Text-to-    │    │ Image-to-   │    │ Evaluation  │    │
│  │ Image       │───▶│ Image       │───▶│             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                  │                   │           │
│         ▼                  ▼                   ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              output_images/                          │   │
│  │   (wanx_*.png, seedream_*.png, hunyuan_*.png)       │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              report/report.md                        │   │
│  │   (评测报告：HPSv2 + Evaluation Agent 评分)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 模块关系

### 1. 图像生成模块 (Text-to-Image/)

| 文件 | API | 说明 |
|------|-----|------|
| `nano_pro_gen.py` | Gemini Nano Pro | 文本到图像生成 |
| `wanx_gen.py` | 阿里 WanX (DashScope) | 文本到图像生成 |
| `seedream_gen.py` | 字节 Seedream (Volcengine) | 文本到图像生成 |
| `hunyuan_gen.py` | 腾讯 Hunyuan | 文本到图像生成 |

### 2. 图像到图像模块 (Image-to-Image/)

| 文件 | API | 说明 |
|------|-----|------|
| `wanx_img2img.py` | 阿里 WanX | 图像到图像生成 |
| `seedream_img2img.py` | 字节 Seedream | 图像到图像生成 |
| `hunyuan_img2img.py` | 腾讯 Hunyuan | 图像到图像生成 |

### 3. 评测模块

#### HPSv2_evaluation/ (CLIP 自动评分)

| 文件 | 说明 |
|------|------|
| `hpsv2_scorer.py` | HPSv2 评分实现 |
| `evaluate_hpsv2.py` | 核心评测逻辑 |
| `run_evaluation.py` | 入口点 |

#### Evaluation-Agent/ (VLM 智能评分)

| 文件 | 说明 |
|------|------|
| `eval_agent/evaluate_agent.py` | VLM 评测入口 |
| `eval_agent/eval_agent_scorer.py` | 评分器 |

### 4. 配置模块

| 文件 | 说明 |
|------|------|
| `config.py` | API 密钥和提示词（敏感） |
| `config.example.py` | 配置模板 |

## 目录结构

```
zixun-test/
├── config.py                    # 运行时配置（API密钥）
├── config.example.py            # 配置模板
├── requirements.txt              # Python 依赖
│
├── Text-to-Image/                # 文本到图像生成
│   ├── nano_pro_gen.py
│   ├── wanx_gen.py
│   ├── seedream_gen.py
│   └── hunyuan_gen.py
│
├── Image-to-Image/               # 图像到图像生成
│   ├── wanx_img2img.py
│   ├── seedream_img2img.py
│   └── hunyuan_img2img.py
│
├── HPSv2_evaluation/            # CLIP 自动化评分
│   ├── hpsv2_scorer.py
│   ├── evaluate_hpsv2.py
│   └── run_evaluation.py
│
├── Evaluation-Agent/             # VLM 智能评分
│   ├── eval_agent/
│   │   ├── eval_agent_scorer.py
│   │   └── evaluate_agent.py
│   ├── dataset/
│   └── assets/
│
├── input_images/                 # 输入参考图像
│   ├── 商品图.jpg
│   ├── 模特图.jpg
│   └── 场景图.jpg
│
├── output_images/                # 生成结果输出
│
└── report/                       # 评测报告
    └── report.md
```

## 数据流

```
输入提示词 (config.py::IMAGE_GENERATION_PROMPTS)
        │
        ▼
┌───────────────────┐
│  图像生成模块      │
│  Text-to-Image/   │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  output_images/  │
└───────────────────┘
        │
        ▼
┌───────────────────┐     ┌───────────────────┐
│  HPSv2_evaluation │     │ Evaluation-Agent  │
│  (CLIP评分)       │     │ (VLM评分)         │
└───────────────────┘     └───────────────────┘
        │                         │
        └────────┬────────────────┘
                 ▼
        ┌───────────────────┐
        │   report.md      │
        └───────────────────┘
```

---

*最后更新: 2026-03-26*
