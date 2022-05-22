import project.dependencies

import os
from project import utilities, streaming, network
from flask import Flask, render_template, request, jsonify, make_response


app = Flask(__name__)


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return streaming.favicon(app)


@app.route('/', methods=['GET'])
def home():
    path = request.args.get('path')

    if path is None:
        path = root

    if os.path.isfile(path):
        return streaming.download(path)
    if os.path.isdir(path):
        meta = path.replace(root, 'Internal Storage').replace('/', ' / ')
        return render_template('index.html', meta=meta)

    return f'<br> <h1 align="center"> Path not found ! <br> {path} </h1>'


@app.route('/body', methods=['GET'])
def body():
    path = request.args.get('path')
    search = request.args.get('search')

    newcookie = request.args.get('cookie')
    oldcookie = request.cookies.get('settings')

    settings = oldcookie if newcookie is None else newcookie
    if settings is None:
        settings = 'name False False'

    val = settings.split()
    files, folders = utilities.files_and_folders(path, sortby=val[0], reverse=eval(val[1]), showhidden=eval(val[2]), search=search)

    response = make_response(render_template('body.html', files=files, folders=folders), 200)
    response.headers['Settings'] = settings

    if newcookie is not None or newcookie is None and oldcookie is None:
        response.set_cookie('settings', settings, max_age=90*24*60*60)
        print('New cookie set =', {'sortby': val[0], 'reverse': eval(val[1]), 'showhidden': eval(val[2])})

    return response


@app.route('/upload', methods=['POST'])
def upload():
    return streaming.upload(request)


@app.route('/open', methods=['GET'])
def stream():
    return streaming.stream(request)


@app.route('/thumbnails', methods=['POST'])
def thumbnails():
    return jsonify({'thumbnails': streaming.thumbnails(request, app)})


root = '/storage/emulated/0'

host, port = network.user_selection(), 8849
network.publish_socket(f'{host}:{port}' if host.count('.') == 3 else f'[{host}]:{port}')

os.system('clear')
app.run(host=host, port=port, debug=False)
