from flask import Flask, request

from noodleamp import NoodleAmp


app = Flask(__name__)
player = NoodleAmp()


@app.route('/')
def index():
    return 'test'


@app.route('/play/', methods=['POST'])
def play():
    url = request.form['url']
    if url:
        player.play(url)
    return 'ok'
