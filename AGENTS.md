# AGENTS.md - 项目宪法

> 这是项目的"入职手册"。AI 启动时的第一份必读文件。

## 项目简介

**项目名称**: zixun-test2
**类型**: Python AI 图像生成模型评测工具
**核心功能**: 集成4个图像生成API（Nano Pro/Gemini, WanX, Seedream, Hunyuan）进行文本到图像和图像到图像生成，并提供自动化评分。

## 技术栈

- **语言**: Python 3.8+
- **依赖管理**: pip, requirements.txt
- **主要库**:
  - `requests` - HTTP 请求
  - `dashscope` - 阿里 DashScope SDK (WanX)
  - `volcengine-python-sdk[ark]` - 字节火山引擎 SDK (Seedream)
  - `torch`, `transformers`, `CLIP` - 深度学习/评分
  - `Pillow` - 图像处理

## 代码风格规范

- 遵循 **PEP 8** 标准
- 使用 **Black** 格式化（line-length: 88）
- 使用 **Isort** 排序导入

## 必需命令集

```bash
# 安装依赖
pip install -r requirements.txt

# 文本到图像生成
python Text-to-Image/nano_pro_gen.py
python Text-to-Image/wanx_gen.py
python Text-to-Image/seedream_gen.py
python Text-to-Image/hunyuan_gen.py

# 图像到图像生成
python Image-to-Image/wanx_img2img.py
python Image-to-Image/seedream_img2img.py
python Image-to-Image/hunyuan_img2img.py

# 自动化评分
python HPSv2_evaluation/run_evaluation.py
python Evaluation-Agent/eval_agent/evaluate_agent.py
```

## 依赖规则

**允许引入的第三方库**:
- `requests`, `dashscope`, `volcengine-python-sdk`
- `torch`, `torchvision`, `transformers`, `CLIP`
- `Pillow`, `pandas`, `numpy`

**禁止引入的库**:
- 未经确认的所有其他第三方库

## 禁止事项

- **不要修改 `config.py`** - 包含敏感 API 密钥
- **不要提交 `config.py` 到版本控制** - 已添加到 .gitignore
- **不要在代码中硬编码 API 密钥** - 使用 config.py 中的配置

## 项目结构

```
zixun-test/
├── config.py                    # API密钥（禁止修改）
├── config.example.py            # 配置模板
├── requirements.txt             # 依赖
├── Text-to-Image/               # 文本到图像生成
├── Image-to-Image/              # 图像到图像生成
├── HPSv2_evaluation/           # CLIP自动评分
├── Evaluation-Agent/            # VLM智能评分
├── input_images/                # 输入参考图
├── output_images/               # 生成结果
└── report/                      # 评测报告
```

## 知识库索引

- [架构文档](docs/architecture.md) - 项目架构和模块关系
- [API 文档](docs/api.md) - 各图像生成API调用方式
- [工作流程](docs/workflow.md) - 常用工作流程

## 技能模块索引

- [代码审查 SOP](skills/code-review.md)
- [功能开发 SOP](skills/feature-generation.md)
- [Bug修复 SOP](skills/bug-fix.md)
- [测试 SOP](skills/testing.md)

---

## 角色定义

| 角色 | 职责 |
|------|------|
| **人类** | 架构师和产品经理：定义高层次目标、架构设计、产品需求 |
| **AI** | 高级工程师和执行者：根据指令完成编码、测试、文档任务 |

## 工作流程

1. **任务分解**: 人类将大任务分解为 AI 可以理解和执行的小任务
2. **执行**: AI 根据 SOP 和规范执行任务
3. **审查与批准**: AI 完成工作后，人类进行最终审查
4. **持续学习**: AI 犯错时，规则迭代到 AGENTS.md 或相应 skill.md

## 持续学习规则

当 AI 犯错时：
1. 人类修正错误
2. 将修正规则写入 AGENTS.md 或相应 skill.md
3. AI 下次不再犯同样的错误

---

*最后更新: 2026-03-26*
