#!/usr/bin/env python3
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

from tradeP9.tradeP9_fubon_api import *

appX_list = []
is_quit = 0
is_release = 0
argsX = {
	"securities_firm": 'Fubon'
	,"config_ini": '/work/certs/fubon/config.ini'
	,"verbose": True
	,"test_only": False
	,"intact_json":False
}

def app_quit_get():
	return is_quit

def app_quit_set(mode):
	global is_quit
	is_quit=mode

def app_menu_delete(tradex_mgr):
	while True:
		# 委託紀錄
		tradex_mgr.tradex_q_orders()

		orders = tradex_mgr.tradex_orders_get()
		total = len(orders)

		if (total > 0):
			msg = f"\n委託刪單- 請輸入編號 [0]~[{total-1}], [q] 離開："
			# 第 1 層
			action = input(msg).strip().lower()

			if action == 'q':
				#print("離開程式")
				break

			if action == '':
				break

			try:
				idx = int(action)
			except ValueError:
				print("編號格式錯誤，請重新輸入 !!!")
				continue

			if (idx <= (total-1)):
				item = orders[idx]
				order_result = item

				ord_no = tradex_mgr.tradex_field_ord_no(item)

				celable = tradex_mgr.tradex_field_celable(item)
				if ( celable == 'yes' ):
					#print(f"{item}")
					#print(f"{type(orders)}")

					# 是否繼續
					msg = f"委託單 [{idx}] {ord_no} 將被刪除，是否繼續執行？[y/n]："
					answer = input(msg).strip().lower()

					match answer:
						case 'y':
							tradex_mgr.tradex_o_delete(item)
						case _:
							print("取消交易 !")

					break
				else:
					print(f"委託單 [{idx}] {ord_no} 無法刪除，請重新輸入 !!!\n")
			else:
				print("編號格式錯誤，請重新輸入 !!!\n")
		else:
			print("查無委託單 !!!")
			break

def app_menu_order(tradex_mgr):
	while True:
		msg = f"\n交易下單-\n"
		msg+= f"  [b] 買股,\n"
		msg+= f"  [s] 賣股,\n"
		msg+= f"請輸入 [b] or [s], [q] 離開："

		# 第 1 層
		action = input(msg).strip().lower()

		if action == 'q':
			#print("離開程式")
			break

		if action == '':
			break

		if action not in ('b', 's'):
			print("輸入錯誤，請輸入 b 或 s !!!")
			continue

		# 第 2 層
		stock_no = input("請輸入股票代碼：").strip()

		if stock_no == '':
			continue

		# 第 3 層
		price = input("請輸入價格：").strip()

		if price == '':
			continue

		try:
			price = float(price)
		except ValueError:
			print("價格格式錯誤，請重新輸入 !!!")
			continue

		# 第 4 層
		quantity = input("請輸入股數：").strip()

		if quantity == '':
			continue

		# 第 5 層
		market = input("請選擇 [i] 盤中 或 [a] 盤後：").strip().lower()

		if market == '':
			continue

		if market not in ('i', 'a'):
			print("輸入錯誤，請輸入 i 或 a")
			continue

		tradex_mgr.tradex_o_commit(action, stock_no, price, quantity, market)

def app_menu_main(tradex_mgr):
	while True:
		msg = f"\n--------------- " + argsX_get(argsX, "securities_firm") + " 主選單 ---------------\n"
		msg+= f"  [1] 庫存明細,\n"
		msg+= f"  [2] 交易下單,\n"
		msg+= f"  [3] 委託紀錄, [4] 成交明細, [5] 委託刪單,\n"
		msg+= f"  [6] 交割款, [7] 銀行餘額, [8] 交易額度,\n"
		msg+= f"  [i] 資料切換 ({'Full' if tradex_mgr.tradex_intact_json_get()==True else 'Partial'}),\n"
		msg+= f"  [l] logout\n"
		msg+= f"請輸入編號 [1]~[8], [q] 離開："

		# 第 1 層
		action = input(msg).strip().lower()

		if action == 'q':
			#print("離開程式")
			break

		if action == '':
			continue

		match action:
			case '1':
				# 庫存明細
				tradex_mgr.tradex_q_inventories()

			case '2':
				# 交易下單
				app_menu_order(tradex_mgr)

			case '3':
				# 委託紀錄
				tradex_mgr.tradex_q_orders()
				#tradex_mgr.tradex_q_orders_history("2026-09-21", "2026-09-24")

			case '4':
				# 成交明細
				tradex_mgr.tradex_q_transactions(query_range="0d")
				#tradex_mgr.tradex_q_transactions_history("2026-09-01", "2026-09-24")

			case '5':
				# 委託刪單
				app_menu_delete(tradex_mgr)

			case '6':
				# 交割款
				tradex_mgr.tradex_q_settlements()

			case '7':
				# 銀行餘額
				tradex_mgr.tradex_q_balance()
				#print(f"(tradex_mgr.balance: {tradex_mgr.balance})\r")

			case '8':
				# 交易額度及權限
				tradex_mgr.tradex_q_tradelimit()

			case 'l':
				# 登出
				tradex_mgr.tradex_logout()

			case 'i':
				# 委託刪單
				tradex_mgr.tradex_intact_json_toggle()

			case _:
				continue

