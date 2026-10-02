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

	#**************************************************
	# 玉山SDK
	#**************************************************
from configparser import ConfigParser
from esun_trade.sdk import SDK as EsunSDK
from esun_trade.order import OrderObject
from esun_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)

from datetime import date, timedelta

#import os, sys, errno, getopt, signal, time, io
#from time import sleep
from utilsP9.utilsP9 import *
from utilsP9.threadx_api import *

class esunp9_ctx(utilsP9, threadx_ctx):
	QUANTITY_LOTS_UNIT = 1

	ACTION_BUY = Action.Buy
	ACTION_SELL = Action.Sell

	MARKETTYPE_COMMON = APCode.Common
	MARKETTYPE_AFTERMARKET = APCode.AfterMarket
	MARKETTYPE_INTRADAYODD = APCode.IntradayOdd
	MARKETTYPE_ODD = APCode.Odd

	PRICEFLAG_LIMIT = PriceFlag.Limit
	PRICEFLAG_FLAT = PriceFlag.Flat
	PRICEFLAG_LIMITDOWN = PriceFlag.LimitDown
	PRICEFLAG_LIMITUP = PriceFlag.LimitUp
	PRICEFLAG_MARKET = PriceFlag.Market

	BSFLAG_ROD = BSFlag.ROD
	BSFLAG_FOK = BSFlag.FOK
	BSFLAG_IOC = BSFlag.IOC

	TRADE_CASH = Trade.Cash
	TRADE_MARGIN = Trade.Margin
	TRADE_SHORT = Trade.Short
	TRADE_DAYTRADINGSELL = Trade.DayTradingSell
	#TRADE_SBL =

	DATE_HYPHEN = 0

	#**************************************************
	# Field Value
	#**************************************************
	# 可取消狀態
	def tradex_field_celable(self, item):
		if item['celable'] == "1":
			celable = f"yes"
		else:
			celable = f"no"
		return celable

	# 委託書編號
	def tradex_field_ord_no(self, item):
		if item['ord_no'] != "":
			ord_no = f"{item['ord_no']}"
		else:
			ord_no = f"{item['pre_ord_no']}"
		return ord_no

	# 預約狀態
	def tradex_field_pre_order(self, item):
		if 'ord_status' in item:
			if item['ord_status'] == "1":
				return f"預約單"
			else:
				return f"盤中單"
		else:
			return f"ｘｘｘ"

	# 股票代號
	def tradex_field_stk_no(self, item):
		if 'stock_no' in item:
			return f"{item['stock_no']}"
		elif 'stk_no' in item:
			return f"{item['stk_no']}"
		else:
			return f"xxx"

	# 股票名稱
	def tradex_field_stk_name(self, item):
		if 'stk_na' in item:
			return f"{item['stk_na']}"
		else:
			return f"xxx"

	# 買賣別
	def tradex_field_buy_sell(self, item):
		if item['buy_sell'] == "B":
			buy_sell = "買"
		else:
			buy_sell = "賣"
		return buy_sell

		# 原始委託數量
	def tradex_field_quantity(self, item):
		if 'org_qty_share' in item:
			return f"{item['org_qty_share']:,}"
		else:
			return f"xxx"

	# 交割日
	def tradex_field_s_date(self, item):
		if 'date' in item:
			return f"{item['date']}"
		else:
			return f"xxx"

	# 成交日
	def tradex_field_o_date(self, item):
		if 'c_date' in item:
			return f"{item['date']}"
		else:
			return f"xxx"

	# 日期
	def tradex_field_c_date(self, item):
		if 'c_date' in item:
			return f"{item['c_date']}"
		elif 'work_date' in item:
			return f"{item['work_date']}"
		elif 'ack_date' in item:
			return f"{item['ack_date']}"
		else:
			return f"xxx"

	# 已成交數量
	def tradex_field_mat_qty(self, item):
		if 'mat_qty_share' in item:
			return f"{int(item['mat_qty_share']):,}"
		elif 'qty' in item:
			return f"{int(item['qty']):,}"
		else:
			return f"xxx"

	# 取消數量
	def tradex_field_cel_qty(self, item):
		if 'cel_qty_share' in item:
			return f"{int(item['cel_qty_share']):,}"
		else:
			return f"xxx"

	# 昨餘額股數
	def tradex_field_qty_l(self, item):
		if 'qty_l' in item:
			return f"{int(item['qty_l']):,}"
		else:
			return f"xxx"

	# 委買成交股數
	def tradex_field_qty_bm(self, item):
		if 'qty_bm' in item:
			return f"{int(item['qty_bm']):,}"
		else:
			return f"xxx"

	# 賣成交股數
	def tradex_field_qty_sm(self, item):
		if 'qty_sm' in item:
			return f"{int(item['qty_sm']):,}"
		else:
			return f"xxx"

	# 委託價格
	def tradex_field_od_price(self, item):
		if 'od_price' in item:
			return f"{float(item['od_price']):,}"
		else:
			return f"xxx"

	# 成交均價
	def tradex_field_avg_price(self, item):
		if 'avg_price' in item:
			return f"{item['avg_price']:,}"
		elif 'price_avg' in item:
			return f"{float(item['price_avg']):,}"
		else:
			return f"xxx"

	# 即時價格
	def tradex_field_price_now(self, item):
		if 'price_now' in item:
			return f"{float(item['price_now']):,}"
		else:
			return f"xxx"

	# 交割款
	def tradex_field_settlement_price(self, item):
		if 'price' in item:
			return f"{float(item['price']):,}"
		else:
			return f"xxx"

	# 市場別
	def tradex_field_s_type(self, item):
		if 's_type' in item:
			match item['s_type']:
				case 'H':
					return f"上市"

				case 'O':
					return f"上櫃"

				case 'R':
					return f"興櫃"

				case _:
					return f"上市"
		else:
			return f"ｘｘｘ"

	# 錯誤碼
	def tradex_field_err_code(self, item):
		if 'err_code' in item:
			return f"{item['err_code']}"
		else:
			return f"xxx"


	#**************************************************
	# 交易下單
	#**************************************************
	def tradex_orders_get(self):
		return self.orders

	# 委託紀錄
	def tradex_q_orders(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		def orders_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'交易日期':<7} {'可取消':<4} {'買/賣':<4} {'股票代碼':<5} {'委託股數':<5} {'成交股數':<5} {'取消股數':<5} {'委託價格':<5} {'成交均價':<5} {'預約狀態':<5} {'錯誤碼':<6} {'委託書編號':<7}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				c_date_str = self.tradex_field_c_date(item)

				celable = self.tradex_field_celable(item)
				celable_str = f"{celable}"

				buy_sell_str = self.tradex_field_buy_sell(item)

				stk_no_str = self.tradex_field_stk_no(item)

				qty_sign = "+" if buy_sell_str == "買" else "-" if buy_sell_str == "賣" else ""
				qty_str = f"{qty_sign}{self.tradex_field_quantity(item)}"
				#qty_str = self.tradex_field_quantity(item)

				mat_qty_str = self.tradex_field_mat_qty(item)

				cel_qty_str = self.tradex_field_cel_qty(item)

				od_price_str = self.tradex_field_od_price(item)

				avg_price_str = self.tradex_field_avg_price(item)

				ord_status_str = self.tradex_field_pre_order(item)

				err_code = self.tradex_field_err_code(item)

				ord_no = self.tradex_field_ord_no(item)
				ord_no_str = f"{ord_no}"

				msg += f"{i:>3} - {c_date_str:<11} {celable_str:<7} {buy_sell_str:<5} {stk_no_str:<9} {qty_str:<9} {mat_qty_str:<9} {cel_qty_str:<9} {od_price_str:<9} {avg_price_str:<9} {ord_status_str:<6} {err_code:<9} {ord_no_str:<12}{comma}"
			msg += "\n\n]"
			return msg

		self.orders = self.trade_sdk.get_order_results()
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				JSON_IF_FORMAT(self.orders, jstyle=JSTYLE.ARRAY)
			else:
				JSON_IF_FORMAT(self.orders, jstyle=JSTYLE.ARRAY, filter_cb=orders_filter_cb)

		return self.orders

	# 委託歷史紀錄
	def tradex_q_orders_history(self, start_date_str=None, end_date_str=None):
		DBG_TR_LN(DBG_TXT_ENTER)

		def orders_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'交易日期':<7} {'可取消':<4} {'買/賣':<4} {'股票代碼':<5} {'委託股數':<5} {'成交股數':<5} {'取消股數':<5} {'委託價格':<5} {'成交均價':<5} {'預約狀態':<5} {'錯誤碼':<6} {'委託書編號':<7}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				c_date_str = self.tradex_field_c_date(item)

				celable = self.tradex_field_celable(item)
				celable_str = f"{celable}"

				buy_sell_str = self.tradex_field_buy_sell(item)

				stk_no_str = self.tradex_field_stk_no(item)

				qty_sign = "+" if buy_sell_str == "買" else "-" if buy_sell_str == "賣" else ""
				qty_str = f"{qty_sign}{self.tradex_field_quantity(item)}"
				#qty_str = self.tradex_field_quantity(item)

				mat_qty_str = self.tradex_field_mat_qty(item)

				cel_qty_str = self.tradex_field_cel_qty(item)

				od_price_str = self.tradex_field_od_price(item)

				avg_price_str = self.tradex_field_avg_price(item)

				ord_status_str = self.tradex_field_pre_order(item)

				err_code = self.tradex_field_err_code(item)

				ord_no = self.tradex_field_ord_no(item)
				ord_no_str = f"{ord_no}"

				msg += f"{i:>3} - {c_date_str:<11} {celable_str:<7} {buy_sell_str:<5} {stk_no_str:<9} {qty_str:<9} {mat_qty_str:<9} {cel_qty_str:<9} {od_price_str:<9} {avg_price_str:<9} {ord_status_str:<6} {err_code:<9} {ord_no_str:<12}{comma}"
			msg += "\n\n]"
			return msg

		if end_date_str is None:
			end_date = date.today() - timedelta(days=1)
			end_date_str = end_date.strftime("%Y-%m-%d")

		if start_date_str is None:
			start_date = date.today() - timedelta(days=2)
			start_date_str = start_date.strftime("%Y-%m-%d")

		DBG_IF_LN(f"( {start_date_str} ~ {end_date_str} )")
		if ( self.DATE_HYPHEN == 1):
			start_date_str = start_date_str.replace("-", "")
			end_date_str = end_date_str.replace("-", "")

		self.orders_history = self.trade_sdk.get_order_results_by_date(start_date_str, end_date_str)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				JSON_IF_FORMAT(self.orders_history)
			else:
				JSON_IF_FORMAT(self.orders_history, jstyle=JSTYLE.ARRAY, filter_cb=orders_filter_cb)

		return self.orders_history

	# 成交明細
	# query_range: 0d|3d|1m|3m
	def tradex_q_transactions(self, query_range="0d"):
		DBG_TR_LN(DBG_TXT_ENTER)

		def transactions_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'成交日期':<7} {'買/賣':<4} {'股票代碼':<5} {'成交股數':<5} {'成交均價 ':<5} {'股票名稱'}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				c_date_str = self.tradex_field_c_date(item)

				buy_sell_str = self.tradex_field_buy_sell(item)

				stk_no_str = self.tradex_field_stk_no(item)

				qty_sign = "+" if buy_sell_str == "買" else "-" if buy_sell_str == "賣" else ""
				qty_str = f"{qty_sign}{self.tradex_field_mat_qty(item)}"

				price_str = self.tradex_field_avg_price(item)

				stk_name_str = self.tradex_field_stk_name(item)

				msg += f"{i:>3} - {c_date_str:<11} {buy_sell_str:<5} {stk_no_str:<9} {qty_str:<9} {price_str:<9} {stk_name_str}{comma}"
			msg += "\n\n]"
			return msg

		DBG_IF_LN(f"(query_range: {query_range})")

		if ( self.DATE_HYPHEN == 1):
			start_date_str = start_date_str.replace("-", "")
			end_date_str = end_date_str.replace("-", "")

		self.transactions = self.trade_sdk.get_transactions(query_range)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				JSON_IF_FORMAT(self.transactions, jstyle=JSTYLE.ARRAY)
			else:
				JSON_IF_FORMAT(self.transactions, jstyle=JSTYLE.ARRAY, filter_cb=transactions_filter_cb)

		return self.transactions

	# 成交明細（依指定日期）
	def tradex_q_transactions_history(self, start_date_str=None, end_date_str=None):
		DBG_TR_LN(DBG_TXT_ENTER)

		def transactions_history_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'成交日期':<7} {'買/賣':<4} {'股票代碼':<5} {'成交股數':<5} {'成交均價 ':<5} {'股票名稱'}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				c_date_str = self.tradex_field_c_date(item)

				buy_sell_str = self.tradex_field_buy_sell(item)

				stk_no_str = self.tradex_field_stk_no(item)

				qty_sign = "+" if buy_sell_str == "買" else "-" if buy_sell_str == "賣" else ""
				qty_str = f"{qty_sign}{self.tradex_field_mat_qty(item)}"

				price_str = self.tradex_field_avg_price(item)

				stk_name_str = self.tradex_field_stk_name(item)

				msg += f"{i:>3} - {c_date_str:<11} {buy_sell_str:<5} {stk_no_str:<9} {qty_str:<9} {price_str:<9} {stk_name_str}{comma}"
			msg += "\n\n]"
			return msg

		if end_date_str is None:
			end_date = date.today() - timedelta(days=1)
			end_date_str = end_date.strftime("%Y-%m-%d")

		if start_date_str is None:
			start_date = date.today() - timedelta(days=2)
			start_date_str = start_date.strftime("%Y-%m-%d")

		DBG_IF_LN(f"( {start_date_str} ~ {end_date_str} )")

		if ( self.DATE_HYPHEN == 1):
			start_date_str = start_date_str.replace("-", "")
			end_date_str = end_date_str.replace("-", "")

		self.transactions_history = self.trade_sdk.get_transactions_by_date(start_date_str, end_date_str)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				JSON_IF_FORMAT(self.transactions_history, jstyle=JSTYLE.ARRAY)
			else:
				JSON_IF_FORMAT(self.transactions_history, jstyle=JSTYLE.ARRAY, filter_cb=transactions_history_filter_cb)

		return self.transactions_history

	# 交割款
	def tradex_q_settlements(self, range="3d"):
		DBG_TR_LN(DBG_TXT_ENTER)

		def settlements_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'交易日期':<8} {'交割日期':<8} {'交割款':<7}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				o_date_str = self.tradex_field_o_date(item)

				s_date_str = self.tradex_field_s_date(item)

				settlement_price_str = self.tradex_field_settlement_price(item)

				msg += f"{i:>3} - {o_date_str:<12} {s_date_str:<12} {settlement_price_str:<10}{comma}"
			msg += "\n\n]"
			return msg

		self.settlements = self.trade_sdk.get_settlements()
		if ( self.verbose == True ):
			if ( self.verbose == True ):
				JSON_IF_FORMAT(self.settlements, jstyle=JSTYLE.ARRAY, filter_cb=settlements_filter_cb)
			else:
				JSON_IF_FORMAT(self.settlements)

		return self.settlements

	# 刷單訊息
	def tradex_o_delete_response(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.verbose == True ) and ( self.last_delete_response is not None ):
			JSON_IF_FORMAT(self.last_delete_response)

		return self.last_delete_response

	# 減少委託單量
	def tradex_o_delete_qty(self, order_result, qty_share):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.test_only == False ):
			self.last_delete_response = self.trade_sdk.cancel_order(order_result, qty_share)
		else:
			DBG_WN_LN("測試模式，未執行交易 !")

		return self.tradex_o_delete_response()

	# 刪除單筆委託
	def tradex_o_delete(self, order_result):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.test_only == False ):
			self.last_delete_response = self.trade_sdk.cancel_order(order_result)
		else:
			DBG_WN_LN("測試模式，未執行交易 !")

		return self.tradex_o_delete_response()

	# 交易訊息
	def tradex_o_response(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.verbose == True ) and ( self.last_order_response is not None ):
			JSON_IF_FORMAT(self.last_order_response)

		return self.last_order_response

	#Action
	#  Buy	"B"	買
	#  Sell	"S"	賣
	#APCode
	#  Common	"1"	整股, 張, 1 ~ 499
	#  AfterMarket	"2"	盤後定價, 張, 1 ~ 499
	#  Odd	"3"	盤後零股, 股, 1 ~ 999
	#  Emg	"4"	興櫃, 股, 1 ~ 999, 1000 ~ 499000 (超過 1000 後，最小升降單位為 1000)
	#  IntradayOdd	"5"	盤中零股, 股, 1 ~ 999
	# PriceFlag
	#  Limit	"0"	限價
	#  Flat	"1"	平盤
	#  LimitDown	"2"	跌停
	#  LimitUp	"3"	漲停
	#  Market	"4"	市價
	# BSFlag
	#  ROD	"R"	當日委託有效單
	#  FOK	"F"	立即全部成交否則取消
	#  IOC	"I"	立即成交否則取消
	# Trade
	#  Cash	"0"	現股
	#  Margin	"3"	融資
	#  Short	"4"	融券
	#  DayTrading	"9"	信用當沖（僅適用於帳務）
	#  DayTradingSell	"A"	現股當沖賣
	def tradex_o_helper(self, stock_no=None, price=None, quantity=0, buy_sell=ACTION_BUY, ap_code=MARKETTYPE_COMMON):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.__is_login == True ) and ( stock_no is not None ):
			order_args = {
				"stock_no": stock_no,
				"quantity": quantity,
				"buy_sell": buy_sell,
				"ap_code": ap_code,
				"price_flag": self.PRICEFLAG_LIMIT,
				"bs_flag": self.BSFLAG_ROD,
				"trade": self.TRADE_CASH,
			}

			if not price is None:
				order_args["price"] = price

			DBG_DB_LN(f"(order_args: {order_args})")

			self.last_order = OrderObject(**order_args)

			if ( self.test_only == False ):
				self.last_order_response = self.trade_sdk.place_order( self.last_order )
			else:
				DBG_WN_LN("測試模式，未執行交易 !")
		else:
			DBG_ER_LN("請先登入 !!!")

		return self.tradex_o_response()

	# 整張買進
	def tradex_o_buy(self, stock_no, price, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, price=price, quantity=quantity, buy_sell=self.ACTION_BUY, ap_code=self.MARKETTYPE_COMMON)

	# 整張買進-盤後
	def tradex_o_buy_after(self, stock_no, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, quantity=quantity, buy_sell=self.ACTION_BUY, ap_code=self.MARKETTYPE_AFTERMARKET)

	# 零股買進
	def tradex_o_buy_odd(self, stock_no, price, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, price=price, quantity=quantity, buy_sell=self.ACTION_BUY, ap_code=self.MARKETTYPE_INTRADAYODD)

	# 零股買進-盤後
	def tradex_o_buy_odd_after(self, stock_no, price, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, price=price, quantity=quantity, buy_sell=self.ACTION_BUY, ap_code=self.MARKETTYPE_ODD)

	# 整張賣出
	def tradex_o_sell(self, stock_no, price, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, price=price, quantity=quantity, buy_sell=self.ACTION_SELL, ap_code=self.MARKETTYPE_COMMON)

	# 整張賣出-盤後
	def tradex_o_sell_after(self, stock_no, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, quantity=quantity, buy_sell=self.ACTION_SELL, ap_code=self.MARKETTYPE_AFTERMARKET)

	# 零股賣出
	def tradex_o_sell_odd(self, stock_no, price, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, price=price, quantity=quantity, buy_sell=self.ACTION_SELL, ap_code=self.MARKETTYPE_INTRADAYODD)

	# 零股賣出-盤後
	def tradex_o_buy_sell_after(self, stock_no, quantity):
		DBG_TR_LN(DBG_TXT_ENTER)
		return self.tradex_o_helper(stock_no, quantity=quantity, buy_sell=self.ACTION_SELL, ap_code=self.MARKETTYPE_ODD)

	def tradex_o_commit(self, action, stock_no, price, quantity, market):
		DBG_TR_LN(DBG_TXT_ENTER)
		quantity_lots, quantity_shares = divmod(int(quantity), 1000)

		# 第 5 層
		print("\n========== 交易內容 ==========")
		print(f"買賣：{'買股' if action == 'b' else '賣股'}")
		print(f"代碼：{stock_no}")
		print(f"價格：{price}")
		if quantity_lots > 0 and quantity_shares > 0:
			print(f"股數：{quantity_lots} 張 {quantity_shares} 股")
		elif quantity_lots > 0:
			print(f"股數：{quantity_lots} 張")
		else:
			print(f"股數：{quantity_shares} 股")
		print(f"時段：{'盤中' if market == 'i' else '盤後'}")
		tax = (1+0.001425) if action == 'b' else (1-0.001425-0.003)
		total = float(price)* int(quantity)*tax
		print(f"預估價金：{total:,.2f}")
		print("==============================")

		# 是否繼續
		answer = input("是否繼續執行？[y/n]：").strip().lower()

		match answer:
			case 'y':
				order = {
					"action": action,
					"market": market
				}
				match order:
					case {"action": 'b', "market": 'i'}:
							if quantity_lots > 0:
								self.tradex_o_buy(stock_no, price, quantity_lots*self.QUANTITY_LOTS_UNIT)
							if quantity_shares > 0:
								self.tradex_o_buy_odd(stock_no, price, quantity_shares)

					case {"action": 'b', "market": 'a'}:
							if quantity_lots > 0:
								self.tradex_o_buy_after(stock_no, quantity_lots*self.QUANTITY_LOTS_UNIT)
							if quantity_shares > 0:
								self.tradex_o_buy_odd_after(stock_no, price, quantity_shares)

					case {"action": 's', "market": 'i'}:
							if quantity_lots > 0:
								self.tradex_o_sell(stock_no, price, quantity_lots*self.QUANTITY_LOTS_UNIT)
							if quantity_shares > 0:
								self.tradex_o_sell_odd(stock_no, price, quantity_shares)

					case {"action": 's', "market": 'a'}:
							if quantity_lots > 0:
								self.tradex_o_sell_after(stock_no, quantity_lots*self.QUANTITY_LOTS_UNIT)
							if quantity_shares > 0:
								self.tradex_o_sell_odd_after(stock_no, price, quantity_shares)

					case _:
						DBG_IF_LN("輸入錯誤 !!!")

			case _:
				DBG_IF_LN("取消交易 !")


	#**************************************************
	# 查詢
	#**************************************************
	# 交易額度及權限
	def tradex_q_tradelimit(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.tradelimit = self.trade_sdk.get_trade_status()
		if ( self.verbose == True ):
			JSON_IF_FORMAT(self.tradelimit)

		return self.tradelimit

	# 銀行餘額
	def tradex_q_balance(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.balance = self.trade_sdk.get_balance()
		if ( self.verbose == True ):
			JSON_IF_FORMAT(self.balance)

		return self.balance

	# 庫存明細
	def tradex_q_inventories(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		def inventories_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'股票代碼':<6} {'昨餘額股數':<7} {'今買股數':<6} {'今賣股數':<6} {'成交均價':<6} {'即時價格':<6} {'市場別':<6} {'股票名稱'}\n"
			for i, item in enumerate(datas):
				comma = "\n" if i < len(datas) - 1 else ""

				stk_no_str = self.tradex_field_stk_no(item)

				qty_l_str = self.tradex_field_qty_l(item)

				qty_bm_str = f"+{self.tradex_field_qty_bm(item)}"

				qty_sm_str = f"-{self.tradex_field_qty_sm(item)}"

				price_avg_str = self.tradex_field_avg_price(item)

				price_now_str = self.tradex_field_price_now(item)

				s_type_str = self.tradex_field_s_type(item)

				stk_name_str = self.tradex_field_stk_name(item)

				msg += f"{i:>3} - {stk_no_str:<10} {qty_l_str:<12} {qty_bm_str:<10} {qty_sm_str:<10} {price_avg_str:<10} {price_now_str:<10} {s_type_str:<7} {stk_name_str}{comma}"
			msg += "\n\n]"
			return msg

		self.inventories = self.trade_sdk.get_inventories()
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				JSON_IF_FORMAT(self.inventories, jstyle=JSTYLE.ARRAY)
			else:
				JSON_IF_FORMAT(self.inventories, jstyle=JSTYLE.ARRAY, filter_cb=inventories_filter_cb)

		return self.inventories


	#**************************************************
	# 帳號
	#**************************************************
	def tradex_config_validate(self, config):
		DBG_TR_LN(DBG_TXT_ENTER)

	# 讀取設定檔
	def tradex_config(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.config = ConfigParser()
		self.config.read(self.config_ini)

		self.tradex_config_validate(self.config)

	# cat ~/.local/share/python_keyring/keyring_pass.cfg
	def tradex_remove_credentials(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		user_account = self.__AID

		# Delete both passwords from the keyring
		delete_password(TRADE_SDK_ACCOUNT_KEY, user_account)
		delete_password(TRADE_SDK_CERT_KEY, user_account)

	# cat ~/.local/share/python_keyring/keyring_pass.cfg
	def tradex_load_credentials(self):
		DBG_TR_LN(DBG_TXT_ENTER)

	# 登出
	def tradex_logout(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		#self.tradex_remove_credentials()

		self.trade_sdk.logout()

	# 登入
	def tradex_login(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.trade_sdk.login()

		self.__is_login = True

	# 重設密碼
	def tradex_password(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.trade_sdk.reset_password()

		return self.password_response

	# 憑證資訊
	def tradex_q_certinfo(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.certinfo = self.trade_sdk.certinfo()
		if ( self.verbose == True ):
			JSON_IF_FORMAT(self.certinfo)

		return self.certinfo

	# 金鑰資訊
	def tradex_q_keyinfo(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.keyinfo = self.trade_sdk.get_key_info()
		if ( self.verbose == True ):
			JSON_IF_FORMAT(self.keyinfo)

		return self.keyinfo


	#**************************************************
	# websocket
	#**************************************************
	def threadx_websocket_open(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		# 註冊當 websocket 發生錯誤時的 callback
		@self.trade_sdk.on('error')
		def on_error(err):
			DBG_ER_LN(f"{err}")

		# 註冊接收委託回報的 callback
		@self.trade_sdk.on('order')
		def on_order(data):
			DBG_IF_LN(f"{data}")

		# 註冊接收成交回報的 callback
		@self.trade_sdk.on('dealt')
		def on_dealt(data):
			DBG_WN_LN(f"{data}")

		# 註冊關閉回報的 callback
		@self.trade_sdk.on('close')
		def on_close(ws, close_status_code, close_msg):
			DBG_WN_LN(f"(close_status_code: {close_status_code}, close_msg: {close_msg})")

		self.trade_sdk.connect_websocket()

	def threadx_websocket_close(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.trade_sdk.close_websocket()


	#**************************************************
	# thread
	#**************************************************
	def threadx_handler(self):
		#DBG_IF_LN(DBG_TXT_ENTER)
		self.tradex_login()

		self.threadx_set_inloop(1)
		self.threadx_websocket_open()
		while ( self.is_quit == 0 ):
			self.threadx_sleep(1)
		self.threadx_set_inloop(0)
		DBG_WN_LN(DBG_TXT_BYE_BYE)

	def tradex_register_cb(self):
		DBG_TR_LN(DBG_TXT_ENTER)

	def tradex_create(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.tradex_config()
		self.credentials = self.tradex_load_credentials()

		self.trade_sdk = EsunSDK(self.config)


	#**************************************************
	# ctx api
	#**************************************************
	def tradex_intact_json_get(self):
		return self.intact_json

	def tradex_intact_json_toggle(self):
		self.intact_json = not self.intact_json

	def release(self):
		if ( self.is_quit == 0 ):
			self.is_quit = 1
			if ( self.threadx_inloop() == 1 ):
				self.threadx_wakeup()
			self.threadx_websocket_close()
			#self.tradex_logout()
			self.threadx_join()
			DBG_DB_LN(DBG_TXT_DONE)

	def ctx_init(self):
		DBG_DB_LN(DBG_TXT_ENTER)

		self.orders = None
		self.transactions = None
		self.transactions_history = None

		self.settlements = None

		self.last_delete_response = None
		self.last_order_response = None

		self.last_order = None

		self.tradelimit = None
		self.balance = None
		self.inventories = None

		self.config = None
		self.__AID = None
		self.__certPath = None
		self.__APISecret = None
		self.trade_sdk = None
		self.__is_login = False
		self.__account = None

		self.password_response = None

		self.certinfo = None
		self.keyinfo = None

	def __init__(self, **kwargs):
		if ( isPYTHON(PYTHON_V3) ):
			super().__init__(**kwargs)
		else:
			super(tradex_esun_ctx, self).__init__(**kwargs)

		DBG_TR_LN(DBG_TXT_ENTER)
		self._kwargs = kwargs
		self.ctx_init()

	def parse_args(self, args):
		DBG_TR_LN(DBG_TXT_ENTER)
		self._args = args
		self.verbose = args["verbose"]
		self.config_ini = args["config_ini"]
		self.test_only = args["test_only"]
		self.intact_json = args["intact_json"]

	def start(self, args={}):
		DBG_TR_LN(DBG_TXT_START)
		self.parse_args(args)
		self.tradex_create()
		self.tradex_register_cb()

		self.threadx_init()

