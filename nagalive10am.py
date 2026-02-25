import requests, json
from pya3 import *
import dateutil.parser
import datetime
from datetime import timedelta
import pandas as pd
import time
import sys
from html import *
import webbrowser
import os
import argparse
import logging
import random
import atexit



class Log( object ):
	def __init__(self):
		self.orgstdout = sys.stdout
		self.log = open( "output2.txt", "a" )

	def write(self, msg):
		self.orgstdout.write( msg )
		self.log.write( msg )


# sys.stdout = Log()
# filename = 'file:///'+os.getcwd()+'/' + 'check.html'
# webbrowser.open_new_tab(filename)
# to open/create a new html file in the write mode

# CLI + mode flags
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--test', action='store_true', help='Run in simulated paper-test mode')
parser.add_argument('--duration', type=int, default=30, help='Test duration in minutes')
parser.add_argument('--live', action='store_true', help='Enable live mode')
parser.add_argument('--confirm-live', action='store_true', help='Confirm live trading (required with --live)')
parser.add_argument('--close-open', action='store_true', help='Close open positions at start')
args, _ = parser.parse_known_args()
TEST_MODE = bool(args.test and not args.live)
LIVE_MODE = bool(args.live and args.confirm_live)

# Trailing SL configuration
TRAILING_THRESHOLD = 0.10   # +10% to activate trailing
TRAILING_SL_PERCENT = -0.04 # -4% trailing when active

f = open( 'daywisemargin.txt', 'w' )

# Credentials (prefer environment variables)
user_id = os.getenv('ALICE_USER_ID', '593605')
api_key = os.getenv('ALICE_API_KEY', 'A5XTjuqDNZVsH5kILiDSqcig5Gcnc8baeZ4zejc0aifx4D3WSm3ITX1TjXxFOW1A7Qz3AJbUYvGmNVJXfKKGvWHxJHijNNbRlg6NAL957C6U8oyCPl90K5TmbBQUc2ds')
alice = Aliceblue(user_id=user_id, api_key=api_key)


# Safe order wrappers: simulate when TEST_MODE is True
def place_order_safe(**kwargs):
	if TEST_MODE:
		oms = f"SIM{int(time.time()*1000)}"
		logging.info("SIMULATED place_order %s", kwargs)
		# ledger entry
		with open('trade_ledger.jsonl','a') as tl:
			entry = {'time': time.time(), 'action': 'place', 'details': kwargs, 'oms': oms}
			tl.write(json.dumps(entry)+"\n")
		return {'data': {'oms_order_id': oms}}
	return alice.place_order(**kwargs)

def modify_order_safe(**kwargs):
	if TEST_MODE:
		logging.info("SIMULATED modify_order %s", kwargs)
		with open('trade_ledger.jsonl','a') as tl:
			entry = {'time': time.time(), 'action': 'modify', 'details': kwargs}
			tl.write(json.dumps(entry)+"\n")
		return {'data': {'status': 'modified'}}
	return alice.modify_order(**kwargs)

def cancel_order_safe(order_id):
	if TEST_MODE:
		logging.info("SIMULATED cancel_order %s", order_id)
		with open('trade_ledger.jsonl','a') as tl:
			entry = {'time': time.time(), 'action': 'cancel', 'order_id': order_id}
			tl.write(json.dumps(entry)+"\n")
		return {'data': {'status': 'cancelled'}}
	return alice.cancel_order(order_id)

def get_order_history_safe(order_id):
	if TEST_MODE:
		logging.info("SIMULATED get_order_history %s", order_id)
		with open('trade_ledger.jsonl','a') as tl:
			entry = {'time': time.time(), 'action': 'history', 'order_id': order_id}
			tl.write(json.dumps(entry)+"\n")
		return {'data': [{'order_status': 'complete'}]}
	return alice.get_order_history(order_id)


