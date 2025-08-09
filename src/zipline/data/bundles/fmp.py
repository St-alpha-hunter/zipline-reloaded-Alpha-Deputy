from io import BytesIO
###用于在内存中读写二进制数据（如下载的文件内容），
###类似文件对象，常用于处理网络下载的内容。
import os
###import tarfile
###用于读取和解压.tar或.tar.gz等归档文件，
###常用于批量解压数据包。
import time
###from zipfile import ZipFile
###用于读取和解压.zip压缩包，
###常用于处理下载的zip格式数据文件。
###from click import progressbar
###click是一个命令行工具库
###用于在命令行显示进度条，提升用户体验。
import logging
import pandas as pd
import requests

from urllib.parse import urlencode
from dotenv import load_dotenv

from tqdm import tqdm  # ✅ 正确导入 tqdm 函数

from zipline.pipeline import data
from zipline.utils.calendar_utils import register_calendar_alias
from zipline.utils.standardize_fmp_data import standardize_fmp_data  # 导入函数
###from zipline.utils import daily_update;
###

from zipline.data.bundles import core as bundles
import numpy as np


load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")
log = logging.getLogger(__name__)
if not API_KEY:
    raise ValueError("FMP_API_KEY not set in .env or environment.")

ONE_MEGABYTE = 1024 * 1024
FMP_DATA_URL = "https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from={from_date}&to={to_date}&apikey={apikey}"
# 使用：
###url = FMP_DATA_URL.format(symbol="AAPL", apikey="API_KEY")
CACHE_DIR = os.path.join("data", "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 输出文件路径定义
OUTPUT_PATH = os.path.join(CACHE_DIR, "all_stocks.parquet")
##从FMP下载的zip文件中读取csv，解析为DataFrame，重命名部分字段。


def fetch_symbol_data(symbol, from_date, to_date, retries=3, delay=2, rate_delay=0.25):
    url = FMP_DATA_URL.format(symbol=symbol, from_date=from_date, to_date=to_date, apikey=API_KEY)
    for attempt in range(retries):
        try:
            time.sleep(rate_delay)  # 限速
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "historical" in data:
                historical = data["historical"]
            else:
                raise ValueError(f"Unexpected response format: {type(data)} -- content: {data}")

            df = pd.DataFrame(historical)
            df["symbol"] = symbol
            print(f"[DEBUG] Fetched raw data for {symbol}:")
            print(df.head(8))
            return df

        except Exception as e:
            log.warning(f"Error fetching {symbol}: {e}, retrying...")
            time.sleep(delay)

    return None



# def load_fmp_data(symbol, index_col, cache_dir, show_progress=False):
#     """
#     Load historical stock data for a symbol from FMP, cache as CSV, and return as DataFrame.
    
#     Parameters:
#     - symbol: Stock symbol string, e.g., "AAPL"
#     - index_col: Column to use as index, e.g., "date"
#     - cache_dir: Directory path to save CSV cache files
#     - show_progress: Whether to log progress info
#     """

#     ##可扩展建议（未来增强）：
#     ##✅ 批量加载多个symbol（封装成批处理器）
#     ##✅ 自动检测最新日期 → 更新增量数据
#     ##✅ CSV压缩（保存为 .csv.gz）
#     ##✅ 错误重试/异常处理更稳健

#     os.makedirs(cache_dir, exist_ok=True)
#     csv_path = os.path.join(cache_dir, f"{symbol}.csv")
    
#     if not os.path.exists(csv_path):
#         # Step 1: Download JSON from FMP
#         url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey=YOUR_API_KEY"
#         if show_progress:
#             log.info(f"Fetching data for {symbol} from FMP...")
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
        
#         historical = data.get("historical", [])
#         if not historical:
#             raise ValueError(f"No data found for symbol: {symbol}")
        
#         # Step 2: Convert JSON to DataFrame and save to CSV
#         data_table = pd.DataFrame(historical)
#         data_table.to_csv(csv_path, index=False)
    
#     # Step 3: Load CSV and process
#     if show_progress:
#         log.info(f"Loading cached data for {symbol}...")
#     data_table = pd.read_csv(
#         csv_path,
#         parse_dates=["date"],
#         index_col=index_col,
#         usecols=[
#             "date", "open", "high", "low", "close", "volume", "dividend", "splitCoefficient"
#         ]
#     )

#     # Step 4: Rename columns to unified style
#     data_table.rename(
#         columns={
#             "splitCoefficient": "split_ratio",
#             "dividend": "dividend",  # Already snake_case; can skip or include for clarity
#         },
#         inplace=True,
#         copy=False
#     )

#     return data_table


def load_fmp_bulk_data(symbols, from_date, to_date, output_path=OUTPUT_PATH, show_progress=True):
    all_data = []
    for symbol in tqdm(symbols, desc="Fetching symbols", disable=not show_progress):
            if os.path.exists(output_path):
                try:
                    existing_df = pd.read_parquet(output_path)
                    if symbol in existing_df["symbol"].unique():
                        print(f"[SKIP] {symbol} already exists, skipping.")
                        continue
                except Exception as e:
                    print(f"[WARN] Could not check existing file: {e}") 
            df = fetch_symbol_data(symbol, from_date, to_date)
            if df is not None:
                df = standardize_fmp_data(df)
                all_data.append(df)

    if not all_data:
        raise ValueError("No data fetched successfully.")

    full_data = pd.concat(all_data, ignore_index=True)

    # 保存追加或覆盖（建议 Parquet 多版本管理）
    if output_path.endswith(".parquet"):
        if os.path.exists(output_path):
            existing = pd.read_parquet(output_path)
            full_data = pd.concat([existing, full_data]).drop_duplicates(subset=["date", "symbol"])
        print(f"[INFO] Writing to: {output_path}")
        full_data.to_parquet(output_path, index=False)
        print(f"[DEBUG] Saved file to: {output_path}")
        print(f"[DEBUG] Writing to: {os.path.abspath(OUTPUT_PATH)}")
    else:
        full_data.to_csv(output_path, index=False)

    log.info(f"Data saved to {output_path}, total rows: {len(full_data)}")
    return full_data

PROJECT_ROOT = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(
                                os.path.dirname(
                                os.path.abspath(__file__)
                            )
                        )
                    )
                )
            )
