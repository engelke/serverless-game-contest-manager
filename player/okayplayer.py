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

import json


# This guesser will succeed... eventually!
def make_guess(request):
    game = request.get_json()

    min = game['minimum']

    for old_guess in game['history']:
        if old_guess['result'] == 'higher': # The minimum is at least one more
            new_min = old_guess['guess'] + 1
            if new_min > min:
                min = new_min

    guess = min

    return json.dumps(guess)