# Logging setup
logging.basicConfig(level=logging.INFO, filename='nagalive10am.log', filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s')


# Simple price simulator for test mode
class PriceSimulator:
    def __init__(self, start_price):
        self.price = float(start_price)
    def step(self):
        # small random walk
        self.price *= (1 + random.uniform(-0.002, 0.002))
        return round(self.price, 2)


# ensure ledger closed on exit (file used with append so just log)
def _on_exit():
    logging.info('Exiting, TEST_MODE=%s LIVE_MODE=%s', TEST_MODE, LIVE_MODE)
atexit.register(_on_exit)


if TEST_MODE:
	now_dt = datetime.datetime.now()
	date = now_dt.day
	month = now_dt.month
	range_greater = int(os.getenv('TEST_RANGE_GREATER','100'))
	range_smaller = int(os.getenv('TEST_RANGE_SMALLER','1000'))
	sec = int(os.getenv('TEST_SEC','2'))
	year1 = now_dt.year
	year = str(year1 % 100)
	datefinal = str(date)+"/"+str(month)+"/"+year+" "
	print(f"TEST_MODE defaults: date={date} month={month} range>={range_greater} range<={range_smaller} sec={sec}")
else:
	date=int(input("enter date :"))
	month=int(input("enter month :"))
	'''ex_date=int(input("enter expiry date :"))
	ex_month=int(input("enter expairy month :"))
	date=datetime.datetime.now().day
	month=datetime.datetime.now().month'''
	range_greater=int(input("Enter range between greater than :"))
	range_smaller=int(input("Enter range between smaller than :"))
	year1=datetime.datetime.now().year
	#year=str(input("enter year :"))
	year=str("22")
	datefinal=str(date)+"/"+str(month)+"/"+year+" "
today = datetime.date(year1,month,date)
td=today
i=0
exp=[]

while i<2:
	td = td + timedelta(days=1)
	if td.weekday() == 3:          # 3 is thursday
		print(td)
		exp.append(td)
		i=i+1
print(exp,"  ",today)
expairy_date=exp[0]
if((exp[0]-today)<timedelta(days=2)):
	print(exp[1],"Hiiiiii")
	expairy_date = exp[1]
#expairy_date=datetime.date( 2022, ex_month, ex_date )
sec=int(input("Enter no of sec: "))
print("expiery Date: ",expairy_date)
ex_day=expairy_date.day
ex_month=expairy_date.month
ex_year=expairy_date.year
print(ex_day,ex_month,ex_year)

expairy_date=str(ex_day)+'-'+str(ex_month)+'-'+str(ex_year)
print(expairy_date)

#from_datetime=datetime.strptime(datefinal, "%d/%m/%y %H:%M")

from_datetime=datetime.datetime.strptime(datefinal+"9:15", "%d/%m/%y %H:%M")
to_datetime = datetime.datetime.strptime(datefinal+"10:01", "%d/%m/%y %H:%M")
interval = "15_MIN"   # ["DAY", "1_HR", "3_HR", "1_MIN", "5_MIN", "15_MIN", "60_MIN"]
indices = False
maxi = 0




def get_historical(instrument, from_datetime, to_datetime, interval, indices=False):
	# intervals = ["1", "2", "3", "4", "5", "10", "15", "30", "60", "120", "180", "240", "D", "1W", "1M"]
	params = {"symbol": instrument.token,
			  "exchange": instrument.exchange if not indices else f"{instrument.exchange}::index",
			  "from": str( int( from_datetime.timestamp() ) ),
			  "to": str( int( to_datetime.timestamp() ) ),
			  "resolution": interval,
			  "user": user_id}
	lst = requests.get( f"https://a3.aliceblueonline.com/rest/AliceBlueAPIService/chart/history?",
						params=params ).json()
	print(lst)
	records = []
	global maxi
	maxi = 0
	get_historical.high = [0]
	get_historical.high.clear()

	get_historical.maxi = 0
	get_historical.high.append( 0 )
	# for ke in lst:
	#     print(ke,lst[ke],'  ',max(lst[ke]))
	get_historical.high.append( max(max(lst['o']),max(lst['h'])) )
	print(max(max(lst['o']),max(lst['h'])))
	print(get_historical.high)
	maxi = max( get_historical.high )
	print(get_historical.maxi)


start_time = datetime.datetime.strptime( datefinal + "10:00", "%d/%m/%y %H:%M" )
while True:
	if (datetime.datetime.now() >= start_time):

		break
	else:
		print( "Waiting....for 10am..." )
		time.sleep( 5 )

from_datetimebn=datetime.datetime.strptime(datefinal+"9:59", "%d/%m/%y %H:%M")
to_datetimebn = datetime.datetime.strptime(datefinal+"10:00", "%d/%m/%y %H:%M")
intervalbn = "1"   # ["DAY", "1_HR", "3_HR", "1_MIN", "5_MIN", "15_MIN", "60_MIN"]
indicesbn = True
banknifty_nse_index = alice.get_instrument_by_symbol('INDICES','NIFTY BANK')
get_historical( banknifty_nse_index, from_datetimebn, to_datetimebn, intervalbn, indicesbn )
# print(dfbn)
quo=maxi//100
spot_price=quo*100

print( "spot price :", spot_price )

if TEST_MODE:
	price_simulator = PriceSimulator(spot_price)

ceflag = 0
peflag = 0
ce_price_fin = 0
pe_price_fin = 0
ce_at = 0
pe_at = 0

ce_price=spot_price-300
pe_price=spot_price+300
# instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
#                                              strike=pe_price, is_CE=False )
# instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
#                                              strike=ce_price, is_CE=True )
instrumentce = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
											strike=ce_price, is_CE=True )
