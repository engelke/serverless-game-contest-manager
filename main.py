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

from datetime import datetime
import uuid
from flask import Flask, request
from google.cloud import datastore


app = Flask(__name__)


@app.route('/', methods=['GET'])
def echo_recent_results():
    page = """
<!doctype html>
<html>
<head>
  <title>Recent Results</title>
</head>
<body>
  <h1>Recent Results</h1>

  <table>
    <thead>
      <tr>
        <th>Timestamp</th>
        <th>Posted Result</th>
      </tr>
    </thead>
    <tbody>
    """
    
    client = datastore.Client()
    query = client.query(kind='Result', order=['-timestamp'])
    for result in query.fetch(limit=20):
        page += """
      <tr>
        <td>{}</td>
        <td>{}</td>
      </tr>
        """.format(result['timestamp'].isoformat(), result['result'])

    page += """
    </tbody>
  </table>
</body>
</html>
    """        

    print(page)
    return page


@app.route('/', methods=['POST'])
def save_result():
    body = request.get_data(as_text=True)
    id = str(uuid.uuid4())
    
    client = datastore.Client()
    key = client.key('Result', id)
    entity = datastore.Entity(key=key)
    entity.update({
        'result': body,
        'timestamp': datetime.utcnow()
    })
    client.put(entity)
    
    return 'Okay'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
