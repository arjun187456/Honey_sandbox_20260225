from AliceBlue_V2 import Alice
from datetime import datetime, timedelta
import time


user_id='593605'
api_key='A5XTjuqDNZVsH5kILiDSqcig5Gcnc8baeZ4zejc0aifx4D3WSm3ITX1TjXxFOW1A7Qz3AJbUYvGmNVJXfKKGvWHxJHijNNbRlg6NAL957C6U8oyCPl90K5TmbBQUc2ds'


alice = Alice(user_id=user_id, api_key=api_key)
print(alice.create_session())       # Must "log in" to Alice platform before create session
alice.download_master_contract(to_csv=True)

print(alice.get_profile())
print(alice.get_balance())
print(alice.get_orderbook())
print(alice.get_trade_book())
print(alice.get_positions(alice.POSITION_DAYWISE))
print(alice.get_positions(alice.POSITION_NETWISE))
print(alice.get_holdings())

# instrument = alice.get_instrument_by_symbol( "NFO", "RELIANCE" )
# instrument2=alice.get_instrument_by_symbol("NSE", "NIFTY BANK")
# print(alice.get_instrument_by_symbol("NSE", "NIFTY BANK"))
# # instrument2 = alice.get_instrument_for_fno( exch="NFO", symbol='BANKNIFTY', expiry_date="15-9-2022", is_fut=False,
# #                                             strike=40000, is_CE=True )
# print( instrument2 )
# from_datetime = datetime.now() - timedelta( days=7 )  # From last & days
# to_datetime = datetime.now()  # To now
# interval = "15"  # ["1", "2", "3", "4", "5", "10", "15", "30", "60", "120", "180", "240", "D", "1W", "1M"]
# indices = False  # For Getting index data
# print( alice.get_historical( instrument2, from_datetime, to_datetime, interval, indices ) )

instrument = alice.get_instrument_by_symbol("NSE", "LUPIN-EQ")
from_datetime = datetime.now() - timedelta(days=7)     # From last & days
to_datetime = datetime.now()                                    # To now
interval = "1"       # ["1", "2", "3", "4", "5", "10", "15", "30", "60", "120", "180", "240", "D", "1W", "1M"]
indices = False      # For Getting index data
print(alice.get_historical(instrument, from_datetime, to_datetime, interval, indices))

socket_opened = False


def event_handler_quote_update(message):
    print(message)
    global LTP
    LTP = message[
        'lp'] if 'lp' in message else LTP
    print( LTP )


def open_callback():
    global socket_opened
    socket_opened = True


alice.invalidate_socket_session()
alice.create_socket_session()
alice.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)
while not socket_opened:
    pass
print("Websocket : Connected")

alice.subscribe( [alice.get_instrument_by_symbol( "NSE","RELIANCE-EQ")])
time.sleep(1)
alice.unsubscribe([alice.get_instrument_by_symbol("NSE","RELIANCE-EQ")])
time.sleep(1)
alice.subscribe( [alice.get_instrument_by_symbol( "NSE","ACC-EQ")])
time.sleep(1)
alice.unsubscribe([alice.get_instrument_by_symbol("NSE","ACC-EQ")])

instrumentce = alice.get_instrument_for_fno("NFO", "BANKNIFTY", is_fut=False, expiry_date=datetime.date(2022, 9, 15), strike=40000, is_CE=True)
 # alice.subscribe([alice.get_instrument_by_symbol("NSE", i) for i in ["ACC-EQ", "RELIANCE-EQ", "UPL-EQ", "LUPIN-EQ"]])
# time.sleep(30)
# alice.unsubscribe([alice.get_instrument_by_symbol("NSE", i) for i in ["ACC-EQ", "RELIANCE-EQ"]])
# time.sleep(10)
time.sleep(1)
alice.subscribe( [instrumentce])
time.sleep(1)
alice.unsubscribe([instrumentce])