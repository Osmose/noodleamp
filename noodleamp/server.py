import json
import os
import urllib

import flask
from flask import Flask, render_template, request

from noodleamp import NoodleAmp


app = Flask(__name__)
app.config.from_object('noodleamp.settings')
app.config.from_envvar('NOODLEAMP_SETTINGS')

app.player = NoodleAmp()
playable_ext = ('mp3', 'ogg', 'wav', 'py')


def normalize_library_path(path):
    path = os.path.realpath(os.path.join(app.config['LIBRARY_ROOT'], path))
    root = os.path.realpath(app.config['LIBRARY_ROOT'])
    if os.path.commonprefix((path, root)) != root:
        return None
    return path


def is_playable(path):
    _, ext = os.path.splitext(path)
    return ext[1:] in playable_ext


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play/', methods=['POST'])
def play():
    path = request.form.get('path', None)
    if path:
        path = normalize_library_path(path)

    app.player.play(path)
    return json.dumps({'status': 'ok'})


@app.route('/pause/', methods=['POST'])
def pause():
    if app.player.is_playing:
        app.player.pause()
    else:
        app.player.unpaused()
    return json.dumps({'status': 'ok'})


@app.route('/stop/', methods=['POST'])
def stop():
    app.player.stop()
    return json.dumps({'status': 'ok'})


@app.route('/library/', methods=['POST'])
def library():
    path = urllib.unquote(request.form.get('dir', ''))
    norm_path = normalize_library_path(path)
    if norm_path is None:
        flask.abort(403)

    if os.path.isdir(norm_path):
        dir_list = [(os.path.join(norm_path, p), os.path.join(path, p), p) for p
                    in os.listdir(norm_path)]
        files = sorted([p for p in dir_list if os.path.isfile(p[0]) and
                        is_playable(p[0])])
        dirs = sorted([p for p in dir_list if os.path.isdir(p[0])])
        return render_template('directory.html', dirs=dirs, files=files)
    else:
        return flask.abort(404)
