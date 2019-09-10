import base64
import json
import requests

MINIMUM = 0
MAXIMUM = 1000000000
TARGET = 3
MAX_GUESSES = 100
QUESTIONER = 'hard-questioner'


def report_score(url, outcome, moves, contest_round, secret):
    score = {
        'questioner': QUESTIONER,
        'contest_round': contest_round,
        'secret': secret,
        'outcome': outcome,
        'moves': moves
    }
    requests.post(url, data=json.dumps(score),
        headers={'Content-type': 'application/json'}
    )


def play_game(url):
    # Keep track of the plays in this game to provide for each guess
    state = {
        'minimum': MINIMUM,
        'maximum': MAXIMUM,
        'history': []
    }

    # Give the player MAX_GUESSES tries to find the TARGET
    for guess_number in range(1, MAX_GUESSES+1):
        try:
            player_response = requests.post(url, data=json.dumps(state),
                headers={'Content-type': 'application/json'}
            )
            guess = player_response.json()
            if guess == TARGET:
                # Done. Exit loop by returning outcome
                return 'won', guess_number
            if guess < TARGET:
                state['history'].append({'guess': guess, 'result': 'higher'})
            else:
                state['history'].append({'guess': guess, 'result': 'lower'})
        except:
            # Player could not return a valid response
            return 'crashed', guess_number

    # Give up after MAX_GUESSES
    return 'failed', MAX_GUESSES


def question_player(event, context):
    message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    player_url = message['player_url']
    result_url = message['result_url']
    contest_round = message['contest_round']
    secret = message['secret']

    outcome, moves = play_game(player_url)
    report_score(result_url, outcome, moves, contest_round, secret)
