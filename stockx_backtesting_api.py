# -*- coding: utf-8 -*-
"""
 ***************************************************************************
 * Copyright (C) 2023, Lanka Hsu, <lankahsu@gmail.com>, et al.
 *
 * This software is licensed as described in the file COPYING, which
 * you should have received as part of this distribution.
 *
 * You may opt to use, copy, modify, merge, publish, distribute and/or sell
 * copies of the Software, and permit persons to whom the Software is
 * furnished to do so, under the terms of the COPYING file.
 *
 * This software is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY
 * KIND, either express or implied.
 *
 ***************************************************************************
"""

#import os, sys, errno, getopt, signal, time, io
#from time import sleep
from pythonX9 import *
from threadx_api import *

import pandas as pd
import numpy
import requests, json

from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta

from pathlib import Path
from calendar import monthrange

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

stock_splits = [ ("0050", pd.Timestamp("2025-06-18"), 1/4) ]

class stockx_backtesting_ctx(pythonX9):

	def is_otc_stock(self, stock_no, year, month):
		"""判斷股票是否是櫃買（OTC）"""
		#date = f"{year}{month:02d}01"
		#url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20251101&stockNo=0050'
		#url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock_no}'
		#url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo=0050'
		url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={stock_no}'
		try:
			r = requests.get(url, timeout=2)
			data = r.json()
			self.is_otc = data.get("stat") != "OK"
		except Exception:
			self.is_otc = True

	def fetch_otc_monthly(self, stock_no, year, month):
		"""抓取櫃買股票整個月份的每日資料"""
		date = f"{year}/{month:02d}/01"
		#url = f'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={stock_no}&date={date}&response=csv'
		url = f'https://www.tpex.org.tw/www/zh-tw/afterTrading/tradingStock?code={stock_no}&date={date}'
		#headers = {"User-Agent": "Mozilla/5.0"}
		res = requests.get(url)
		res.encoding = 'utf-8'
		data = res.json()
		if data.get("stat") != "ok" or "tables" not in data or not data["tables"]:
			return pd.DataFrame()

		records = []
		for row in data["tables"][0]["data"]:
			try:
				# 日期轉換：113/01/02 → 2024-01-02
				date_str = row[0]
				# ['112/12/05*', '237,645', '3,669,097', '15.21', '15.65', '15.21', '15.65', '0.54', '44,683']: invalid literal for int() with base 10: '05*'
				date_str.replace("*", "")
				y, m, d = map(int, date_str.split("/"))
				full_date = pd.Timestamp(year=y + 1911, month=m, day=d)

				close_price = float(row[6].replace(",", ""))
				records.append({"DATE": full_date, "CLOSEYEST": close_price})
			except Exception as e:
				print(f"\r[跳過錯誤資料] {row}: {e}")
				continue

		return pd.DataFrame(records)

	def fetch_twse_monthly(self, stock_no, year, month):
		date = f"{year}{month:02d}01"
		#https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=20250613&stockNo=0050
		url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock_no}'
		res = requests.get(url)
		res.encoding = 'utf-8'
		data = res.json()
		if data['stat'] != 'OK':
			return pd.DataFrame()

		df = pd.DataFrame(data['data'], columns=data['fields'])

		# 民國年轉西元年（例如 113/01/02 → 2024-01-02）
		df['日期'] = df['日期'].apply(lambda x: f"{1911 + int(x.split('/')[0])}-{x.split('/')[1]}-{x.split('/')[2]}")
		df['日期'] = pd.to_datetime(df['日期'], format="%Y-%m-%d")

		df['收盤價'] = pd.to_numeric(df['收盤價'].str.replace(',', ''), errors='coerce')
		return df[['日期', '收盤價']].rename(columns={'日期': 'DATE', '收盤價': 'CLOSEYEST'})

	def fetch_stock_auto(self, stock_no, year, month):
		"""自動抓取股票資料（可辨識上櫃 vs 上市）"""
		if (self.is_otc == True) :
			return self.fetch_otc_monthly(stock_no, year, month)
		else:
			return self.fetch_twse_monthly(stock_no, year, month)

	def fetch_helper(self, stock_history, stock_last_date):
		print("[{}] ".format(self.stock_no), end="", flush=True)

		if stock_history is None:
			all_data = pd.DataFrame()
		else:
			all_data = stock_history

		delta = self.NOW_t.date() - self.stock_last_date.date()

		print(f"(stock_last_date：{self.stock_last_date.date()}, delta.days: {delta.days}, stock_delta_days: {self.stock_delta_days}) ", end="", flush=True)
		if ( delta.days >= self.stock_delta_days ):
			self.is_otc_stock(self.stock_no, self.NOW_t.year, self.NOW_t.month)

			current = (stock_last_date.replace(day=1)).date()
			end = datetime(self.NOW_t.year, self.NOW_t.month, 1).date()

			while current <= end:
				y, m = current.year, current.month

				if self.is_quit == 1:
					break

				if ( self.is_new == False ):
					self.is_new= True

				df = self.fetch_stock_auto(self.stock_no, y, m)
				all_data = pd.concat([all_data, df]).drop_duplicates(subset="DATE").reset_index(drop=True)
				print(".", end="", flush=True)

				sleep(0.5)

				current = (current + relativedelta(months=1))  # 下一個月

		if hasattr(all_data, "DATE"):
			all_data = all_data.sort_values(by='DATE').reset_index(drop=True)
		else:
			all_data = None
			DBG_ER_LN("all_data is None !!!")

		if ( self.is_quit == 1 ):
			print(" Quit !!!", flush=True)
		else:
			print(" Completed !!!", flush=True)
		return all_data

	def buy_prices_helper(self):
		if self.stock_history is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		self.buy_return = []
		df = self.stock_history

		end_date = pd.Timestamp.today() - pd.Timedelta(days=1)
		short_years_ago = pd.Timestamp.today() - pd.DateOffset(years=self.buy_short)
		medium_years_ago = pd.Timestamp.today() - pd.DateOffset(years=self.buy_medium)
		long_years_ago = pd.Timestamp.today() - pd.DateOffset(years=self.buy_long)

		def adjust_price(date, price):
			for stock_no, split_date, factor in self.stock_splits:
				if ( self.stock_no == stock_no ):
					if date < split_date:
						price *= factor
			return price

		for day in range(1, 32):  # 每月 1～31 日
			buy_prices_short = []
			buy_prices_medium = []
			buy_prices_long = []

			for date in pd.date_range(long_years_ago, end_date, freq="MS"):
				year, month = date.year, date.month
				max_day = monthrange(year, month)[1]
				if day <= max_day:
					try_day = pd.Timestamp(year=year, month=month, day=day)

					# 找 try_day 之前的最後一筆記錄（前一筆）
					past_day = df[df["DATE"] < try_day]
					if not past_day.empty:
						prev_record = past_day.iloc[-1]
						closeyest = prev_record["CLOSEYEST"]
						record_date = prev_record["DATE"]
						closeyest = adjust_price(record_date, closeyest)

						if not numpy.isnan(closeyest):
							buy_prices_long.append(closeyest)

							if try_day >= short_years_ago:
								buy_prices_short.append(closeyest)
							if try_day >= medium_years_ago:
								buy_prices_medium.append(closeyest)

			# --- 報酬率計算 ---
			def calc_return(prices, final_price):
				if not prices or final_price is None:
						return {
								"return_pct": None,
								"avg_price": None,
								"count": 0
						}

				avg_price = sum(prices) / len(prices)
				return_pct = round((final_price - avg_price) / avg_price * 100, 2)

				return {
						"return_pct": return_pct,
						"avg_price": round(avg_price, 4),
						"count": len(prices)
				}

			#final_price = df[df["DATE"] == end_date]["CLOSEYEST"].values[0]
			final_row = df[df["DATE"] <= end_date].sort_values("DATE", ascending=False).head(1)
			if not final_row.empty:
				final_price = final_row.iloc[0]["CLOSEYEST"]
			else:
				final_price = None  # 或 raise 錯誤 / 給預設值

			self.buy_return.append({
					"Day": day
					,"Short": calc_return(buy_prices_short, final_price)
					,"Medium": calc_return(buy_prices_medium, final_price)
					,"Long": calc_return(buy_prices_long, final_price)
			})
			self.final_price = final_price

	def buy_return_plot_lines_on_screen(self):
		if self.buy_return is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		DBG_IF_LN("Plotting lines ...")

		# --- 匯出結果 ---
		report_df = pd.DataFrame(self.buy_return)

		# 解析巢狀結構
		report_df["Short_return"] = report_df["Short"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)
		report_df["Medium_return"] = report_df["Medium"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)
		report_df["Long_return"] = report_df["Long"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)

		# 畫圖
		plt.figure(figsize=(12, 6))
		plt.plot(report_df["Day"], report_df["Short_return"], label=f"{self.buy_short}-Year", color="red", marker="o")
		plt.plot(report_df["Day"], report_df["Medium_return"], label=f"{self.buy_medium}-Year", color="blue", marker="o")
		plt.plot(report_df["Day"], report_df["Long_return"], label=f"{self.buy_long}-Year", color="green", marker="o")

		plt.axhline(0, color="gray", linestyle="--")  # 零報酬線

		plt.title(f"{self.stock_no}", fontsize=14)
		plt.xlabel("Day (1~31)")
		plt.ylabel("Rate of return (%)")
		plt.legend()
		plt.grid(True)
		plt.tight_layout()
		plt.show()

	def buy_return_plot_bars_on_screen(self):
		if self.buy_return is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		DBG_IF_LN("Plotting ...")

		# --- 匯出結果 ---
		report_df = pd.DataFrame(self.buy_return)

		# 解析巢狀結構
		report_df["Short_return"] = report_df["Short"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)
		report_df["Medium_return"] = report_df["Medium"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)
		report_df["Long_return"] = report_df["Long"].apply(lambda x: x.get("return_pct") if isinstance(x, dict) else None)

		# 畫圖
		plt.figure(figsize=(12, 6))

		x = np.arange(len(report_df))  # X 座標：0,1,2,...
		width = 0.25            # 條形寬度
		plt.bar(x-width, report_df["Short_return"], width, label=f"{self.buy_short}-Year", color="red")
		plt.bar(x, report_df["Medium_return"], width, label=f"{self.buy_medium}-Year", color="blue")
		plt.bar(x+width, report_df["Long_return"], width, label=f"{self.buy_long}-Year", color="green")
		plt.xticks(x, report_df["Day"])

		plt.axhline(0, color="gray", linestyle="--")  # 零報酬線

		plt.title(f"{self.stock_no}", fontsize=14)
		plt.xlabel("Day (1~31)")
		plt.ylabel("Rate of return (%)")
		plt.legend()
		plt.grid(True)
		plt.tight_layout()
		plt.show()

	def buy_return_display_on_screen(self):
		if self.buy_return is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		# --- 匯出結果 ---
		report_df = pd.DataFrame(self.buy_return)
		#report_df["Day"] = report_df["Day"].astype(int)
		#print(report_df)
		#print(report_df.dtypes)
		print("Day {}-Year                  {}-Year                  {}-Year                  Sum".format(self.buy_short, self.buy_medium, self.buy_long) )
		print(f"{'':<4}{'(%)':<7}{'count':<7}{'average':<10}{'(%)':<7}{'count':<7}{'average':<10}{'(%)':<7}{'count':<7}{'average':<10}(%)")
		for idx, row in report_df.iterrows():
			print("{:<4}".format( int(row['Day']) ), end="")
			print("{:<7}{:<7}{:<10.02f}".format( row['Short']['return_pct'], row['Short']['count'], row['Short']['avg_price'] ), end="")
			print("{:<7}{:<7}{:<10.02f}".format( row['Medium']['return_pct'], row['Medium']['count'], row['Medium']['avg_price'] ), end="")
			print("{:<7}{:<7}{:<10.02f}".format( row['Long']['return_pct'], row['Long']['count'], row['Long']['avg_price'] ), end="" )
			print("{:<10.02f}".format( row['Short']['return_pct'] + row['Medium']['return_pct'] + row['Long']['return_pct'] ) )
			#print("{:<4}{:<6}{:<7}{:<10.02f}{:<6}{:<7}{:<10.02f}".format( int(row['Day']), row['Short']['return_pct'], row['Short']['count'], row['Short']['avg_price'], row['Medium']['return_pct'], row['Medium']['count'], row['Medium']['avg_price']))
			#print("[{}] ".format(self.stock_no), end="", flush=True)

		print("(stock_no: {}, final_price: {})".format( self.stock_no, self.final_price ))

	def history_load_from_csv(self):
		DBG_IF_LN("Found !!! ({}), Loading ...".format(self.history_filename))
		self.stock_history = pd.read_csv(self.history_filename, encoding="utf-8-sig")
		self.stock_history["DATE"] = pd.to_datetime(self.stock_history["DATE"])
		self.stock_history["CLOSEYEST"] = pd.to_numeric(self.stock_history["CLOSEYEST"], errors="coerce")
		self.stock_history = self.stock_history.sort_values(by='DATE').reset_index(drop=True)

		if not self.stock_history.empty and "DATE" in self.stock_history.columns:
			self.stock_last_date = self.stock_history["DATE"].max()
		else:
			DBG_ER_LN("stock_history is None !!!")

	def history_exists(self):
		return Path(self.history_filename).exists()

	def history_save_to_csv(self):
		if self.stock_history is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		# 儲存 CSV（可選）
		if ( self.is_new == True ):
			self.stock_history.to_csv(self.history_filename, index=False, encoding="utf-8-sig")

	def history_display_on_screen(self):
		if self.stock_history is None:
			DBG_ER_LN("stock_history is None !!!")
			return

		df = self.stock_history
		# 自訂格式化輸出
		print("{:<12} {:<14}".format( "DATE", "CLOSEYEST") )
		for idx, row in df.iterrows():
			#print("{:<12} {:<14.2f}".format( row['DATE'].strftime('%Y-%m-%d'), row['CLOSEYEST']) )
			#print("{:<12}".format( row['DATE'].strftime('%Y-%m-%d') ) )
			if pd.notna(row['CLOSEYEST']):
				print("{:<12} {:<14.2f}".format( row['DATE'].strftime('%Y-%m-%d'), row['CLOSEYEST'] ))
			else:
				print("{:<12} {}".format( row['DATE'].strftime('%Y-%m-%d'), "" ))

	def release(self):
		if ( self.is_quit == 0 ):
			self.is_quit = 1
			DBG_DB_LN("{}".format(DBG_TXT_DONE))

	def ctx_init(self):
		DBG_DB_LN("{}".format(DBG_TXT_ENTER))

		self.NOW_t = datetime.today()

		self.stock_history = None
		self.buy_return = None
		self.is_otc = False

		self.stock_splits = sorted(stock_splits, key=lambda x: x[0], reverse=True)  # 自動由新到舊排序

	def __init__(self, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(stockx_backtesting_ctx, self).__init__(**kwargs)

		self._kwargs = kwargs
		self.ctx_init()

	def parse_args(self, args):
		DBG_TR_LN("{}".format(DBG_TXT_ENTER))
		self._args = args

		self.stock_no = args["stock_no"]
		self.year_ago = args["year_ago"]
		self.stock_last_date = self.NOW_t - relativedelta(years=self.year_ago)
		self.stock_delta_days = args["delta"]

		self.renew = args["renew"]

		self.buy_short = args["buy_short"]
		self.buy_medium = args["buy_medium"]
		self.buy_long = args["buy_long"]

		self.history_folder = args["history_folder"]

		dir_mkdir(self.history_folder)

		self.history_filename = f"{self.history_folder}/{self.stock_no}_history.csv"

	def start(self, args={}):
		DBG_TR_LN("{}".format(DBG_TXT_START))
		self.parse_args(args)
		if ( self.renew == False) and ( self.history_exists() ):
			self.history_load_from_csv()

		self.is_new = False
		self.stock_history = self.fetch_helper(self.stock_history, self.stock_last_date)

		#self.buy_prices_helper()

#stockx_backtesting_mgr = stockx_backtesting_ctx("HelloStockX")
#stockx_backtesting_mgr.start()
#stockx_backtesting_mgr.display_on_screen()
#stockx_backtesting_mgr.save_to_csv()

