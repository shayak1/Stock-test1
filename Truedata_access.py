from fyers_api import accessToken

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
token= "gAAAAABfv9fsZXERao47sPWBA5w5XHui15U-N0WRoFMF58ESHl4e2bsu1Q8NCT3A3qRejF9fMmSw1gkBtHTfoe7rGBUlwe_BJTYNWpy8hA7YkdLWLV7iyG4="

is_async = False #(By default False, Change to True for asnyc API calls.)

fyers = fyersModel.FyersModel(is_async)

print(fyers. get_profile(token = token))