SYMBOLS_FILE = os.path.join(PROJECT_ROOT, "symbols.txt")

def read_symbols_from_file(filepath=SYMBOLS_FILE):
    with open(filepath, "r") as f:
        symbols = [line.strip().upper() for line in f if line.strip()]
    return symbols

##直接保留===生成股票元数据（如起止日期、交易所、自动平仓日等）
def gen_asset_metadata(data, show_progress):
    if show_progress:
        log.info("Generating asset metadata.")

    data = data.groupby(by="symbol").agg({"date": [np.min, np.max]})
    data.reset_index(inplace=True)
    data["start_date"] = data.date[np.min.__name__]
    data["end_date"] = data.date[np.max.__name__]
    del data["date"]
    data.columns = data.columns.get_level_values(0)

    data["exchange"] = "QUANDL"
    data["auto_close_date"] = data["end_date"].values + pd.Timedelta(days=1)
    return data

##直接保留===解析拆股数据，转换字段名和比例
# def parse_splits(data, show_progress):
#     if show_progress:
#         log.info("Parsing split data.")

#     data["split_ratio"] = 1.0 / data.split_ratio
#     data.rename(
#         columns={
#             "split_ratio": "ratio",
#             "date": "effective_date",
#         },
#         inplace=True,
#         copy=False,
#     )
#     return data

##直接保留===解析分红数据，转换字段名
# def parse_dividends(data, show_progress):
#     if show_progress:
#         log.info("Parsing dividend data.")

#     data["record_date"] = data["declared_date"] = data["pay_date"] = pd.NaT
#     data.rename(
#         columns={
#             "ex_dividend": "amount",
#             "date": "ex_date",
#         },
#         inplace=True,
#         copy=False,
#     )
#     return data

##直接保留===按股票ID和交易日生成价格和成交量数据，供写入daily_bar_writer
def parse_pricing_and_vol(data, sessions, symbol_map):
    for asset_id, symbol in symbol_map.items():
        asset_data = (
            data.xs(symbol, level=1).reindex(sessions.tz_localize(None)).fillna(0.0)
        )
        yield asset_id, asset_data


##主函数入口

register_calendar_alias("FMP", "NYSE")


if __name__ == "__main__":
    test_symbols = read_symbols_from_file(SYMBOLS_FILE)
##  test_symbols = ["AAPL", "GOOGL","MSFT"]
    from_date = "2020-08-09"
    to_date = "2025-08-06"

    df = load_fmp_bulk_data(
        test_symbols,
        from_date,
        to_date,
        output_path=OUTPUT_PATH,
        show_progress=True
    )

    print(df.head())  # 查看前几行数据