get_historical( instrumentce, from_datetime, to_datetime, interval, indices )
pre_ce_at=maxi
instrumentpe = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
											strike=pe_price, is_CE=False )

get_historical( instrumentpe, from_datetime, to_datetime, interval, indices )
pre_pe_at=maxi
print(pre_ce_at,pre_pe_at)

while True:

	if ceflag!=1:
	   instrumentce = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date,
													 is_fut=False,
													 strike=ce_price, is_CE=True )
	   get_historical( instrumentce, from_datetime, to_datetime, interval, indices )
	   print( "ce_price = ", ce_price ," = ",maxi)
	   if(maxi>=range_greater and maxi<=range_smaller):
		   print("ce_price = ",ce_price)
		   ce_price_fin=ce_price
		   ce_at=maxi
		   ceflag=1
	   else:
		   ce_price=ce_price+100

	   if (maxi < range_greater):
		   ceflag = 1
		   ce_price_fin = ce_price-200
		   ce_at = pre_ce_at
	   pre_ce_at =maxi

	if peflag != 1:
		instrumentpe = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date,
													 is_fut=False,
													 strike=pe_price, is_CE=False )

		get_historical( instrumentpe, from_datetime, to_datetime, interval, indices )
		print( "pe_price = ", pe_price, " = ", maxi )
		if (maxi >= range_greater and maxi <= range_smaller):
			print( pe_price )
			pe_price_fin=pe_price
			pe_at=maxi
			peflag = 1
		else:
			pe_price = pe_price - 100

		if(maxi<range_greater):
			peflag = 1
			pe_price_fin = pe_price+200
			pe_at = pre_pe_at
		pre_pe_at=maxi
	if ceflag==1 and peflag==1:
		break

print( "ce_price = ", ce_price_fin, " at =", ce_at )
print( "pe_price = ", pe_price_fin, " at =", pe_at )
ce_price = ce_price_fin
pe_price = pe_price_fin
# instrument = alice.get_instrument_by_symbol("NSE", "Nifty Bank")expiry_date=datetime.date('2022', '5', '19')
instrumentce = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date,
													 is_fut=False,
													 strike=ce_price_fin, is_CE=True )
# instrumentce = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=expairy_date, is_fut=False, strike=ce_price_fin, is_CE = True)
instrumentpe = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date=expairy_date,
													 is_fut=False,
													 strike=pe_price_fin, is_CE=False )
# instrumentpe = alice.get_instrument_for_fno(symbol = 'BANKNIFTY', expiry_date=expairy_date, is_fut=False, strike=pe_price_fin, is_CE = False)
from_datetime=datetime.datetime.strptime(datefinal+"9:15", "%d/%m/%y %H:%M")
to_datetime = datetime.datetime.strptime(datefinal+"10:01", "%d/%m/%y %H:%M")
exit_time=datetime.datetime.strptime(datefinal+"15:15", "%d/%m/%y %H:%M")
interval = "15"   # ["DAY", "1_HR", "3_HR", "1_MIN", "5_MIN", "15_MIN", "60_MIN"]
indices = False
get_historical(instrumentce, from_datetime, to_datetime, interval, indices)
dfce=alice.get_historical(instrumentce, from_datetime, to_datetime, interval, indices)
print(dfce)
cedayhigh=maxi
print(maxi)
dfpe = alice.get_historical(instrumentpe, from_datetime, to_datetime, interval, indices)
# dfce.index = dfce["date"]
# dfcde = dfce.drop("date", axis=1)
# dfce["MA_3"] = dfcde["close"].rolling(window=3).mean()
cebuy25 = 0
cebuy50 =0
cebuy100 = 0
cebuy200 = 0
pebuy25 = 0
pebuy50 = 0
pebuy100 = 0
pebuy200 = 0
exit=0
print(dfpe)

