# Feature Generation SOP - 功能开发标准流程

> 用于从零开始生成和实现新功能。

## 前置条件

- [ ] 需求已明确
- [ ] 架构设计已确认（参考 [docs/architecture.md](docs/architecture.md)）
- [ ] 相关 API 文档已阅读（参考 [docs/api.md](docs/api.md)）

## 执行步骤

### 1. 理解需求

1. 明确功能目标
2. 确定输入输出
3. 识别依赖模块
4. 评估影响范围

### 2. 设计实现

1. 选择合适的模块位置
2. 设计函数/类接口
3. 考虑扩展性

### 3. 编写代码

**模板**:

```python
"""
功能说明

Args:
    param1: 参数1说明
    param2: 参数2说明

Returns:
    返回值说明

Raises:
    ExceptionType: 异常说明
"""

def function_name(param1, param2):
    """函数文档字符串"""
    # 实现
    pass
```

### 4. 自检清单

- [ ] 代码遵循 PEP 8
- [ ] 文档字符串完整
- [ ] 类型注解清晰
- [ ] 错误处理完善
- [ ] 无硬编码配置

### 5. 格式化

```bash
# 格式化代码
black <new_file.py>
isort <new_file.py>
```

## 验证方法

1. 单元测试（参考 [testing.md](testing.md)）
2. 手动验证功能
3. 检查输出结果

## 新增文件位置

| 功能类型 | 位置 |
|---------|------|
| 文本到图像生成 | `Text-to-Image/<name>_gen.py` |
| 图像到图像生成 | `Image-to-Image/<name>_img2img.py` |
| 评分功能 | `HPSv2_evaluation/` 或 `Evaluation-Agent/` |
| 工具脚本 | 项目根目录 |

## 规则引用

- 遵循 [AGENTS.md](AGENTS.md) 中的依赖规则
- 只允许引入允许列表中的库
- 不要修改 `config.py`

## 附录：API 凭证处理

### 安全原则

1. **永远不要在代码中硬编码 API 密钥**
2. **使用 config.py 存储密钥**，代码从中读取
3. **config.py 已添加到 .gitignore**，不要提交

### 正确示例

```python
# 正确：从 config 导入
from config import DASHSCOPE_API_KEY
os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

# 错误：硬编码密钥
API_KEY = "sk-xxx"  # 不要这样做！
```

### 图像生成脚本模板

```python
"""
{模型名称} 图像生成脚本

使用方式:
    python Text-to-Image/{model}_gen.py
"""

import os
import requests
from config import {MODEL_API_KEY}, IMAGE_GENERATION_PROMPTS

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../output_images")

def generate_{model}_image(prompt: str, **kwargs) -> dict:
    """生成图像"""
    # 设置 API Key
    os.environ["{MODEL_API_KEY}"] = {MODEL_API_KEY}

    # 调用 API
    # ...

    return {"success": True, "image_urls": [...]}

if __name__ == "__main__":
    for image_type, prompt in IMAGE_GENERATION_PROMPTS.items():
        result = generate_{model}_image(prompt=prompt, save_to_file=True)
```

## 附录：评测任务工作流

### OneIG-Bench 评测流程

1. **准备提示词**
   - 从 `OneIG-Benchmark/OneIG-Bench-ZH.csv` 加载提示词
   - 选择要评测的类别和数量

2. **生成图像**
   - 使用正确提示词 ID 保存图像
   - 格式: `{category}/{model}/{prompt_id}.png`

3. **运行评测**
   - Alignment: `python -m scripts.alignment.alignment_score ...`
   - 其他维度: `python -m scripts.{dimension}.{dimension}_score ...`

4. **解析结果**
   - 结果保存在 `results/` 目录
   - 使用 `fine_grained_analysis.py` 进行细粒度分析

### HPSv2 评测流程

```bash
python HPSv2_evaluation/run_evaluation.py
```

---

*最后更新: 2026-03-26*
