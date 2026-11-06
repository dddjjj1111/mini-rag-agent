# pytest 基础

pytest 会自动发现以 `test_` 开头的文件和函数。

常用写法：

```python
def test_add():
    assert 1 + 1 == 2
```

运行：在项目根目录执行 `pytest -q`。
失败时看断言信息和堆栈，先复现再改代码。
