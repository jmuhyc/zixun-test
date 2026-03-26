# Testing SOP - 测试编写标准流程

> 用于编写和运行测试，确保代码质量。

## 前置条件

- [ ] 待测试代码已编写
- [ ] `pytest` 已安装
- [ ] 了解测试目标

## 执行步骤

### 1. 确定测试范围

1. 识别需要测试的函数/模块
2. 确定测试类型：
   - **单元测试**: 单一函数/方法
   - **集成测试**: 多模块协作
   - **端到端测试**: 完整流程

### 2. 编写测试

**测试文件位置**: `tests/` 目录

**命名规范**:
```
tests/
├── test_<module_name>.py       # 模块测试
├── test_<feature>.py           # 功能测试
└── conftest.py                # pytest 配置
```

**测试模板**:

```python
"""
测试模块说明
"""

import pytest
from module_under_test import function_name


class TestFunctionName:
    """测试类：测试 function_name"""

    def test_normal_case(self):
        """测试正常输入"""
        # Arrange
        input_data = "test"

        # Act
        result = function_name(input_data)

        # Assert
        assert result == expected_output

    def test_edge_case(self):
        """测试边界条件"""
        # Arrange
        input_data = ""

        # Act & Assert
        with pytest.raises(ValueError):
            function_name(input_data)
```

### 3. 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_module.py

# 运行特定测试函数
python -m pytest tests/test_module.py::TestClass::test_function

# 显示详细输出
python -m pytest tests/ -v

# 显示 print 输出
python -m pytest tests/ -s
```

### 4. 检查覆盖率

```bash
# 安装 coverage
pip install pytest-cov

# 运行覆盖率测试
python -m pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 测试最佳实践

1. **Arrange-Act-Assert (AAA) 模式**
   - Arrange: 准备测试数据
   - Act: 执行被测操作
   - Assert: 验证结果

2. **单一职责**: 每个测试函数只测试一个行为

3. **独立性**: 测试之间无依赖

4. **可重复性**: 测试结果稳定，不依赖外部状态

5. **清晰的命名**: 测试名称描述预期行为

## 常见问题处理

| 问题 | 解决方案 |
|------|---------|
| API 调用失败 | 使用 mock 或检查网络 |
| 图像处理不确定 | 使用固定种子或预设图像 |
| 顺序依赖 | 使用 fixture 确保顺序 |

---

*最后更新: 2026-03-26*
