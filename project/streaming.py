import io
import os

from flask import make_response, redirect, send_file
from mutagen.id3 import ID3
from PIL import Image
from pyautogui import FailSafeException, press

from project.utilities import format_url


def favicon(app):
    favpath = os.path.join(app.root_path, 'static', 'images', 'favicon', 'favicon.ico')
    return send_file(favpath, mimetype='image/vnd.microsoft.icon')


def download(path):
    filename = path.split('/')[-1]
    response = send_file(path, as_attachment=True, cache_timeout=-1)

    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Accept-Ranges'] = 'none'

    return response


def upload(req):
    try:
        savepath = f"/home/{os.getenv('USERNAME')}/Downloads"
        if not os.path.exists(savepath):
            raise Exception()
    except Exception:
        print('\nWarning: Download path not found.\n')
        if not os.path.isdir('Uploads'):
            os.mkdir('Uploads')
        savepath = 'Uploads'

    for file in req.files.getlist('files'):
        file.save(f'{savepath}/{file.filename}')
        print(file)

    return redirect(f'/storage?path={format_url(savepath)}')


def stream(req):
    path = req.args.get('path')
    size = os.path.getsize(path)

    extension = path[path.rfind('.') + 1:].lower()
    range_header = req.headers.get('Range')

    if range_header is not None:
        try:
            press('ctrl')
        except FailSafeException:
            pass

        start, end = range_header.split('=')[-1].strip().split('-')
        start = int(start)

        if end.isnumeric():
            end = int(end)
            block = end - start + 1
        else:
            end = size - 1
            block = 1024*1024

        with open(path, 'rb') as file:
            file.seek(start, 0)
            data = file.read(block)

        response = make_response(data, 206)
        response.headers['Content-Range'] = f'bytes {start}-{end}/{size}'
    else:
        response = send_file(path)

        if extension in 'mkv mp4 3gp avi wmv flv vob':
            response.headers['Content-Type'] = 'video/mp4'
        elif extension in 'aac mp3 wav m4a ogg':
            response.headers['Content-Type'] = 'audio/' + extension
        elif extension in 'jpg jpeg png ico gif tiff svg':
            response.headers['Content-Type'] = 'image/jpeg'
        elif extension in 'txt html xml js py c cpp java css csv h asm cmd':
            response.headers['Content-Type'] = 'text/plain'

    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = f'{size}'
    return response


def thumbnail(data, thumbname, root):
    buffer = io.BytesIO(data)
    thumbimg = Image.open(buffer)
    thumbimg.thumbnail((64, 64))
    thumbimg.save(os.path.join(root, 'static', 'images', 'thumbnails', thumbname))
    buffer.close()
    return 'static/images/thumbnails/' + format_url(thumbname)


def thumbnails(req, app):
    # path = req.args.get('path')
    root = app.root_path
    res = []

    for line in req.get_data().decode('utf-8').split('\n'):
        try:
            fileurl, thumbid = eval(line)
            filepath = format_url(fileurl, is_url=True)
            filename = filepath.split('/')[-1]
            extension = filename[filename.rfind('.') + 1:].lower()
        except Exception:
            continue

        if not extension:
            continue

        thumbname = filename + '.png'
        thumbpath = None

        if os.path.exists(os.path.join(root, 'static', 'images', 'thumbnails', thumbname)):
            thumbpath = 'static/images/thumbnails/' + format_url(thumbname)
        elif extension in 'mp3':
            try:
                album_art = ID3(filepath)['APIC:'].data
                thumbpath = thumbnail(album_art, thumbname, root)
            except Exception:
                thumbpath = 'static/images/default/mp3.png'
        elif extension in 'jpg jpeg png ico':
            try:
                with open(filepath, 'rb') as file:
                    thumbpath = thumbnail(file.read(), thumbname, root)
            except Exception:
                thumbpath = f'static/images/default/{extension}.png'
        elif os.path.exists(os.path.join(root, 'static', 'images', 'default', extension + '.png')):
            thumbpath = f'static/images/default/{extension}.png'

        if thumbpath is not None:
            res.append({'thumbid': thumbid, 'thumbpath': thumbpath})

    return res
