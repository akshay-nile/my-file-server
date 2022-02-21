import project.dependencies

import os
from socket import gethostname
from project import utilities, streaming
from flask import Flask, render_template, request, redirect, jsonify, make_response


app = Flask(__name__)


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return streaming.favicon(app)


@app.route('/', methods=['GET'])
def welcome():
    path = request.args.get('path')

    if path is not None:
        return redirect(f'/storage?path={path}')

    drives = utilities.drives_info()
    libs, shorts = utilities.shortcuts_info()

    return render_template('welcome.html', drives=drives, meta=gethostname().title(), libraries=libs, shortcuts=shorts)


@app.route('/storage', methods=['GET'])
def home():
    path = request.args.get('path')

    if path is None:
        return redirect('/')

    if os.path.isfile(path):
        return streaming.download(path)
    if os.path.isdir(path):
        return render_template('index.html', meta=path.replace('/', ' / '))

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


if input('Run server on Public IPv6 address? Yes/No: ').strip().lower().startswith('y'):
    ip, port = utilities.ip_v6(), 8849
    utilities.publish_socket(f'[{ip}]:{port}')
else:
    ip, port = utilities.ip_v4(), 8849
    utilities.publish_socket(f'{ip}:{port}')

print()
app.run(host=ip, port=port, debug=False)
