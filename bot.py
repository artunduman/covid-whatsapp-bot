import requests
import re
import json

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
playlist_id = '0Voksg4xZg5H14j3PVp9F2'
client_id = 'da437917030c458bb34b1282eaac1725'
client_secret = '247c471caf964a8e86e24b680e2cd402'
spotify_code = ''

def get_spotify_token():
    # url = 'https://accounts.spotify.com/authorize?client_id={}&response_type=code&' \
    #       'redirect_uri=http%3A%2F%2F51f34525.ngrok.io%2Fspotify'.format(client_id)
    grant_type = 'client_credential'

    body_params = {'grant_type': grant_type}

    url = 'https://accounts.spotify.com/api/token'

    response = requests.post(url, data=body_params, auth=(client_id, client_secret))
    content = json.loads(response.content.decode('utf-8'))
    return content['access_token'], content['expires_in']

@app.route('/spotify')
def spotify_callback():
    code = request.values.get('code', '')
    if code:
        spotify_code = code

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if "open.spotify.com/track" in incoming_msg:
        spotify_url = re.search("(?P<url>https?://[^\s]+)", incoming_msg).group("url")
        track_id = spotify_url.split('/')[-1].split('?')[0]
        spotify_request_uri = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
        body = {
            "uris": [
                "spotify:track:{}".format(track_id)
            ]
        }
        token, _ = get_spotify_token()
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(token)
        }
        print(body)
        print(headers)
        r = requests.post(url=spotify_request_uri, json=body, headers=headers)
        print(r.content, r.status_code)
        if r.status_code == 200:
            msg.body('The song has been added to the playlist')
        else:
            msg.body("I see that you are sharing a song, but I couldn't add it to playlist")
        responded = True
    if not responded:
        msg.body("This text doesn't include a song to add")
    return str(resp)
