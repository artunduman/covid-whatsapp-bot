#Covid Whatsapp Bot

A Whatsapp chatbot to get the latest COVID-19 information

### Prerequisites

You need Python3 installed on your machine. Once you have that,
create a virtual environment and install requirements

```
python3 -m venv whatsapp-bot-venv
source whatsapp-bot-venv/bin/activate
pip3 install -r 
```
You are ready to run the server
```
gunicorn -b :5000 bot:app
```

### Whatsapp Integration

To see it running you need to create a twilio account.
Create a whatsapp sandbox, and channel your local server by
```
./ngrok http 5000
```

Then you can give a post endpoint to twilio with /bot path.

Send 'help me' to the sandbox to get tips.

