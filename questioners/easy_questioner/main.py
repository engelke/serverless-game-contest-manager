import base64
import json
import requests

MINIMUM = 1
MAXIMUM = 10
TARGET = 7
MAX_GUESSES = 20
QUESTIONER = 'easy-questioner'

CONTEST_ROUND = None


def report_score(url, outcome, moves):
    score = {
        'questioner': QUESTIONER,
        'contest_round': CONTEST_ROUND,
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
    global CONTEST_ROUND

    message = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    player_url = message['player_url']
    result_url = message['result_url']
    CONTEST_ROUND = message['contest_round']

    outcome, moves = play_game(player_url)
    report_score(result_url, outcome, moves)
