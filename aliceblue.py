from alice_blue import *
print(AliceBlue)
access_token = AliceBlue.login_and_get_access_token(username='AB044026', password='KOP@123', twoFA='silver',  api_secret='GGSTJRYIP7UCZUJ9TW49X0VZM4VL6447AVQQFAKSVI4SGRP2G4ODQTGPV2HP6MLV')
alice = AliceBlue(username='AB044026', password='KOP@123', access_token=access_token)
print(alice.get_balance()) # get balance / margin limits
print(alice.get_profile()) # get profile

alice = AliceBlue(username='username', password='password', access_token=access_token, master_contracts_to_download=['NSE', 'BSE', 'MCX'])

print (alice.get_profile())

# TransactionType.Buy, OrderType.Market, ProductType.Delivery

print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%1%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
print(
   alice.place_order(transaction_type = TransactionType.Buy,
                     instrument = alice.get_instrument_by_symbol('NSE', 'SBIN'),
                     quantity = 1,
                     order_type = OrderType.Limit,
                     product_type = ProductType.Intraday,
                     price = 186.00,
                     trigger_price = None,
                     stop_loss = None,
                     square_off = None,
                     trailing_sl = None,
                     is_amo = True)
   )

alice.cancel_order('200928000298652') #Cancel an open order