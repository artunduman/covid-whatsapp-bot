import requests
import json
import humanize
from collections import OrderedDict

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from countries import Countries

app = Flask(__name__)
base_url = 'https://corona.lmao.ninja'

important_keys = OrderedDict(
    [('cases', 'cases'),
     ('active', 'active'),
     ('deaths', 'deaths'),
     ('recovered', 'recovered'),
     ('todayDeaths', 'deaths today'),
     ('todayCases', 'new cases today'),
     ('casesPerOneMillion', 'per million cases'),
     ])


def get_help_string():
    string = 'Try typing ' \
          '"Info about Canada and Turkey"' \
          ', "World info" or "Compare Iran and China"\n'
    return string


def get_stats(resp):
    resp_json = json.loads(resp.content)
    template = '{}: {}\n'
    ret = ''
    for key in important_keys.keys():
        numeric_value = resp_json.get(key, '')
        if numeric_value != '':
            ret += template.format(
                important_keys[key].capitalize(),
                humanize.intcomma(int(numeric_value))
            )
    return ret, resp_json


def _compare(country1, country2, raw1, raw2):
    template = '{} has more {}\n'
    ret = ''
    for key in important_keys.keys():
        if raw1[key] > raw2[key]:
            ret += template.format(country1.capitalize(), important_keys[key])
        elif raw2[key] > raw1[key]:
            ret += template.format(country2.capitalize(), important_keys[key])
        else:
            ret += 'Countries have same {}'.format(important_keys[key])
    return ret


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    msg_resp = MessagingResponse()
    msg = msg_resp.message()
    print(incoming_msg)
    countries = [c for c in Countries.values() if c in incoming_msg]

    print('Countries: {}'.format(countries))
    if 'help' in incoming_msg:
        msg.body(get_help_string())
    elif 'north korea' in incoming_msg:
        msg.body('North korea is a black box baby')
    elif len(countries) == 0:
        query_url = base_url + '/all'
        resp = requests.get(query_url)
        print(resp.content)
        if resp.status_code == 200 and b'not found' not in resp.content:
            print(resp.content)
            stats_str, _ = get_stats(resp)
            msg.body(
                "World stats of COVID-19 as of now:\n" + stats_str
            )
        else:
            msg.body("No data found for the given input. Might be a server error\n"
                     + get_help_string())
    else:
        ret_string = ''
        count = 0
        raw_entries = []
        for country in countries:
            resp = requests.get(base_url + '/countries/{}'.format(country))
            print(resp.content)
            if resp.status_code == 200 and b'not found' not in resp.content:
                count += 1
                stats_str, raw = get_stats(resp)
                raw_entries.append(raw)
                ret_string += "COVID-19 statistics of {} as of now:\n".format(country.capitalize()) + stats_str
        if 'compare' in incoming_msg:
            if len(countries) != 2:
                ret_string = 'To compare countries, you should give two country names.\n' \
                             'Given countries are {}'.format(', '.join(countries))
            else:
                comparison_str = _compare(
                    countries[0],
                    countries[1],
                    raw_entries[0],
                    raw_entries[1]
                )
                ret_string += comparison_str

        if count != 0:
            msg.body(ret_string)
        else:
            msg.body("No data found for the given string. Might be a server error\n"
                     + get_help_string())
    return str(msg_resp)
