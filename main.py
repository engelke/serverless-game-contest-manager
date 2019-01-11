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
from flask import Flask, redirect, render_template, request
import json
import os
import uuid

from google.cloud import datastore
from google.cloud import pubsub


app = Flask(__name__)


@app.route('/', methods=['GET'])
def echo_recent_results():
    client = datastore.Client()
    query = client.query(kind='Trial', order=['-timestamp'])
    trials = [
        {
            'timestamp': entity['timestamp'].isoformat(),
            'user': entity['user'],
            'player_url': entity['player_url'],
            'key': entity.key,
            'runs': []
        } for entity in query.fetch()
    ]

    for trial in trials:
        query = client.query(
            kind='Result', 
            order=['-questioner'], 
            ancestor=trial['key']
        )
        for entity in query.fetch():
            trial['runs'].append({
                'questioner': entity['questioner'],
                'outcome': entity['outcome'],
                'moves': entity['moves']
            })
    
    page = render_template('index.html', trials=trials)
    return page


@app.route('/request-trial', methods=['GET'])
def trial_form():
    return render_template('trial_form.html')


@app.route('/request-trial', methods=['POST'])
def start_trial():
    user = request.form['user']
    player_url = request.form['player_url']

    contest_round = str(uuid.uuid4())
    timestamp = datetime.utcnow()

    client = datastore.Client()
    key = client.key('Trial', contest_round)
    entity = datastore.Entity(key=key)
    entity.update({
        'user': user,
        'player_url': player_url,
        'timestamp': timestamp
    })
    client.put(entity)

    publisher = pubsub.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
        topic='play-a-game'
    )
    
    payload = {
        'contest_round': contest_round,
        'player_url': player_url,
        'result_url': 'https://{project_id}.appspot.com/report-result'.format(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT')
        )
    }
    
    publisher.publish(topic_name, json.dumps(payload).encode())
    return redirect('/', code=302)


@app.route('/report-result', methods=['POST'])
def save_result():
    result = request.get_json()
    if result is None:
        return 415  # Was not sent application/json, can't handle it

    client = datastore.Client()
        
    contest_round = result['contest_round']
    outcome = result['outcome']
    moves = result['moves']
    questioner = result['questioner']

    trial_key = client.key('Trial', contest_round)
    trial_entity = client.get(trial_key)
    if trial_entity is None:
        return 404  # A result we never asked for
    
    result_id = str(uuid.uuid4())
    result_key = client.key('Result', result_id, parent=trial_key)
    result_entity = datastore.Entity(key=result_key)
    result_entity.update({
        'questioner': questioner,
        'outcome': outcome,
        'moves': moves
    })
    client.put(result_entity)
    
    return 'Okay'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
