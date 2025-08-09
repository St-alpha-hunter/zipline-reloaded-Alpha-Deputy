import datetime
import os
from zipline.data.bundles.fmp import load_fmp_bulk_data  # 主逻辑来自 fmp.py

def get_yesterday_today():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    return yesterday.isoformat(), today.isoformat()

if __name__ == "__main__":
    with open("symbols.txt") as f:
        symbols = [line.strip() for line in f if line.strip()]

    from_date, to_date = get_yesterday_today()
    print(f"Updating data from {from_date} to {to_date}...")

    # 推荐用绝对路径
    output_path = os.path.abspath(
        "C:/Users/K.Hawk/zipline-reloaded-Alpha-Deputy/src/zipline/data/bundles/data/data_cache/all_stocks.parquet"
    )

    load_fmp_bulk_data(
        symbols,
        from_date=from_date,
        to_date=to_date,
        output_path=output_path,
        show_progress=True
    )