i=1
k=0
get_historical(instrumentpe, from_datetime, to_datetime, interval, indices)
pedayhigh=maxi
print(maxi)

p = 0
global pre1
pre1 = 0
global pre2
pre2 = 0

socket_opened = False
h = 0
lp = 0


def event_handler_quote_update(message):
	# print( f"quote update {message}" )
	# print(message)
	# print(message['high'])
	# event_handler_quote_update.hi=0
	# event_handler_quote_update.hi=message['ltp']
	global h
	h = 0
	h = message['high']
	global lp
	lp = 0
	lp = message['ltp']


def open_callback():
	global socket_opened
	socket_opened = True


alice.start_websocket( subscribe_callback=event_handler_quote_update,
					   socket_open_callback=open_callback,
					   run_in_background=True )
while (socket_opened == False):
	pass

'''alice.subscribe( instrument1, LiveFeedType.MARKET_DATA )

#print(event_handler_quote_update.hi)
from_datetime1 = datetime.datetime.now()
print("i value=====",i,from_datetime1)
time.sleep( 2 )
print(h)'''


def getpricehigh(instrument):
	alice.subscribe( instrument, LiveFeedType.MARKET_DATA )
	# print(event_handler_quote_update.hi)
	i = 0
	from_datetime1 = datetime.datetime.now()
	print( instrument )
	time.sleep( 1 )
	print( "i value=====", i, from_datetime1, " hai this is def", h )
	alice.unsubscribe( instrument, LiveFeedType.MARKET_DATA )
	return (h)


def getpricelive(instrument):
	if TEST_MODE:
		try:
			return price_simulator.step()
		except NameError:
			return lp
	alice.subscribe( instrument, LiveFeedType.MARKET_DATA )
	# print(event_handler_quote_update.hi)
	i = 0
	from_datetime1 = datetime.datetime.now()
	print( "-----x-----" )
	print( instrument )
	time.sleep( 1 )
	print( "i value=====", i, from_datetime1, " hai this is def", h )
	alice.unsubscribe( instrument, LiveFeedType.MARKET_DATA )
	return (lp)


def getprice(instrument):
	ltp = getpricelive( instrument )
	check = 0
	print( ltp )
	global pre_ce, pre_pe

	print( instrument.symbol, type( instrument.symbol ) )
	sym = str( instrument.symbol )
	if ("CE" in sym):
		print( "ce===" , instrument )
		if (pre_pe + 1 >= ltp and pre_pe - 1 <= ltp):
			check = pre_ce
			print( "Happened" )
		else:
			print( "pre_ce = ", pre_ce, "pre_pe = ", pre_pe, "check= ", check )
			check = ltp
			pre2_ce = pre_ce
			pre_ce = check
		print( "pre_ce = ", pre_ce, "pre_pe = ", pre_pe, "check= ", check )
		return check
	else:
		print( "pe===" , instrument )
		if (pre_ce + 1 >= ltp and pre_ce - 1 <= ltp):
			check = pre_ce
			print( "Happened" )
		else:
			print( "pre_ce= ", pre_ce, "pre_pe= ", pre_pe, "check= ", check )
			check = ltp
			pre2_pe = pre_pe
			pre_pe = check
		print( "pre_ce= ", pre_ce, "pre_pe= ", pre_pe, "check= ", check )
		return check