def app_demo(tradex_mgr):
	#**************************************************
	# 交易下單
	#**************************************************
	# 委託紀錄
	#tradex_mgr.tradex_q_orders()

	# 委託歷史紀錄
	# 預設前 2日的歷史紀錄
	#tradex_mgr.tradex_q_orders_history()
	# 查詢 2026-09-09 ~ 2026-09-10 的歷史紀錄
	#tradex_mgr.tradex_q_orders_history("2026-09-09", "2026-09-10")

	# 成交明細
	#tradex_mgr.tradex_q_transactions(query_range="0d")

	# 成交明細（依指定日期）
	# 查詢 2026-09-09 ~ 2026-09-10 的成交紀錄
	#tradex_mgr.tradex_q_transactions_history("2026-09-09", "2026-09-10")

	# 交割款
	#tradex_mgr.tradex_q_settlements()

	# 交易訊息
	#tradex_mgr.tradex_o_response()

	# 整張買進 0050, 109 元 * 1張
	#tradex_mgr.tradex_o_buy("0050", 109, 1)
	# 整張買進 00919, 32.34 元 * 1張
	#tradex_mgr.tradex_o_buy("00919", 32.34, 1)
	# 零股買進 00919, 32.32 元 * 837股
	#tradex_mgr.tradex_o_buy_odd("00919", 32.32, 837)

	#**************************************************
	# 查詢
	#**************************************************
	# 交易額度及權限
	#tradex_mgr.tradex_q_tradelimit()

	# 銀行餘額
	tradex_mgr.tradex_q_balance()
	#print(f"(tradex_mgr.balance: {tradex_mgr.balance})\r")

	# 庫存明細
	#tradex_mgr.tradex_q_inventories()


	#**************************************************
	# 帳號
	#**************************************************
	# 重設密碼
	#tradex_mgr.tradex_password()

	# 憑證資訊
	#tradex_mgr.tradex_q_certinfo()

	# 金鑰資訊
	#tradex_mgr.tradex_q_keyinfo()

def app_start():
	argsX_dump(argsX)

	tradex_mgr = tradeP9_fubon_ctx(dbg_lvl=DBG_LVL_INFO)
	tradex_mgr.start(argsX)

	app_watch(tradex_mgr)

	#app_demo(tradex_mgr)
	app_menu_main(tradex_mgr)

def app_watch(app_ctx):
	global appX_list

	appX_list.append( app_ctx )

def app_release():
	global appX_list
	global is_release

	if ( is_release == 0 ):
		is_release = 1
		DBG_DB_LN(DBG_TXT_ENTER)
		for x in appX_list:
			try:
				objname = DBG_NAME(x)
				if not x.release is None:
					DBG_DB_LN(f"call {objname}.release ..." )
					x.release() # No handlers could be found for logger "google.api_core.bidi"
			except Exception:
				pass
		DBG_DB_LN(DBG_TXT_DONE)

def app_stop():
	# dont block this function or print, signal_handler->app_stop
	if ( app_quit_get() == 0 ):
		app_quit_set(1)

		app_release()

def app_exit():
	app_stop()
	DBG_DB_LN(DBG_TXT_DONE)

def show_usage(argv):
	print(f"Usage: {argv[0]} <options...>")
	print("  -t, --test")
	print("         test only")
	print("  -i, --intact")
	print("         print full json")
	print("  -h, --help")
	print("  -d, --debug level")
	print("    0: critical, 1: errror, 2: warning, 3: info, 4: debug, 5: trace")
	app_exit()
	sys.exit(0)

def parse_arg(argv):
	try:
		opts,args = getopt.getopt(argv[1:], "tihd:", ["test", "intact", "help", "debug"])
	except getopt.GetoptError:
		show_usage(argv)

	#print (opts)
	#print (args)

	if (len(opts) > 0):
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				show_usage(argv)
			elif opt in ("-d", "--debug"):
				dbg_debug_helper( int(arg) )
			elif opt in ("-t", "--test"):
				argsX_set(argsX, "test_only", True)
			elif opt in ("-i", "--intact"):
				argsX_set(argsX, "intact_json", True)
			else:
				print (f"(opt: {opt})")
	#else:
	#	show_usage(argv)

def signal_handler(sig, frame):
	if sig in (signal.SIGINT, signal.SIGTERM):
		app_stop()
		return
	sys.exit(0)

def main(argv):
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	parse_arg(argv)

	app_start()

	app_exit()
	DBG_WN_LN(f"{DBG_TXT_BYE_BYE} (app_quit_get: {app_quit_get()})")

if __name__ == "__main__":
	main(sys.argv[0:])
