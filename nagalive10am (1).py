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
f = open( 'daywisemargin.txt', 'w' )

user_id='593605'
alice = Aliceblue(user_id='593605',api_key='A5XTjuqDNZVsH5kILiDSqcig5Gcnc8baeZ4zejc0aifx4D3WSm3ITX1TjXxFOW1A7Qz3AJbUYvGmNVJXfKKGvWHxJHijNNbRlg6NAL957C6U8oyCPl90K5TmbBQUc2ds')


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


# instrument=[]
def getpricelive(instrument):
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


'''def getpriceu(instrument):
    ltp=getpricelive(instrument)
    check=0
    global pre1,pre2
    if(pre1 <= ltp+1 and pre1 >=ltp-1):
        check= pre2
    else:
        check= ltp
    pre2=pre1
    pre1=check
    return check'''

global pre_ce, pre_pe
global pre2_ce, pre2_pe
pre2_ce = 0
pre2_pe = 0
pre_ce = 0
pre_pe = 0


def getprice(instrument):
    ltp = getpricelive( instrument )
    check = 0
    print( ltp )
    global pre_ce, pre_pe

    print( instrument.symbol, type( instrument.symbol ) )
    sym = str( instrument.symbol )
    if ("CE" in sym):
        print( "ce===", instrument )
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
        print( "pe===", instrument )
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
ce_dayhigh_buy = alice.place_order( transaction_type=TransactionType.Buy,
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

pe_dayhigh_buy = alice.place_order( transaction_type=TransactionType.Buy,
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

        alice.cancel_order( placed_orders["pe_dayhigh"] )

        ce_dayhigh_Stoploss = alice.place_order( transaction_type=TransactionType.Sell,
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
                print( live_ce_price, " -", percentage )
                print( placed_orders )
                print( alice.modify_order( transaction_type=TransactionType.Sell,
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
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
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
                        status = alice.get_order_history( placed_orders["ce_stoploss"] )['data'][0]['order_status']
                        time.sleep( 5 )
                        if (status != "complete"):
                            print( alice.modify_order( transaction_type=TransactionType.Sell,
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
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        exit = 1
                        break


            elif (live_ce_price <= cedayhigh - cedayhigh / 100 * 10):
                list_pe = getlive_priceatrequired()
                pe_price = list_pe[2]
                instrumentpe = alice.get_instrument_for_fno( symbol='BANKNIFTY',
                                                             expiry_date=expairy_date, is_fut=False,
                                                             strike=pe_price, is_CE=False )
                pre_time = datetime.datetime.now()
                print( pre_time )
                live_pe_price = getprice( instrument=instrumentpe )
                print( live_pe_price, "=", pe_price )
                pedayhigh = live_pe_price

                Pe_need_buy = alice.place_order( transaction_type=TransactionType.Buy,
                                                 instrument=instrumentpe,
                                                 quantity=25,
                                                 order_type=OrderType.Market,
                                                 product_type=ProductType.Intraday,
                                                 price=0.0,
                                                 trigger_price=None,
                                                 stop_loss=None,
                                                 square_off=None,
                                                 trailing_sl=None,
                                                 is_amo=False )
                time.sleep( 10 )
                placed_orders["pe_need_buy"] = Pe_need_buy['data']['oms_order_id']

                print( "pe bought at: ", pedayhigh, "=", pe_price )
                stoplosspe = pedayhigh - pedayhigh / 100 * 30
                stoplosspe = round( stoplosspe + 0.00, 1 )
                targetpe = pedayhigh + pedayhigh / 100 * 50
                percentage = 20

                pe_need_Stoploss = alice.place_order( transaction_type=TransactionType.Sell,
                                                      instrument=instrumentpe,
                                                      quantity=25,
                                                      order_type=OrderType.StopLossLimit,
                                                      product_type=ProductType.Intraday,
                                                      price=stoplosspe + 0.5,
                                                      trigger_price=stoplosspe + 0.0,
                                                      stop_loss=None,
                                                      square_off=None,
                                                      trailing_sl=None,
                                                      is_amo=False )
                print( pe_need_Stoploss, pe_need_Stoploss['data']['oms_order_id'] )
                placed_orders["pe_stoploss"] = pe_need_Stoploss['data']['oms_order_id']
                pebuy25 = 25 * pedayhigh
                pebuy50 = 50 * pedayhigh
                pebuy100 = 100 * pedayhigh
                pebuy200 = 200 * pedayhigh
                print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                print( placed_orders )
                while True:
                    pre_time = datetime.datetime.now()
                    print( pre_time )
                    live_ce_price = getprice( instrument=instrumentce )
                    print( live_ce_price, "=", ce_price )
                    cemax = live_ce_price
                    print( live_ce_price, " -", percentage, "=", ce_price )
                    pre_time = datetime.datetime.now()
                    print( pre_time )
                    live_pe_price = getprice( instrument=instrumentpe )
                    print( live_pe_price, "=", pe_price )
                    pemax = live_pe_price
                    print( live_pe_price, " -", percentage, "=", pe_price )
                    time.sleep( sec )
                    percentagece = 20
                    percentagepe = 20
                    if (cemax >= cedayhigh + (cedayhigh / 100 * percentagece)):
                        stoploss = cedayhigh + cedayhigh / 100 * (percentagece - 7)
                        stoploss = round( stoploss + 0.00, 1 )
                        percentagece = percentagece + 7
                        print( cemax, " -", percentagece )
                        print( "pe exit at: ", pemax )
                        pebuy25 = 25 * pemax - pebuy25
                        pebuy50 = 50 * pemax - pebuy50
                        pebuy100 = 100 * pemax - pebuy100
                        pebuy200 = 200 * pemax - pebuy200

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.StopLossLimit,
                                                   quantity=25,
                                                   price=stoploss + 0.5,
                                                   trigger_price=stoploss + 0.0 ) )
                        print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        while True:
                            pre_time = datetime.datetime.now()
                            print( pre_time )
                            live_ce_price = getprice( instrument=instrumentce )
                            print( live_ce_price, "=", ce_price )
                            print( live_ce_price, " -", percentagece, "=", ce_price )
                            time.sleep( sec )

                            if (live_ce_price >= cedayhigh + (cedayhigh / 100 * percentagece)):
                                stoploss = cedayhigh + cedayhigh / 100 * (percentagece - 7)
                                stoploss = round( stoploss + 0.00, 1 )
                                percentagece = percentagece + 7
                                print( live_ce_price, " -", percentagece )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentce,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["ce_stoploss"],
                                                           order_type=OrderType.StopLossLimit,
                                                           quantity=25,
                                                           price=stoploss + 0.5,
                                                           trigger_price=stoploss + 0.0 ) )
                            if (live_ce_price <= stoploss):
                                print( "ce exit at: ", stoploss, live_ce_price )
                                print( "entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                cebuy25 = -cebuy25 + 25 * stoploss + pebuy25
                                cebuy50 = -cebuy50 + 50 * stoploss + pebuy50
                                cebuy100 = -cebuy100 + 100 * stoploss + pebuy100
                                cebuy200 = -cebuy200 + 200 * stoploss + pebuy200
                                print( "Fianl :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                status = alice.get_order_history( placed_orders["ce_stoploss"] )['data'][0][
                                    'order_status']
                                time.sleep( 5 )
                                if (status != "complete"):
                                    print( alice.modify_order( transaction_type=TransactionType.Sell,
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
                                print( "ce exit at: ", stoploss, live_ce_price )
                                print( "entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                cebuy25 = -cebuy25 + 25 * stoploss + pebuy25
                                cebuy50 = -cebuy50 + 50 * stoploss + pebuy50
                                cebuy100 = -cebuy100 + 100 * stoploss + pebuy100
                                cebuy200 = -cebuy200 + 200 * stoploss + pebuy200
                                print( "Fianl :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                alice.cancel_order( placed_orders["pe_dayhigh"] )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentce,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["ce_stoploss"],
                                                           order_type=OrderType.Market,
                                                           quantity=25,
                                                           price=0.0,
                                                           trigger_price=None ) )
                                exit = 1
                                break

                    elif (pemax >= pedayhigh + (pedayhigh / 100 * percentagepe)):
                        stoploss = pedayhigh + pedayhigh / 100 * (percentagepe - 7)
                        stoploss = round( stoploss + 0.00, 1 )
                        percentagepe = percentagepe + 7
                        print( pemax, " -", percentagepe )
                        print( "ce exit at: ", cemax )
                        cebuy25 = 25 * cemax - cebuy25
                        cebuy50 = 50 * cemax - cebuy50
                        cebuy100 = 100 * cemax - cebuy100
                        cebuy200 = 200 * cemax - cebuy200

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.StopLossLimit,
                                                   quantity=25,
                                                   price=stoploss + 0.5,
                                                   trigger_price=stoploss + 0.0 ) )

                        print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                        while True:
                            pre_time = datetime.datetime.now()
                            print( pre_time )
                            live_pe_price = getprice( instrument=instrumentpe )
                            print( live_pe_price, "=", pe_price )
                            print( live_pe_price, " -", percentagepe, "=", pe_price )
                            k = k + 1
                            time.sleep( sec )
                            if (live_pe_price >= pedayhigh + (pedayhigh / 100 * percentagepe)):
                                stoploss = pedayhigh + pedayhigh / 100 * (percentagepe - 7)
                                stoploss = round( stoploss + 0.00, 1 )
                                percentagepe = percentagepe + 7
                                print( live_pe_price, " -", percentagepe )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentpe,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["pe_stoploss"],
                                                           order_type=OrderType.StopLossLimit,
                                                           quantity=25,
                                                           price=stoploss + 0.5,
                                                           trigger_price=stoploss + 0.0 ) )
                            if (live_pe_price <= stoploss):
                                print( "pe exit at: ", stoploss, live_pe_price )
                                print( "Entry :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                pebuy25 = -pebuy25 + 25 * stoploss + cebuy25
                                pebuy50 = -pebuy50 + 50 * stoploss + cebuy50
                                pebuy100 = -pebuy100 + 100 * stoploss + cebuy100
                                pebuy200 = -pebuy200 + 200 * stoploss + cebuy200
                                print( "Exit :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                status = alice.get_order_history( placed_orders["pe_stoploss"] )['data'][0][
                                    'order_status']
                                if (status != "complete"):
                                    print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                               instrument=instrumentpe,
                                                               product_type=ProductType.Intraday,
                                                               order_id=placed_orders["pe_stoploss"],
                                                               order_type=OrderType.Market,
                                                               quantity=25,
                                                               price=0.0,
                                                               trigger_price=None ) )
                                exit = 1
                                break
                            if pre_time >= exit_time:
                                print( "time is 3pm closed" )
                                print( "pe exit at: ", stoploss, live_pe_price )
                                print( "Entry :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                pebuy25 = -pebuy25 + 25 * stoploss + cebuy25
                                pebuy50 = -pebuy50 + 50 * stoploss + cebuy50
                                pebuy100 = -pebuy100 + 100 * stoploss + cebuy100
                                pebuy200 = -pebuy200 + 200 * stoploss + cebuy200
                                print( "Exit :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentpe,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["pe_stoploss"],
                                                           order_type=OrderType.Market,
                                                           quantity=25,
                                                           price=0.0,
                                                           trigger_price=None ) )
                                exit = 1
                                break

                    if exit == 1:
                        break

                    elif pre_time >= exit_time:
                        print( "time is 3pm closed" )
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        print( cemax, " -", percentagece )
                        print( "pe exit at: ", pemax )
                        pebuy25 = 25 * pemax - pebuy25
                        pebuy50 = 50 * pemax - pebuy50
                        pebuy100 = 100 * pemax - pebuy100
                        pebuy200 = 200 * pemax - pebuy200
                        print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        print( pemax, " -", percentagepe )
                        print( "ce exit at: ", cemax )
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        cebuy25 = 25 * cemax - cebuy25
                        cebuy50 = 50 * cemax - cebuy50
                        cebuy100 = 100 * cemax - cebuy100
                        cebuy200 = 200 * cemax - cebuy200
                        print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                        exit = 1
                        break
            if exit == 1:
                break
            elif pre_time >= exit_time:
                print( "time is 3pm closed" )
                print( "ce exit at: ", stoploss, live_ce_price )
                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                           instrument=instrumentce,
                                           product_type=ProductType.Intraday,
                                           order_id=placed_orders["ce_stoploss"],
                                           order_type=OrderType.Market,
                                           quantity=25,
                                           price=0.0,
                                           trigger_price=None ) )
                print( "entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                cebuy25 = -cebuy25 + 25 * live_ce_price
                cebuy50 = -cebuy50 + 50 * live_ce_price
                cebuy100 = -cebuy100 + 100 * live_ce_price
                cebuy200 = -cebuy200 + 200 * live_ce_price
                print( "Fianl :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                exit = 1
                break

    pre_time = datetime.datetime.now()
    print( pre_time )
    live_pe_price = getprice( instrument=instrumentpe )
    print( live_pe_price, "=", pe_price )
    time.sleep( sec )
    if (live_pe_price >= pedayhigh and exit != 1):
        print( "pe bought at: ", pedayhigh )
        pebuy25 = 25 * pedayhigh
        pebuy50 = 50 * pedayhigh
        pebuy100 = 100 * pedayhigh
        pebuy200 = 200 * pedayhigh
        print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
        stoploss = pedayhigh - pedayhigh / 100 * 30
        stoploss = round( stoploss + 0.00, 1 )
        target = pedayhigh + pedayhigh / 100 * 50
        percentage = 20

        alice.cancel_order( placed_orders["ce_dayhigh"] )

        pe_dayhigh_Stoploss = alice.place_order( transaction_type=TransactionType.Sell,
                                                 instrument=instrumentpe,
                                                 quantity=25,
                                                 order_type=OrderType.StopLossLimit,
                                                 product_type=ProductType.Intraday,
                                                 price=stoploss + 0.5,
                                                 trigger_price=stoploss + 0.0,
                                                 stop_loss=None,
                                                 square_off=None,
                                                 trailing_sl=None,
                                                 is_amo=False )
        print( pe_dayhigh_Stoploss, pe_dayhigh_Stoploss['data']['oms_order_id'] )
        placed_orders["pe_stoploss"] = pe_dayhigh_Stoploss['data']['oms_order_id']

        while True:
            pre_time = datetime.datetime.now()
            print( pre_time )
            live_pe_price = getprice( instrument=instrumentpe )
            print( live_pe_price, "=", pe_price )
            print( live_pe_price, " -", percentage, "=", pe_price )
            time.sleep( sec )
            if (live_pe_price >= pedayhigh + (pedayhigh / 100 * percentage)):
                stoploss = pedayhigh + pedayhigh / 100 * (percentage - 7)
                stoploss = round( stoploss + 0.00, 1 )
                percentage = percentage + 7
                print( live_pe_price, " -", percentage )
                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                           instrument=instrumentpe,
                                           product_type=ProductType.Intraday,
                                           order_id=placed_orders["pe_stoploss"],
                                           order_type=OrderType.StopLossLimit,
                                           quantity=25,
                                           price=stoploss + 0.5,
                                           trigger_price=stoploss + 0.0 ) )
                while True:
                    pre_time = datetime.datetime.now()
                    print( pre_time )
                    live_pe_price = getprice( instrument=instrumentpe )
                    print( live_pe_price, "=", pe_price )
                    print( live_pe_price, " -", percentage, "=", pe_price )
                    time.sleep( sec )
                    if (live_pe_price >= pedayhigh + (pedayhigh / 100 * percentage)):
                        stoploss = pedayhigh + pedayhigh / 100 * (percentage - 7)
                        stoploss = round( stoploss + 0.00, 1 )
                        percentage = percentage + 7
                        print( live_pe_price, " -", percentage, "=", pe_price )
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.StopLossLimit,
                                                   quantity=25,
                                                   price=stoploss + 0.5,
                                                   trigger_price=stoploss + 0.0 ) )
                    if (live_pe_price <= stoploss):
                        print( "pe exit at: ", stoploss, live_pe_price )
                        print( "Entry= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        pebuy25 = -pebuy25 + 25 * stoploss
                        pebuy50 = -pebuy50 + 50 * stoploss
                        pebuy100 = -pebuy100 + 100 * stoploss
                        pebuy200 = -pebuy200 + 200 * stoploss
                        print( "Profit= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        status = alice.get_order_history( placed_orders["pe_stoploss"] )['data'][0][
                            'order_status']
                        if (status != "complete"):
                            print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                       instrument=instrumentpe,
                                                       product_type=ProductType.Intraday,
                                                       order_id=placed_orders["pe_stoploss"],
                                                       order_type=OrderType.Market,
                                                       quantity=25,
                                                       price=0.0,
                                                       trigger_price=None ) )
                        exit = 1
                        break
                    if pre_time >= exit_time:
                        print( "time is 3pm closed" )
                        print( "pe exit at: ", stoploss, live_pe_price )
                        print( "Entry= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        pebuy25 = -pebuy25 + 25 * stoploss
                        pebuy50 = -pebuy50 + 50 * stoploss
                        pebuy100 = -pebuy100 + 100 * stoploss
                        pebuy200 = -pebuy200 + 200 * stoploss
                        print( "Profit= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        exit = 1
                        break


            elif (live_pe_price <= pedayhigh - pedayhigh / 100 * 10):
                list_ce = getlive_priceatrequired()
                ce_price = list_ce[0]
                instrumentce = alice.get_instrument_for_fno( symbol='BANKNIFTY', expiry_date=expairy_date, is_fut=False,
                                                             strike=ce_price, is_CE=True )
                pre_time = datetime.datetime.now()
                print( pre_time )
                live_ce_price = getprice( instrument=instrumentce )
                print( live_ce_price, "=", ce_price )
                cedayhigh = live_ce_price

                ce_need_buy = alice.place_order( transaction_type=TransactionType.Buy,
                                                 instrument=instrumentce,
                                                 quantity=25,
                                                 order_type=OrderType.Market,
                                                 product_type=ProductType.Intraday,
                                                 price=0.0,
                                                 trigger_price=None,
                                                 stop_loss=None,
                                                 square_off=None,
                                                 trailing_sl=None,
                                                 is_amo=False )
                time.sleep( 10 )
                placed_orders["ce_need_buy"] = ce_need_buy['data']['oms_order_id']
                print( placed_orders )

                stoplossce = cedayhigh - cedayhigh / 100 * 30
                stoplossce = round( stoplossce + 0.00, 1 )
                targetce = cedayhigh + cedayhigh / 100 * 50
                percentage = 20

                ce_need_Stoploss = alice.place_order( transaction_type=TransactionType.Sell,
                                                      instrument=instrumentce,
                                                      quantity=25,
                                                      order_type=OrderType.StopLossLimit,
                                                      product_type=ProductType.Intraday,
                                                      price=stoplossce + 0.5,
                                                      trigger_price=stoplossce + 0.0,
                                                      stop_loss=None,
                                                      square_off=None,
                                                      trailing_sl=None,
                                                      is_amo=False )
                print( ce_need_Stoploss, ce_need_Stoploss['data']['oms_order_id'] )
                placed_orders["ce_stoploss"] = ce_need_Stoploss['data']['oms_order_id']

                print( "ce bought at: ", cedayhigh, "=", ce_price )
                cebuy25 = 25 * cedayhigh
                cebuy50 = 50 * cedayhigh
                cebuy100 = 100 * cedayhigh
                cebuy200 = 200 * cedayhigh
                print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                while True:
                    pre_time = datetime.datetime.now()
                    print( pre_time )
                    live_ce_price = getprice( instrument=instrumentce )
                    print( live_ce_price, "=", ce_price )
                    cemax = live_ce_price
                    print( live_ce_price, " -", percentage, "=", ce_price )
                    pre_time = datetime.datetime.now()
                    print( pre_time )
                    live_pe_price = getprice( instrument=instrumentpe )
                    print( live_pe_price, "=", pe_price )
                    pemax = live_pe_price
                    print( live_pe_price, " -", percentage, "=", pe_price )
                    percentagece = 20
                    percentagepe = 20
                    time.sleep( sec )

                    if (cemax >= cedayhigh + (cedayhigh / 100 * percentagece)):
                        stoploss = cedayhigh + cedayhigh / 100 * (percentagece - 7)
                        stoploss = round( stoploss + 0.00, 1 )
                        percentagece = percentagece + 7
                        print( cemax, " -", percentagece )
                        print( "pe exit at: ", pemax )
                        pebuy25 = 25 * pemax - pebuy25
                        pebuy50 = 50 * pemax - pebuy50
                        pebuy100 = 100 * pemax - pebuy100
                        pebuy200 = 200 * pemax - pebuy200

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.StopLossLimit,
                                                   quantity=25,
                                                   price=stoploss + 0.5,
                                                   trigger_price=stoploss + 0.0 ) )

                        print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        while True:
                            pre_time = datetime.datetime.now()
                            print( pre_time )
                            live_ce_price = getprice( instrument=instrumentce )
                            print( live_ce_price, "=", ce_price )
                            print( live_ce_price, " -", percentagece, "=", ce_price )
                            time.sleep( sec )
                            if (live_ce_price >= cedayhigh + (cedayhigh / 100 * percentagece)):
                                stoploss = cedayhigh + cedayhigh / 100 * (percentagece - 7)
                                stoploss = round( stoploss + 0.00, 1 )
                                percentagece = percentagece + 7
                                print( live_ce_price, " -", percentagece )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentce,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["ce_stoploss"],
                                                           order_type=OrderType.StopLossLimit,
                                                           quantity=25,
                                                           price=stoploss + 0.5,
                                                           trigger_price=stoploss + 0.0 ) )
                            if (live_ce_price <= stoploss):
                                print( "ce exit at: ", stoploss, live_ce_price )
                                print( "Entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                cebuy25 = -cebuy25 + 25 * stoploss + pebuy25
                                cebuy50 = -cebuy50 + 50 * stoploss + pebuy50
                                cebuy100 = -cebuy100 + 100 * stoploss + pebuy100
                                cebuy200 = -cebuy200 + 200 * stoploss + pebuy200
                                print( "Exit :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                status = alice.get_order_history( placed_orders["ce_stoploss"] )['data'][0][
                                    'order_status']
                                if (status != "complete"):
                                    print( alice.modify_order( transaction_type=TransactionType.Sell,
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
                                print( "ce exit at: ", stoploss, live_ce_price )
                                print( "Entry :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                cebuy25 = -cebuy25 + 25 * stoploss + pebuy25
                                cebuy50 = -cebuy50 + 50 * stoploss + pebuy50
                                cebuy100 = -cebuy100 + 100 * stoploss + pebuy100
                                cebuy200 = -cebuy200 + 200 * stoploss + pebuy200
                                print( "Exit :", cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentce,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["ce_stoploss"],
                                                           order_type=OrderType.Market,
                                                           quantity=25,
                                                           price=0.0,
                                                           trigger_price=None ) )
                                exit = 1
                                break

                    elif (pemax >= pedayhigh + (pedayhigh / 100 * percentagepe)):
                        stoploss = pedayhigh + pedayhigh / 100 * (percentagepe - 7)
                        stoploss = round( stoploss + 0.00, 1 )
                        percentagepe = percentagepe + 7
                        print( pemax, " -", percentagepe )
                        print( "ce exit at: ", cemax )
                        cebuy25 = 25 * cemax - cebuy25
                        cebuy50 = 50 * cemax - cebuy50
                        cebuy100 = 100 * cemax - cebuy100
                        cebuy200 = 200 * cemax - cebuy200

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )

                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.StopLossLimit,
                                                   quantity=25,
                                                   price=stoploss + 0.5,
                                                   trigger_price=stoploss + 0.0 ) )

                        print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                        while True:
                            pre_time = datetime.datetime.now()
                            print( pre_time )
                            live_pe_price = getprice( instrument=instrumentpe )
                            print( live_pe_price, "=", pe_price )
                            print( live_pe_price, " -", percentagepe, "=", pe_price )
                            k = k + 1
                            time.sleep( sec )
                            if (live_pe_price >= pedayhigh + (pedayhigh / 100 * percentagepe)):
                                stoploss = pedayhigh + pedayhigh / 100 * (percentagepe - 7)
                                stoploss = round( stoploss + 0.00, 1 )
                                percentagepe = percentagepe + 7
                                print( live_pe_price, " -", percentagepe )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentpe,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["pe_stoploss"],
                                                           order_type=OrderType.StopLossLimit,
                                                           quantity=25,
                                                           price=stoploss + 0.5,
                                                           trigger_price=stoploss + 0.0 ) )
                            if (live_pe_price <= stoploss):
                                print( "pe exit at: ", stoploss, live_pe_price )
                                print( "Entry : ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                pebuy25 = -pebuy25 + 25 * stoploss + cebuy25
                                pebuy50 = -pebuy50 + 50 * stoploss + cebuy50
                                pebuy100 = -pebuy100 + 100 * stoploss + cebuy100
                                pebuy200 = -pebuy200 + 200 * stoploss + cebuy200
                                print( "Exit :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                status = alice.get_order_history( placed_orders["pe_stoploss"] )['data'][0][
                                    'order_status']
                                if (status != "complete"):
                                    print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                               instrument=instrumentpe,
                                                               product_type=ProductType.Intraday,
                                                               order_id=placed_orders["pe_stoploss"],
                                                               order_type=OrderType.Market,
                                                               quantity=25,
                                                               price=0.0,
                                                               trigger_price=None ) )
                                exit = 1
                                break
                            if pre_time >= exit_time:
                                print( "time is 3pm closed" )
                                print( "pe exit at: ", stoploss, live_pe_price )
                                print( "Entry : ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                pebuy25 = -pebuy25 + 25 * stoploss + cebuy25
                                pebuy50 = -pebuy50 + 50 * stoploss + cebuy50
                                pebuy100 = -pebuy100 + 100 * stoploss + cebuy100
                                pebuy200 = -pebuy200 + 200 * stoploss + cebuy200
                                print( "Exit :", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                           instrument=instrumentpe,
                                                           product_type=ProductType.Intraday,
                                                           order_id=placed_orders["pe_stoploss"],
                                                           order_type=OrderType.Market,
                                                           quantity=25,
                                                           price=0.0,
                                                           trigger_price=None ) )
                                exit = 1
                                break
                    if exit == 1:
                        break

                    elif pre_time >= exit_time:
                        print( "time is 3pm closed" )
                        print( cemax, " -", percentagece )
                        print( "pe exit at: ", pemax )
                        pebuy25 = 25 * pemax - pebuy25
                        pebuy50 = 50 * pemax - pebuy50
                        pebuy100 = 100 * pemax - pebuy100
                        pebuy200 = 200 * pemax - pebuy200
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentpe,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["pe_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        print( pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                        print( pemax, " -", percentagepe )
                        print( "ce exit at: ", cemax )
                        cebuy25 = 25 * cemax - cebuy25
                        cebuy50 = 50 * cemax - cebuy50
                        cebuy100 = 100 * cemax - cebuy100
                        cebuy200 = 200 * cemax - cebuy200
                        print( alice.modify_order( transaction_type=TransactionType.Sell,
                                                   instrument=instrumentce,
                                                   product_type=ProductType.Intraday,
                                                   order_id=placed_orders["ce_stoploss"],
                                                   order_type=OrderType.Market,
                                                   quantity=25,
                                                   price=0.0,
                                                   trigger_price=None ) )
                        print( cebuy25, "-", cebuy50, "-", cebuy100, " ", cebuy200 )
                        exit = 1
                        break
            if exit == 1:
                break
            elif pre_time >= exit_time:
                print( "time is 3pm closed" )
                print( "pe exit at: ", stoploss, live_pe_price )
                print( "Entry= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                pebuy25 = -pebuy25 + 25 * live_pe_price
                pebuy50 = -pebuy50 + 50 * live_pe_price
                pebuy100 = -pebuy100 + 100 * live_pe_price
                pebuy200 = -pebuy200 + 200 * live_pe_price
                print( alice.modify_order( transaction_type=TransactionType.Sell,
                                           instrument=instrumentpe,
                                           product_type=ProductType.Intraday,
                                           order_id=placed_orders["pe_stoploss"],
                                           order_type=OrderType.Market,
                                           quantity=25,
                                           price=0.0,
                                           trigger_price=None ) )
                print( "Profit= ", pebuy25, "-", pebuy50, "-", pebuy100, " ", pebuy200 )
                exit = 1
                break

    if exit == 1:
        i = i - 1
        break

    elif pre_time >= exit_time:
        alice.cancel_order( placed_orders["pe_dayhigh"] )
        alice.cancel_order( placed_orders["ce_dayhigh"] )
        print( "time is 3pm closed" )
        i = i - 1
        break

    # time.sleep(30)





