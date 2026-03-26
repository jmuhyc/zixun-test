# 工作流程文档

## 常用工作流程

---

## 流程 1: 文本到图像生成

### 步骤

1. **准备提示词**
   - 编辑 `config.py` 中的 `IMAGE_GENERATION_PROMPTS`

2. **选择 API**
   - Nano Pro: `Text-to-Image/nano_pro_gen.py`
   - WanX: `Text-to-Image/wanx_gen.py`
   - Seedream: `Text-to-Image/seedream_gen.py`
   - Hunyuan: `Text-to-Image/hunyuan_gen.py`

3. **运行脚本**
   ```bash
   python Text-to-Image/wanx_gen.py
   ```

4. **检查输出**
   - 生成图像保存在 `output_images/`

### 输出
```
output_images/
├── wanx_商品图_001.png
├── wanx_模特图_001.png
└── ...
```

---

## 流程 2: 图像到图像生成

### 步骤

1. **准备输入图像**
   - 将参考图放入 `input_images/`

2. **选择 API**
   - WanX: `Image-to-Image/wanx_img2img.py`
   - Seedream: `Image-to-Image/seedream_img2img.py`
   - Hunyuan: `Image-to-Image/hunyuan_img2img.py`

3. **运行脚本**
   ```bash
   python Image-to-Image/wanx_img2img.py
   ```

---

## 流程 3: HPSv2 自动评分

### 步骤

1. **准备**
   - 确保 `output_images/` 有待评测图像

2. **运行评测**
   ```bash
   python HPSv2_evaluation/run_evaluation.py
   ```

3. **查看结果**
   - 控制台输出各图像的 HPSv2 分数

### 评分维度
- Prompt Adherence (提示词一致性)
- Visual Quality (视觉质量)

---

## 流程 4: VLM 智能评分

### 步骤

1. **配置模型**
   - 编辑 `Evaluation-Agent/eval_agent/evaluate_agent.py`
   - 选择 `gpt-4v` 或 `qwen-vl`

2. **运行评测**
   ```bash
   python Evaluation-Agent/eval_agent/evaluate_agent.py
   ```

3. **查看结果**
   - 生成详细评分报告

### 评分维度
- Prompt Adherence (提示词一致性)
- Functional Quality (功能质量)
- Consistency (一致性)
- Visual Aesthetics (视觉美学)
- Output Specifications (输出规格)

---

## 流程 5: 完整评测流程

### 推荐顺序

```
1. 文本到图像生成
        │
        ▼
2. 图像到图像生成 (可选)
        │
        ▼
3. HPSv2 自动评分
        │
        ▼
4. VLM 智能评分
        │
        ▼
5. 生成报告
```

### 脚本执行顺序

```bash
# 1. 生成图像
python Text-to-Image/wanx_gen.py
python Text-to-Image/seedream_gen.py
python Text-to-Image/hunyuan_gen.py

# 2. HPSv2 评分
python HPSv2_evaluation/run_evaluation.py

# 3. VLM 评分
python Evaluation-Agent/eval_agent/evaluate_agent.py
```

---

## 快速参考

| 任务 | 命令 |
|------|------|
| 安装依赖 | `pip install -r requirements.txt` |
| 生成图像 | `python Text-to-Image/<api>_gen.py` |
| img2img | `python Image-to-Image/<api>_img2img.py` |
| HPSv2评分 | `python HPSv2_evaluation/run_evaluation.py` |
| VLM评分 | `python Evaluation-Agent/eval_agent/evaluate_agent.py` |

---

*最后更新: 2026-03-26*
