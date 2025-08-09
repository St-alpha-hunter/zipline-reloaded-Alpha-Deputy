"""
模块说明：executor.py

职责：
    - 封装 zipline 的回测调用逻辑
    - 动态加载策略 .py 文件，提取 initialize / handle_data 函数
    - 使用 zipline.run_algorithm 执行策略
    - 返回回测结果（净值、指标、图表等）

使用方式：
    - 输入参数：策略文件路径、回测时间段、初始资金等
    - 输出：回测结果 dataframe，可用于生成图表 / JSON 返回

TODO：
    [ ] 实现：execute_strategy(strategy_path, start_date, end_date, ...)
    [ ] 支持异常处理，如策略文件无效、时间不合法等
    [ ] 支持结果图像生成（base64）或结构化回测指标
    [ ] 后续可对接报告归档模块
"""