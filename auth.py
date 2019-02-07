# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import request
from jose import jwt
import requests

KEYS = None


def refresh_keys():
    global KEYS
    try:
        resp = requests.get('https://www.gstatic.com/iap/verify/public_key')
        KEYS = resp.json()
    except:
        pass    # TODO: log this event


# Return the authenticated user's email address.
#
# Raises an exception if no such user (indicates IAP configuration error), or
# JWT token is invalid (indicates bypass of IAP)
def email():
    if KEYS is None:
        refresh_keys()

    assertion = request.headers.get('x-goog-iap-jwt-assertion')
    info = jwt.decode(
        assertion, 
        KEYS, 
        algorithms=['ES256'], 
        audience='/projects/470716193886/apps/engelke-game-player'
    )
    
    return info['email']
