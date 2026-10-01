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
	# 富邦SDK
	#**************************************************
from configparser import ConfigParser

from getpass import getpass
from keyring import get_password, set_password, set_keyring, delete_password
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from hashlib import md5

from fubon_neo.sdk import FubonSDK, Order as OrderObject
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

#import os, sys, errno, getopt, signal, time, io
#from time import sleep
from pythonP9.pythonP9 import *
from pythonP9.threadx_api import *

TRADE_SDK_ACCOUNT_KEY = "fubon_trade_sdk:account"
TRADE_SDK_CERT_KEY = "fubon_trade_sdk:cert"

class fubonp9_ctx(pythonP9, threadx_ctx):
	QUANTITY_LOTS_UNIT = 1000

	ACTION_BUY = BSAction.Buy
	ACTION_SELL = BSAction.Sell

	MARKETTYPE_COMMON = MarketType.Common
	MARKETTYPE_AFTERMARKET = MarketType.Fixing
	MARKETTYPE_INTRADAYODD = MarketType.IntradayOdd
	MARKETTYPE_ODD = MarketType.Odd

	PRICEFLAG_LIMIT = PriceType.Limit
	PRICEFLAG_FLAT = PriceType.Reference
	PRICEFLAG_LIMITDOWN = PriceType.LimitDown
	PRICEFLAG_LIMITUP = PriceType.LimitUp
	PRICEFLAG_MARKET = PriceType.Market

	BSFLAG_ROD = TimeInForce.ROD
	BSFLAG_FOK = TimeInForce.FOK
	BSFLAG_IOC = TimeInForce.IOC

	TRADE_CASH = OrderType.Stock
	TRADE_MARGIN = OrderType.Margin
	TRADE_SHORT = OrderType.Short
	TRADE_DAYTRADINGSELL = OrderType.DayTrade
	TRADE_SBL = OrderType.SBL

	DATE_HYPHEN = 1

	#**************************************************
	# Field Value
	#**************************************************
	# 可取消狀態
	def tradex_field_celable(self, item):
		match item.status:
			case 0: # 預約單
				celable = f"yes" if item.after_qty > 0 else f"no"
			case 10: # 委託成功
				celable = f"yes" if item.after_qty > 0 else f"no"
			case 30: # 未成交刪單成功
				celable = f"no"
			case 40: # 部分成交，剩餘取消
				celable = f"no"
			case 90: # 失敗
				celable = f"no"
			case _:
				celable = f"no"
		return celable

	# 委託書編號
	def tradex_field_ord_no(self, item):
		if item.order_no is not None:
			ord_no = f"{item.order_no}"
		else:
			ord_no = f"{item.seq_no}"
		return ord_no

	# 預約狀態
	def tradex_field_pre_order(self, item):
		if hasattr(item, 'is_pre_order'):
			if item.is_pre_order == True:
				return f"預約單"
			else:
				return f"盤中單"
		else:
			return f"ｘｘｘ"

	# 股票代號
	def tradex_field_stk_no(self, item):
		return f"{item.stock_no}"

	# 股票名稱
	def tradex_field_stk_name(self, item):
		if hasattr(item, 'stk_na'):
			return f"{item.stk_na}"
		else:
			return f"xxx"

	# 買賣別
	def tradex_field_buy_sell(self, item):
		if item.buy_sell == self.ACTION_BUY:
			buy_sell = "買"
		else:
			buy_sell = "賣"
		return buy_sell

		# 原始委託數量
	def tradex_field_quantity(self, item):
		if hasattr(item, 'quantity'):
			return f"{item.quantity:,}"
		else:
			return f"xxx"

	# 交割日
	def tradex_field_s_date(self, item):
		if hasattr(item, 'settlement_date'):
			return f"{item.settlement_date}"
		else:
			return f"xxx"

	# 成交日
	def tradex_field_o_date(self, item):
		if hasattr(item, 'date'):
			return f"{item.date}"
		else:
			return f"xxx"

	# 日期
	def tradex_field_c_date(self, item):
		if hasattr(item, 'date'):
			return f"{item.date}"
		else:
			return f"xxx"

	# 已成交數量
	def tradex_field_mat_qty(self, item):
		if hasattr(item, 'filled_qty'):
			return f"{item.filled_qty:,}" if item.filled_qty is not None else "0"
		else:
			return f"xxx"

	# 取消數量
	def tradex_field_cel_qty(self, item):
		if hasattr(item, 'quantity') and hasattr(item, 'after_qty'):
			return f"{item.quantity - item.after_qty:,}"
		else:
			return f"xxx"

	# 昨餘額股數
	def tradex_field_qty_l(self, item):
		if hasattr(item, 'lastday_qty') and hasattr(item, 'odd') and hasattr(item.odd, 'lastday_qty'):
			return f"{item.lastday_qty + item.odd.lastday_qty:,}"
		else:
			return f"xxx"

	# 委買成交股數
	def tradex_field_qty_bm(self, item):
		if hasattr(item, 'buy_filled_qty') and hasattr(item, 'odd') and hasattr(item.odd, 'buy_filled_qty'):
			return f"{item.buy_filled_qty + item.odd.buy_filled_qty:,}"
		else:
			return f"xxx"

	# 賣成交股數
	def tradex_field_qty_sm(self, item):
		if hasattr(item, 'sell_filled_qty') and hasattr(item, 'odd') and hasattr(item.odd, 'sell_filled_qty'):
			return f"{item.sell_filled_qty + item.odd.sell_filled_qty:,}"
		else:
			return f"xxx"

	# 委託價格
	def tradex_field_od_price(self, item):
		if hasattr(item, 'price'):
			return f"{item.price:,}"
		else:
			return f"xxx"

	# 成交均價
	def tradex_field_avg_price(self, item):
		if hasattr(item, 'price_avg'):
			return f"{item.price_avg:,}"
		elif hasattr(item, 'filled_avg_price'):
			return f"{item.filled_avg_price:,}"
		else:
			return f"xxx"

	# 即時價格
	def tradex_field_price_now(self, item):
		if hasattr(item, 'price_now'):
			return f"{item.price_now:,}"
		else:
			return f"xxx"

	# 交割款
	def tradex_field_settlement_price(self, item):
		if hasattr(item, 'total_settlement_amount'):
			return f"{item.total_settlement_amount:,}" if item.total_settlement_amount is not None else "None"
		else:
			return f"xxx"

	# 市場別
	def tradex_field_s_type(self, item):
		if hasattr(item, 's_type'):
			return f"{item.s_type}"
		else:
			return f"ｘｘｘ"

	# 錯誤碼
	def tradex_field_err_code(self, item):
		if hasattr(item, 'status'):
			return f"{item.status}"
		else:
			return f"xxx"


	#**************************************************
	# 交易下單
	#**************************************************
	def tradex_orders_get(self):
		return self.orders.data

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

		self.orders = self.trade_sdk.stock.get_order_results(self.__account)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(orders: {self.orders})")
			else:
				msg = orders_filter_cb( self.orders.data )
				DBG_IF_LN(f"(orders: {msg})")

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

		self.orders_history = self.trade_sdk.stock.order_history(self.__account, start_date_str, end_date_str)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(orders_history: {self.orders_history})")
			else:
				msg = orders_filter_cb(self.orders_history.data)
				DBG_IF_LN(f"(orders_history: {msg})")

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

		start_date = date.today()
		start_date_str = start_date.strftime("%Y%m%d")
		match query_range:
			case '3m':
				end_date = date.today()
				start_date = end_date - relativedelta(months=3)

			case '1m':
				end_date = date.today()
				start_date = end_date - relativedelta(months=1)

			case '3d':
				end_date = date.today()
				start_date = end_date - timedelta(days=3)

			case '0d':
				start_date = date.today()
				end_date = start_date

			case _:
				start_date = date.today()
				end_date = start_date

		start_date_str = start_date.strftime("%Y-%m-%d")
		end_date_str = end_date.strftime("%Y-%m-%d")

		DBG_IF_LN(f"( {start_date_str} ~ {end_date_str} )")

		if ( self.DATE_HYPHEN == 1):
			start_date_str = start_date_str.replace("-", "")
			end_date_str = end_date_str.replace("-", "")

		self.transactions = self.trade_sdk.stock.filled_history(self.__account, start_date_str, end_date_str)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(transactions: {self.transactions})")
			else:
				msg = transactions_filter_cb(self.transactions.data)
				DBG_IF_LN(f"(transactions: {msg})")

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

		self.transactions_history = self.trade_sdk.stock.filled_history(self.__account, start_date_str, end_date_str)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(transactions_history: {self.transactions_history})")
			else:
				msg = transactions_history_filter_cb(self.transactions_history.data)
				DBG_IF_LN(f"(transactions_history: {msg})")

		return self.transactions_history

	# 交割款
	def tradex_q_settlements(self, range="3d"):
		DBG_TR_LN(DBG_TXT_ENTER)

		def settlements_filter_cb(datas):
			#DBG_DB_LN(DBG_TXT_ENTER)
			msg = "[\n\n"
			msg += f"{'idx':>3} - {'交易日期':<8} {'交割日期':<8} {'交割款':<7}\n"
			i = 0
			for item in datas:
				comma = "\n" if i < len(datas) - 1 else ""

				o_date_str = self.tradex_field_o_date(item)

				s_date_str = self.tradex_field_s_date(item)

				settlement_price_str = self.tradex_field_settlement_price(item)

				msg += f"{i:>3} - {o_date_str:<12} {s_date_str:<12} {settlement_price_str:<10}{comma}"
				i+=1
			msg += "\n\n]"
			return msg

		self.settlements = self.trade_sdk.accounting.query_settlement(self.__account,range)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(settlements: {self.settlements})")
			else:
				details = self.settlements.data.details
				msg = settlements_filter_cb(details)
				DBG_IF_LN(f"(settlements: {msg})")

		return self.settlements

	# 刷單訊息
	def tradex_o_delete_response(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.verbose == True ) and ( self.last_delete_response is not None ):
			DBG_IF_LN(f"(last_delete_response: {self.last_delete_response})")

		return self.last_delete_response

	# 減少委託單量
	def tradex_o_delete_qty(self, order_result, qty_share):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.test_only == False ):
			modify_qty_obj = self.trade_sdk.stock.make_modify_quantity_obj(order_result, 1000)
			self.last_delete_response = self.trade_sdk.stock.cancel_order(self.__account, modify_qty_obj)
		else:
			DBG_WN_LN("測試模式，未執行交易 !")

		return self.tradex_o_delete_response()

	# 刪除單筆委託
	def tradex_o_delete(self, order_result):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.test_only == False ):
			self.last_delete_response = self.trade_sdk.stock.cancel_order(self.__account, order_result)
		else:
			DBG_WN_LN("測試模式，未執行交易 !")

		return self.tradex_o_delete_response()

	# 交易訊息
	def tradex_o_response(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.verbose == True ) and ( self.last_order_response is not None ):
			DBG_IF_LN(f"(last_order_response: {self.last_order_response})")

		return self.last_order_response

	#BSAction
	#  Buy	"B"	買
	#  Sell	"S"	賣
	#MarketType
	#  Common	"?"	整股, 千股, 1000 ~ 499000
	#  Fixing	"?"	盤後定價, 千股, 1000 ~ 499000
	#  Odd	"?"	盤後零股, 股, 1 ~ 999
	#  Emg	"?"	興櫃, 千股, 1000 ~ 499000 (超過 1000 後，最小升降單位為 1000)
	#  IntradayOdd	"?"	盤中零股, 股, 1 ~ 999
	#  EmgOdd	"?"	興櫃零股, 股, 1 ~ 999
	# PriceType
	#  Limit	"?"	限價
	#  LimitUp	"?"	漲停
	#  LimitDown	"?"	跌停
	#  Market	"?"	市價
	#  Reference	"?"	參考價 (定盤時為定盤價)
	# TimeInForce
	#  ROD	"?"	當日有效(Rest of Day)
	#  FOK	"?"	全部成交否則取消(Fill-or-Kill)
	#  IOC	"?"	立即成交否則取消(Immediate-or-Cancel)
	# OrderType
	#  Stock	"?"	現股
	#  Margin	"?"	融資
	#  Short	"?"	融券
	#  DayTrade	"?"	現沖先賣
	#  SBL	"?"	借券
	def tradex_o_helper(self, stock_no=None, price=None, quantity=0, buy_sell=ACTION_BUY, ap_code=MARKETTYPE_COMMON):
		DBG_TR_LN(DBG_TXT_ENTER)

		if ( self.__is_login == True ) and ( stock_no is not None ):
			order_args = {
				"symbol": stock_no,
				"quantity": quantity,
				"buy_sell": buy_sell,
				"market_type": ap_code,
				"price_type": self.PRICEFLAG_LIMIT,
				"time_in_force": self.BSFLAG_ROD,
				"order_type": self.TRADE_CASH,
			}

			if not price is None:
				order_args["price"] = f"{price:.2f}"

			DBG_DB_LN(f"(order_args: {order_args})")

			self.last_order = OrderObject(**order_args)

			if ( self.test_only == False ):
				self.last_order_response = self.trade_sdk.stock.place_order( self.__account, self.last_order )
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

		self.tradelimit = f"未提供相關 API !!!"
		if ( self.verbose == True ):
			DBG_IF_LN(f"(tradelimit: {self.tradelimit})")

		return self.tradelimit

	# 銀行餘額
	def tradex_q_balance(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.balance = self.trade_sdk.accounting.bank_remain(self.__account)
		if ( self.verbose == True ):
			DBG_IF_LN(f"(balance: {self.balance})")

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

		self.inventories = self.trade_sdk.accounting.inventories(self.__account)
		if ( self.verbose == True ):
			if ( self.intact_json == True ):
				DBG_IF_LN(f"(inventories: {self.inventories})")
			else:
				msg = inventories_filter_cb(self.inventories.data)
				DBG_IF_LN(f"(inventories: {msg})")

		return self.inventories


	#**************************************************
	# 帳號
	#**************************************************
	def tradex_config_validate(self, config):
		DBG_TR_LN(DBG_TXT_ENTER)

		if not ( config.has_section("Cert")
			and config.has_section("Api")
			and config.has_section("User") ):
				raise TypeError("please fill in config file")

		if (not config["Cert"].get("Path")) or config["Cert"]["Path"].find(	".p12") == -1:
			raise TypeError("please give correct Cert Path")
		self.__certPath = self.config["Cert"]["Path"]

		#if not config["Api"].get("Secret"):
		#	raise TypeError("please give correct Api Secret")
		#self.__APISecret = self.config["Api"]["Secret"]

		if not config["User"].get("Account"):
			raise TypeError("please give correct User Account")
		self.__AID = self.config["User"]["Account"]

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

		user_account = self.__AID

		# Get existing passwords from keyring
		account_password = get_password(TRADE_SDK_ACCOUNT_KEY, user_account)
		cert_password = get_password(TRADE_SDK_CERT_KEY, user_account)

		# Prompt for missing passwords
		if not account_password:
			new_password = getpass("Enter account password: ")
			set_password(TRADE_SDK_ACCOUNT_KEY, user_account, new_password)
			account_password = new_password

		if not cert_password:
				new_cert_password = getpass("Enter cert password: ")
				set_password(TRADE_SDK_CERT_KEY, user_account, new_cert_password)
				cert_password = new_cert_password

		return {
				"account_password": account_password,
				"cert_password": cert_password
		}

	# 登出
	def tradex_logout(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.tradex_remove_credentials()

		self.trade_sdk.logout()

	# 登入
	def tradex_login(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		# 帳號&密碼 登入
		self.accounts = self.trade_sdk.login(self.__AID, self.credentials["account_password"], self.__certPath, self.credentials["cert_password"])
		# API Key 登入
		#self.accounts = self.trade_sdk.apikey_login(self.__AID, self.__APISecret, self.__certPath, self.credentials["cert_password"])

		if self.accounts.is_success == True:
			self.__is_login = True
			self.__account = self.accounts.data[0]

			DBG_TR_LN(f"(accounts: {self.accounts}, {type(self.accounts)})")
		else:
			DBG_ER_LN("登入失敗 !!!")

	# 重設密碼
	def tradex_password(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.password_response = f"未提供相關 API !!!"
		if ( self.verbose == True ):
			DBG_IF_LN(f"(password_response: {self.password_response})")

		return self.password_response

	# 憑證資訊
	def tradex_q_certinfo(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.certinfo = f"未提供相關 API !!!"
		if ( self.verbose == True ):
			DBG_IF_LN(f"(certinfo: {self.certinfo})")

		return self.certinfo

	# 金鑰資訊
	def tradex_q_keyinfo(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.keyinfo = f"未提供相關 API !!!"
		if ( self.verbose == True ):
			DBG_IF_LN(f"(keyinfo: {self.keyinfo})")

		return self.keyinfo


	#**************************************************
	# websocket
	#**************************************************
	def threadx_websocket_open(self):
		DBG_TR_LN(DBG_TXT_ENTER)

	def threadx_websocket_close(self):
		DBG_TR_LN(DBG_TXT_ENTER)


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
		# 訂閱委託回報
		def on_order(code, content):
			DBG_TR_LN(DBG_TXT_ENTER)
			DBG_IF_LN(f"(code: {code}, content: {content})")

		# 訂閱改價/改量/刪單回報
		def on_order_changed(code, content):
			DBG_TR_LN(DBG_TXT_ENTER)
			DBG_IF_LN(f"(code: {code}, content: {content})")

		# 訂閱成交回報
		def on_filled(code, content):
			DBG_TR_LN(DBG_TXT_ENTER)
			DBG_IF_LN(f"(code: {code}, content: {content})")

		# 訂閱事件通知
		def on_event(code, content):
			DBG_TR_LN(DBG_TXT_ENTER)
			DBG_IF_LN(f"(code: {code}, content: {content})")

		self.trade_sdk.set_on_order(on_order) 
		self.trade_sdk.set_on_order_changed(on_order_changed) 
		self.trade_sdk.set_on_filled(on_filled)
		self.trade_sdk.set_on_event(on_event) 

	def tradex_create(self):
		DBG_TR_LN(DBG_TXT_ENTER)

		self.tradex_config()
		self.credentials = self.tradex_load_credentials()

		self.trade_sdk = FubonSDK()


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
			super(tradex_fubon_ctx, self).__init__(**kwargs)

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

