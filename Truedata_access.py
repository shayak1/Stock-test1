from fyers_api import accessToken
import pandas as pd

from fyers_api import fyersModel

app_id = "MPR9R5RV4H"

app_secret = "IPOW37QERP"
'''
app_session = accessToken.SessionModel(app_id, app_secret)

response = app_session.auth()

authorization_code = response['data']['authorization_code']
print(authorization_code)
app_session.set_token(authorization_code)

URL= app_session.generate_token()
print(URL)
'''
token= "gAAAAABf6qAB7IwmEuaE4y7TDL4XduUqdzOOA3tXhbXf5r8NaeXaIn3pBjcaXGY2Iovp2F3CvC9iGTdsK85GUAy2hkWgnAv30rp6rqTnsWG_46SlEKznj8M="

is_async = False #(By default False, Change to True for asnyc API calls.)


fyers = fyersModel.FyersModel(is_async)

print(fyers. get_profile(token = token))

from truedata_ws.websocket.TD import TD

td_obj = TD('FYERS588', 'RoMOyPcs', broker_token=token)
from dateutil.relativedelta import relativedelta
hist_data_5 = td_obj.get_historic_data('CRUDEOIL20JANFUT')

df = pd.DataFrame(hist_data_5)
print(df.head())

