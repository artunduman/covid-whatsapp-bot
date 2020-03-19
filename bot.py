import requests
import re
import json

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from countries import Countries

app = Flask(__name__)
base_url = 'https://corona.lmao.ninja'


def get_help_string():
    string = 'Try typing ' \
          '"Info about Canada and Turkey" ' \
          'or "World info"\n'
    return string


def get_stats(resp):
    resp_json = json.loads(resp.content)
    ret = "Cases: {}\nDeaths: {}\nRecovered: {}\n".format(
        resp_json['cases'],
        resp_json['deaths'],
        resp_json['recovered']
    )
    return ret


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    msg_resp = MessagingResponse()
    msg = msg_resp.message()
    print(incoming_msg)
    countries = [c for c in incoming_msg.split(' ') if c in Countries.values()]
    print('Countries: {}'.format(countries))
    if 'help' in incoming_msg:
        msg.body(get_help_string())
    elif len(countries) == 0:
        query_url = base_url + '/all'
        resp = requests.get(query_url)
        print(resp.content)
        if resp.status_code == 200:
            stats = get_stats(resp)
            print(stats)
            msg.body(
                "World stats of Coronavirus as of today:\n" + get_stats(resp)
            )
        else:
            msg.body("No data found for the given input. Might be a server error\n"
                     + get_help_string())
    else:
        ret_string = ''
        count = 0
        for country in countries:
            resp = requests.get(base_url + '/countries/{}'.format(country))
            if resp.status_code == 200:
                count += 1
                ret_string += "{}'s stats of Coronavirus as of today:\n".format(country) + get_stats(resp)
        if count != 0:
            msg.body(ret_string)
        else:
            msg.body("No data found for the given string. Might be a server error\n"
                     + get_help_string())
    return str(msg_resp)
