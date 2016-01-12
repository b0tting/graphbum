#!/usr/bin/python
# coding: utf-8

import facebook
import urllib
import urlparse
import subprocess
import warnings

# Keep Facebook settings like APP_ID


# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)


# Trying to get an access token. Very awkward.
oauth_args = dict(client_secret     = '2c8ca12fd86498eee1ff2c57791d7ab0',
                  client_id = '1603614356580841',
                  grant_type    = 'client_credentials')
oauth_curl_cmd = ['curl',
                  'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
oauth_response = subprocess.Popen(oauth_curl_cmd,
                                  stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE).communicate()[0]
print(oauth_response)
try:
    oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
    print(oauth_access_token)
except KeyError as e:
    print('Unable to grab an access token!')
    print(e)
    
    exit()

graph = facebook.GraphAPI(oauth_access_token)
pat = graph.get_object('MarkOtting')
print(pat['id'])

# Try to post something on the wall.
