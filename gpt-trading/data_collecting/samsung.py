"""
GPT 프롬프트: 파이썬의 pykrw 모듈을 활용하여 삼성전자의 OHLCV(시가, 고가, 저가, 종가, 거래량)와 펀더멘털 지표(BPS, PER, PBR, EPS, DIV, DPS)에 대한 1년 동안의 데이터를 병합하여 CSV 파일로 만들 수 있는 코드를 만들어주세요.
"""

import os
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the stock code and date range
stock_code = "005930"  # Samsung Electronics
today = datetime.today()
one_year_ago = today - timedelta(days=365)
start_date = one_year_ago.strftime("%Y%m%d")
end_date = today.strftime("%Y%m%d")

# Fetch OHLCV data
ohlcv_data = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
ohlcv_data = ohlcv_data.reset_index()  # Reset the index to make the date a column
ohlcv_data.rename(columns={"날짜": "Date"}, inplace=True)  # Rename the date column to 'Date'
ohlcv_data["Date"] = pd.to_datetime(ohlcv_data["Date"])  # Ensure 'Date' is in datetime format

# Fetch fundamental data
fundamental_data = stock.get_market_fundamental_by_date(start_date, end_date, stock_code)
fundamental_data = fundamental_data.reset_index()  # Reset the index to make the date a column
fundamental_data.rename(columns={"날짜": "Date"}, inplace=True)  # Rename the date column to 'Date'
fundamental_data["Date"] = pd.to_datetime(fundamental_data["Date"])  # Ensure 'Date' is in datetime format

# Merge OHLCV and fundamental data
merged_data = pd.merge(ohlcv_data, fundamental_data, on="Date")

# Save to CSV file in the same directory as the script
output_file = os.path.join(current_dir, "samsung_ohlcv_fundamental.csv")
merged_data.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Data saved to {output_file}")