def getlive_priceatrequired():
	ceflag = 0
	peflag = 0
	ce_price_fin = 0
	pe_price_fin = 0
	ce_at = 0
	pe_at = 0
	instrument = alice.get_instrument_by_symbol( "NSE", "Nifty Bank" )
	maxi = getprice( instrument=instrument )
	quo = maxi // 100
	spot_price = quo * 100
	print( spot_price )
	ce_price = spot_price - 300
	pe_price = spot_price + 300
	instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
												 is_fut=False,
												 strike=ce_price, is_CE=True )
	maxi = getprice( instrument=instrumentce )
	pre_ce_at = maxi
	instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
												 is_fut=False,
												 strike=pe_price, is_CE=False )
	maxi = getprice( instrument=instrumentpe )
	pre_pe_at = maxi

	while True:

		if ceflag != 1:
			instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
														 is_fut=False, strike=ce_price, is_CE=True )
			cemaxi = getprice( instrument=instrumentce )
			print( "ce_price = ", ce_price, " = ", cemaxi )
			if (cemaxi >= range_greater and cemaxi <= range_smaller):
				print( "ce_price = ", ce_price )
				ce_price_fin = ce_price
				ce_at = cemaxi
				ceflag = 1
			else:
				ce_price = ce_price + 100

			if (cemaxi < range_greater):
				ceflag = 1
				ce_price_fin = ce_price - 200
				ce_at = pre_ce_at
			pre_ce_at = cemaxi

		if peflag != 1:
			instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
														 is_fut=False, strike=pe_price, is_CE=False )
			pemaxi = getprice( instrument=instrumentpe )
			print( "pe_price = ", pe_price, " = ", pemaxi )
			if (pemaxi >= range_greater and pemaxi <= range_smaller):
				print( pe_price )
				pe_price_fin = pe_price
				pe_at = pemaxi
				peflag = 1
			else:
				pe_price = pe_price - 100

			if (pemaxi < range_greater):
				peflag = 1
				pe_price_fin = pe_price + 200
				pe_at = pre_pe_at
			pre_pe_at = pemaxi
		if ceflag == 1 and peflag == 1:
			break

	print( "ce_price = ", ce_price_fin, " at =", ce_at )
	print( "pe_price = ", pe_price_fin, " at =", pe_at )
	ce_price = ce_price_fin
	pe_price = pe_price_fin
	return [ce_price_fin, ce_at, pe_price_fin, pe_at]


def getspot_priceatrequired():
	ceflag = 0
	peflag = 0
	ce_price_fin = 0
	pe_price_fin = 0
	ce_at = 0
	pe_at = 0
	instrument = alice.get_instrument_by_symbol( "NSE", "Nifty Bank" )
	maxi = getprice( instrument=instrument )
	quo = maxi // 100
	spot_price = quo * 100
	print( spot_price )
	ce_price = spot_price - 300
	pe_price = spot_price + 300
	instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
												 is_fut=False,
												 strike=ce_price, is_CE=True )
	maxi = getpricehigh( instrument=instrumentce )
	pre_ce_at = maxi
	instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
												 is_fut=False,
												 strike=pe_price, is_CE=False )
	maxi = getpricehigh( instrument=instrumentpe )
	pre_pe_at = maxi

	while True:

		if ceflag != 1:
			instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
														 is_fut=False, strike=ce_price, is_CE=True )
			cemaxi = getpricehigh( instrument=instrumentce )
			print( "ce_price = ", ce_price, " = ", cemaxi )
			if (cemaxi >= range_greater and cemaxi <= range_smaller):
				print( "ce_price = ", ce_price )
				ce_price_fin = ce_price
				ce_at = cemaxi
				ceflag = 1
			else:
				ce_price = ce_price + 100

			if (cemaxi < range_greater):
				ceflag = 1
				ce_price_fin = ce_price - 200
				ce_at = pre_ce_at
			pre_ce_at = cemaxi

		if peflag != 1:
			instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date,
														 is_fut=False, strike=pe_price, is_CE=False )
			pemaxi = getpricehigh( instrument=instrumentpe )
			print( "pe_price = ", pe_price, " = ", pemaxi )
			if (pemaxi >= range_greater and pemaxi <= range_smaller):
				print( pe_price )
				pe_price_fin = pe_price
				pe_at = pemaxi
				peflag = 1
			else:
				pe_price = pe_price - 100

			if (pemaxi < range_greater):
				peflag = 1
				pe_price_fin = pe_price + 200
				pe_at = pre_pe_at
			pre_pe_at = pemaxi
		if ceflag == 1 and peflag == 1:
			break

	print( "ce_price = ", ce_price_fin, " at =", ce_at )
	print( "pe_price = ", pe_price_fin, " at =", pe_at )
	ce_price = ce_price_fin
	pe_price = pe_price_fin
	return [ce_price_fin, ce_at, pe_price_fin, pe_at]


