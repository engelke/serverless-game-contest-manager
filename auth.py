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
import os
import requests

KEYS = None     # Cached public keys for verification


# Google publishes the public keys needed to verify a JWT. Save them in KEYS.
def refresh_keys():
    global KEYS
    try:
        resp = requests.get('https://www.gstatic.com/iap/verify/public_key')
        KEYS = resp.json()
    except:
        # KEYS is stale (not good, but not disastrous) or missing (very bad)
        if resp:
            message = 'Status {}: {}'.format(resp.status_code, resp.text)
        else:
            message = 'None'
        logging.critical('Key fetching failed, returned ' + message)


# Return the authenticated user's email address if available from Cloud
# Identity Aware Proxy (IAP). If IAP is not active, returns None.
#
# Raises an exception if IAP header exists, but JWT token is invalid, which
# would indicates bypass of IAP or inability to fetch KEYS.
def email():
    assertion = request.headers.get('x-goog-iap-jwt-assertion')
    if assertion is None:   # Request did not come through IAP
        return None

    if KEYS is None:
        refresh_keys()

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', None)
    project_number = os.getenv('PROJECT_ID')

    info = jwt.decode(
        assertion, 
        KEYS, 
        algorithms=['ES256'], 
        audience='/projects/{}/apps/{}'.format(project_id, project_number)
    )
    
    return info['email']
