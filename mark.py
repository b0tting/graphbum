import json
import urllib 

from oauth_tokens.providers.facebook import FacebookAuthRequest
req = FacebookAuthRequest(username='otster@hotmail.com', password='74Dollars')
response = req.authorized_request(url='https://facebook.com')
response.content.count(USER_FULL_NAME)