ce_price_fun = getspot_priceatrequired()

print( " check by live feed :", ce_price_fun )

instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
											 strike=ce_price_fun[0], is_CE=True )
instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
											 strike=ce_price_fun[2], is_CE=False )
cedayhigh = ce_price_fun[1]
cedayhigh = round( cedayhigh + 0.00, 1 )
pedayhigh = ce_price_fun[3]
pedayhigh = round( pedayhigh + 0.00, 1 )
ce_price = ce_price_fun[0]
pe_price = ce_price_fun[2]
# starting
placed_orders = {"ce_dayhigh": None, "pe_dayhigh": None, "ce_stoploss": None, "pe_stoploss": None, "ce_need_buy": None,
				 "pe_need_buy": None}
ce_dayhigh_buy = place_order_safe( transaction_type=TransactionType.Buy,
				instrument=instrumentce,
				quantity=25,
				order_type=OrderType.StopLossLimit,
				product_type=ProductType.Intraday,
				price=cedayhigh + 0.5,
				trigger_price=cedayhigh + 0.0,
				stop_loss=None,
				square_off=None,
				trailing_sl=None,
				is_amo=False )
print( ce_dayhigh_buy, ce_dayhigh_buy['data']['oms_order_id'] )
placed_orders["ce_dayhigh"] = ce_dayhigh_buy['data']['oms_order_id']

pe_dayhigh_buy = place_order_safe( transaction_type=TransactionType.Buy,
				instrument=instrumentpe,
				quantity=25,
				order_type=OrderType.StopLossLimit,
				product_type=ProductType.Intraday,
				price=pedayhigh + 0.5,
				trigger_price=pedayhigh + 0.0,
				stop_loss=None,
				square_off=None,
				trailing_sl=None,
				is_amo=False )
print( pe_dayhigh_buy, pe_dayhigh_buy['data']['oms_order_id'] )
placed_orders["pe_dayhigh"] = pe_dayhigh_buy['data']['oms_order_id']
i = 1
print( placed_orders )

