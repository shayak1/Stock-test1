from fyers_api import accessToken
import pandas as pd

# for webdriver and login automation
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse

from fyers_api import fyersModel

app_id = "MPR9R5RV4H"
app_secret = "IPOW37QERP"

app_session = accessToken.SessionModel(app_id, app_secret)
response = app_session.auth()
print(response)
'''
# df = pd.DataFrame.from_dict(response, orient='index')
'''
authorization_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqaGdqZzg3NiQ3ODVidjVANjQ3NTZ2NSZnNyM2OTg3Njc5OHhkIjoiTVBSOVI1UlY0SCIsImV4cCI6MTYwNDM3Njc1OS42OTI4MjN9.LK-jHejh2UZWSPfQsUJC_PiJw8f11TSbp-4G8qgSEYI"
print("https://api.fyers.in/api/v1/genrateToken?authorization_code="+authorization_code+"&appId="+app_id)

# app_session.set_token(authorization_code)
# app_session.generate_token()

token = "gAAAAABfaeqD8KfVVPj75gh5OiU5u0cvzOVL3GDmTWx9ex7SgSmImunzpqlpSvsrFwvYm3eXzhi5WiGkGkyYuO9-mqahc9ru87d4iaFv9MU8pMrCIzE-gYU"
is_async = False #(By default False, Change to True for asnyc API calls.)
fyers = fyersModel.FyersModel(is_async)

print(fyers)
print(fyers.get_profile(token=token))





