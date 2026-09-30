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

from stockx_backtesting_api import *

stock_no = '0050'           # 股票代碼

year_ago = 10
delta_days = 5

appX_list = []
is_quit = 0
is_release = 0
argsX = {
	"stock_no": stock_no
	,"year_ago": year_ago
	,"delta": delta_days
	,"buy_short": 1
	,"buy_medium": 3
	,"buy_long": 5
	,"history_folder": f"./stock"
	,"renew": False
	,"text": False
	,"verbose": False
}

def app_quit_get():
	return is_quit

def app_quit_set(mode):
	global is_quit
	is_quit=mode

def app_start():
	argsX_dump(argsX)

	stockx_backtesting_mgr = stockx_backtesting_ctx()
	app_watch(stockx_backtesting_mgr)

	stockx_backtesting_mgr.start( argsX )
	if ( argsX_get(argsX, "verbose") == True ) and (app_quit_get()==0):
		stockx_backtesting_mgr.history_display_on_screen()

	if (app_quit_get()==0):
		stockx_backtesting_mgr.history_save_to_csv()

	stockx_backtesting_mgr.buy_prices_helper()

	stockx_backtesting_mgr.buy_return_display_on_screen()

	if ( argsX_get(argsX, "text") == False ) and (app_quit_get()==0):
		stockx_backtesting_mgr.buy_return_plot_lines_on_screen()

	if ( argsX_get(argsX, "text") == False ) and (app_quit_get()==0):
		stockx_backtesting_mgr.buy_return_plot_bars_on_screen()

def app_watch(app_ctx):
	global appX_list

	appX_list.append( app_ctx )

def app_release():
	global appX_list
	global is_release

	if ( is_release == 0 ):
		is_release = 1
		DBG_DB_LN("{}".format(DBG_TXT_ENTER))
		for x in appX_list:
			try:
				objname = DBG_NAME(x)
				if not x.release is None:
					DBG_DB_LN("call {}.release ...".format( objname ) )
					x.release() # No handlers could be found for logger "google.api_core.bidi"
			except Exception:
				pass
		DBG_DB_LN("{}".format(DBG_TXT_DONE))

def app_stop():
	# dont block this function or print, signal_handler->app_stop
	if ( app_quit_get() == 0 ):
		app_quit_set(1)

		app_release()

def app_exit():
	app_stop()
	DBG_DB_LN("{}".format(DBG_TXT_DONE))

def show_usage(argv):
	print("Usage: {} <options...>".format(argv[0]) )
	print("  -h, --help")
	print("  -d, --debug level")
	print("  -s, --stock Stock symbol")
	print("  -y, --year N years ago")
	print("  -l, --delta N days ago")
	print("  -r, --renew")
	print("  -t, --text")
	print("  -v, --verbose")
	print("    0: critical, 1: errror, 2: warning, 3: info, 4: debug, 5: trace")
	app_exit()
	sys.exit(0)

def parse_arg(argv):
	try:
		opts,args = getopt.getopt(argv[1:], "hd:s:y:l:rtv", ["help", "debug", "stock", "year", "delta", "renew", "text", "verbose"])
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
			elif opt in ("-s", "--stock"):
				argsX_set(argsX, "stock_no", arg)
			elif opt in ("-y", "--year"):
				argsX_set(argsX, "year_ago", int(arg))
			elif opt in ("-l", "--delta"):
				argsX_set(argsX, "delta", int(arg))
			elif opt in ("-r", "--renew"):
				argsX_set(argsX, "renew", True)
			elif opt in ("-t", "--text"):
				argsX_set(argsX, "text", True)
			elif opt in ("-v", "--verbose"):
				argsX_set(argsX, "verbose", True)
			else:
				print ("(opt: {})".format(opt))
	else:
		show_usage(argv)

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
	DBG_WN_LN("{} (app_quit_get: {})".format(DBG_TXT_BYE_BYE, app_quit_get()) )

if __name__ == "__main__":
	main(sys.argv[0:])
