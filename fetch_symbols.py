import os
import requests
import pandas as pd
from dotenv import load_dotenv

# 加载 .env 文件中的 API KEY
load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")
if not API_KEY:
    raise ValueError("FMP_API_KEY not set in .env file!")

# FMP symbol 列表 API
SYMBOL_LIST_URL = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={API_KEY}"

def fetch_and_save_symbols():
    print("Fetching symbol list from FMP...")
    response = requests.get(SYMBOL_LIST_URL)
    #检查 HTTP 响应状态码
    response.raise_for_status()
    #解析 JSON 数据
    data = response.json()

    print(f"Total symbols fetched: {len(data)}")

    # 转为DataFrame，筛选主板市场（可按需调整）
    df = pd.DataFrame(data)
    df = df[df['exchangeShortName'].isin(['NASDAQ', 'NYSE', 'AMEX']) & df['type'].isin(['stock'])]
    # 显示哪些交易所被拉到了
    print("Fetched exchanges:", df['exchangeShortName'].dropna().unique())

    df = df[(df['price'] > 0)]


    # 写入 symbols.txt
    symbols = df["symbol"].dropna().unique()
    with open("symbols.txt", "w") as f:
        for sym in symbols:
            f.write(f"{sym}\n")

    print(f"Saved {len(symbols)} symbols to symbols.txt")

if __name__ == "__main__":
    fetch_and_save_symbols()