while i > 0:
	pre_time = datetime.datetime.now()
	print( pre_time )

	live_ce_price = getprice( instrumentce )
	print( live_ce_price, "=", ce_price )

	if (live_ce_price >= cedayhigh):
		print( "ce bought at: ", cedayhigh )
		cebuy25 = 25 * cedayhigh
		cebuy50 = 50 * cedayhigh
		cebuy100 = 100 * cedayhigh
		cebuy200 = 200 * cedayhigh
		print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )

		stoploss = cedayhigh - cedayhigh / 100 * 30
		stoploss = round( stoploss + 0.00, 1 )
		target = cedayhigh + cedayhigh / 100 * 50
		percentage = 20

			cancel_order_safe( placed_orders["pe_dayhigh"] )

			ce_dayhigh_Stoploss = place_order_safe( transaction_type=TransactionType.Sell,
												 instrument=instrumentce,
												 quantity=25,
												 order_type=OrderType.StopLossLimit,
												 product_type=ProductType.Intraday,
					 price=stoploss - 0.5,
					 trigger_price=stoploss - 0.0,
												 stop_loss=None,
												 square_off=None,
					 trailing_sl=None,
					 is_amo=False )
		print( ce_dayhigh_Stoploss, ce_dayhigh_Stoploss['data']['oms_order_id'] )
			placed_orders["ce_stoploss"] = ce_dayhigh_Stoploss['data']['oms_order_id']
			print( placed_orders )
			# trailing state for this trade
			trailing_active = False
			highest_price = cedayhigh
			current_trailing_sl = None
			entry_price = cedayhigh
		while True:
			pre_time = datetime.datetime.now()
			print( pre_time )
			live_ce_price = getprice( instrument=instrumentce )
			print( live_ce_price, "=", ce_price )
			# trailing activation / update
			highest_price = max(highest_price, live_ce_price)
			if (not trailing_active) and (highest_price >= entry_price * (1 + TRAILING_THRESHOLD)):
				trailing_active = True
				current_trailing_sl = round(highest_price * (1 + TRAILING_SL_PERCENT), 1)
				print("Activating trailing SL ->", current_trailing_sl)
				print(modify_order_safe(transaction_type=TransactionType.Sell,
							instrument=instrumentce,
							product_type=ProductType.Intraday,
							order_id=placed_orders["ce_stoploss"],
							order_type=OrderType.StopLossLimit,
							quantity=25,
							price=current_trailing_sl - 0.5,
							trigger_price=current_trailing_sl + 0.0))
			elif trailing_active:
				new_sl = round(highest_price * (1 + TRAILING_SL_PERCENT), 1)
				if new_sl > current_trailing_sl:
					current_trailing_sl = new_sl
					print("Updating trailing SL ->", current_trailing_sl)
					print(modify_order_safe(transaction_type=TransactionType.Sell,
							instrument=instrumentce,
							product_type=ProductType.Intraday,
							order_id=placed_orders["ce_stoploss"],
							order_type=OrderType.StopLossLimit,
							quantity=25,
							price=current_trailing_sl - 0.5,
							trigger_price=current_trailing_sl + 0.0))
			print( live_ce_price, " -", percentage, "=", ce_price )
			time.sleep( sec )
			if (live_ce_price >= cedayhigh + (cedayhigh / 100 * percentage)):
				stoploss = cedayhigh + cedayhigh / 100 * (percentage - 7)
				stoploss = round( stoploss + 0.00, 1 )
				percentage = percentage + 7
				print( live_ce_price, " -", percentage )
				print( placed_orders )
						print( modify_order_safe( transaction_type=TransactionType.Sell,
								instrument=instrumentce,
								product_type=ProductType.Intraday,
								order_id=placed_orders["ce_stoploss"],
								order_type=OrderType.StopLossLimit,
								quantity=25,
								price=stoploss - 0.5,
								trigger_price=stoploss + 0.0 ) )
				while True:
					pre_time = datetime.datetime.now()
					print( pre_time )
					live_ce_price = getprice( instrument=instrumentce )
					print( live_ce_price, "=", ce_price )
					print( live_ce_price, " -", percentage, "=", ce_price )
					time.sleep( sec )
					if (live_ce_price >= cedayhigh + (cedayhigh / 100 * percentage)):
						stoploss = cedayhigh + cedayhigh / 100 * (percentage - 7)
						stoploss = round( stoploss + 0.00, 1 )
						percentage = percentage + 7
						print( live_ce_price, " -", percentage, "=", ce_price )
							print( modify_order_safe( transaction_type=TransactionType.Sell,
									instrument=instrumentce,
									product_type=ProductType.Intraday,
									order_id=placed_orders["ce_stoploss"],
									order_type=OrderType.StopLossLimit,
									quantity=25,
									price=stoploss + 0.5,
									trigger_price=stoploss + 0.0 ) )
						print( placed_orders )
					if (live_ce_price <= stoploss):
						print( "ce exit at: ", stoploss, live_ce_price, "=", ce_price )
						print( "entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
						cebuy25 = -cebuy25 + 25 * stoploss
						cebuy50 = -cebuy50 + 50 * stoploss
						cebuy100 = -cebuy100 + 100 * stoploss
						cebuy200 = -cebuy200 + 200 * stoploss
						print( "Fianl :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
						status = get_order_history_safe( placed_orders["ce_stoploss"] )['data'][0]['order_status']
						time.sleep( 5 )
						if (status != "complete"):
							print( modify_order_safe( transaction_type=TransactionType.Sell,
									instrument=instrumentce,
									product_type=ProductType.Intraday,
									order_id=placed_orders["ce_stoploss"],
									order_type=OrderType.Market,
									quantity=25,
									price=0.0,
									trigger_price=None ) )
						exit = 1
						break
					if pre_time >= exit_time:
						print( "time is 3pm closed" )
						print( "ce exit at: ", stoploss, live_ce_price, "=", ce_price )
						print( "entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
						cebuy25 = -cebuy25 + 25 * stoploss
						cebuy50 = -cebuy50 + 50 * stoploss
						cebuy100 = -cebuy100 + 100 * stoploss
						cebuy200 = -cebuy200 + 200 * stoploss
						print( "Fianl :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
						print( modify_order_safe( transaction_type=TransactionType.Sell,
									instrument=instrumentce,
									product_type=ProductType.Intraday,
									order_id=placed_orders["ce_stoploss"],
									order_type=OrderType.Market,
									quantity=25,
									price=0.0,
									trigger_price=None ) )
						exit = 1
						break
