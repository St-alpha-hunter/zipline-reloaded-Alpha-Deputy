from zipline.api import order, record, symbol
from zipline import run_algorithm
import pandas as pd

def initialize(context):
    context.asset = symbol('AAPL')

def handle_data(context, data):
    order(context.asset, 1)
    record(price=data.current(context.asset, 'price'))

start = pd.Timestamp('2020-01-01', tz='utc')
end = pd.Timestamp('2020-12-31', tz='utc')

result = run_algorithm(
    start=start, end=end,
    initialize=initialize,
    handle_data=handle_data,
    capital_base=10000,
    data_frequency='daily',
    bundle='quantopian-quandl'  # 或自定义 bundle
)
print(result.tail())
