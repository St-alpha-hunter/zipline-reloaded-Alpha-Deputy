"""
模块说明：strategy_generator.py

职责：
    - 专注于使用 Jinja2 渲染策略模板
    - 将用户的参数（symbols、调仓频率、止盈止损等）注入模板
    - 输出一份标准 Python 策略脚本，供 zipline 执行

使用方式：
    - 加载 templates/strategy_template.py.j2 模板
    - 将传入参数 dict 作为上下文，渲染模板
    - 写入一个临时策略 .py 文件，返回文件路径

TODO：
    [ ] 实现：render_strategy(params: dict, output_path: str)
    [ ] 支持参数：symbols、权重、风控参数、调仓周期等
    [ ] 后续可添加多模板支持（如多因子策略、动量策略等）
"""
