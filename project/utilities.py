import os
import stat
from shutil import disk_usage
from datetime import datetime
from pyperclip import paste


def join_path(*args):
    return os.path.join(*args).replace('\\', '/')


def is_hidden(itempath):
    try:
        return bool(os.stat(itempath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        return True


def remove_chars(string, *chars):
    for char in chars:
        string = string.replace(char, '')
    return string


def item_size(itempath):
    if os.path.isfile(itempath):
        return os.path.getsize(itempath)
    size = 0
    for path, folders, files in os.walk(itempath):
        files = map(lambda file: join_path(path, file), files)
        size += sum(map(os.path.getsize, files))
    return size


def deep_search(query, root):
    app_root = os.getcwd().replace('\\', '/')
    for path, folders, files in os.walk(root):
        if path.replace('\\', '/').startswith(app_root):
            continue
        for item in folders + files:
            if query in item.lower():
                yield join_path(path, item)


def size_info(itempath):
    foldercount = len([f for f in os.listdir(itempath) if os.path.isdir(join_path(itempath, f))])
    filecount = len([f for f in os.listdir(itempath) if os.path.isfile(join_path(itempath, f))])
    return f'{foldercount} Folders {filecount} Files'


def date_info(dt):
    return datetime.fromtimestamp(dt).strftime('%d-%m-%y %I:%M:%S %p')


def format_size(b):
    if b > 1024*1024*1024:
        return f'{round(b/1024/1024/1024, 2)} GB'
    elif b > 1024*1024:
        return f'{round(b/1024/1024, 1)} MB'
    elif b > 1024:
        return f'{round(b/1024)} KB'
    else:
        return f'{b} B'


def format_url(path, is_url=False):
    for c in ('&', '?', '=', "'", '"', '+', '-'):
        path = path.replace(*((c, hex(ord(c)).replace('0x', '%'))[::-1 if is_url else 1]))
    return path


def drives_info():
    drives = []

    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        path = letter + ':/'
        if os.path.exists(path):
            total, used, free = map(format_size, disk_usage(path))
            drives.append({'name': 'Drive ' + path, 'path': path, 'icon': 'driveicon.jpg',
                           'sizeinfo': {'total': total, 'used': used, 'free': free}})
    return drives


def shortcuts_info():
    libs, extras = [], []

    try:
        userpath = f"C:/Users/{os.getenv('USERNAME')}"
        if not os.path.exists(userpath):
            userpath = os.getenv('USERPROFILE')
            if not os.path.exists(userpath):
                raise Exception()
        else:
            user = userpath.split('/')[-1].split()[0]
            extras.append({'name': user, 'path': userpath, 'icon': 'user.jpg'})

        for lib in 'Documents Pictures Music Videos'.split():
            libpath = f'{userpath}/{lib}'
            if os.path.exists(libpath):
                libs.append({'name': lib, 'path': format_url(libpath), 'icon': lib.lower() + '.jpg'})

        downpath = userpath + '/Downloads'
        if os.path.exists(downpath):
            extras.append({'name': 'Downloads', 'path': format_url(downpath), 'icon': 'downloads.jpg'})

        clipboard = paste().replace('\\', '/').replace('"', '')
        if os.path.exists(clipboard):
            extras.append({'name': 'Clipboard', 'path': format_url(clipboard),
                           'icon': 'clipfolder.jpg' if os.path.isdir(clipboard) else 'clipfile.jpg'})
    except Exception:
        print('\nWarning: Unable to find libraries\n')

    return libs, extras


def files_and_folders(path, sortby='name', reverse=False, showhidden=False, search=None):
    files, folders = [], []

    if search is None:
        items = map(lambda p: join_path(path, p), os.listdir(path))
    else:
        items = deep_search(search, path)

    for item in items:
        itemname = item.split('/')[-1]

        if itemname[0] in '.$' or is_hidden(item) and not showhidden:
            continue

        if search is None:
            itemname = remove_chars(itemname, "'", '"')
        else:
            itemname = item.replace(path if path[-1] != '/' else path[:-1], '.').replace('/', ' / ')

        iteminfo = {'path': format_url(item), 'name': itemname, 'type': itemname.split('.')[-1]}

        if sortby == 'size':
            iteminfo['size'] = item_size(item)

        try:
            if os.path.isdir(item):
                iteminfo['sizeinfo'] = size_info(item)
                iteminfo['dateinfo'] = date_info(os.path.getctime(item))
                iteminfo['date'] = int(os.path.getctime(item))
                folders.append(iteminfo)
            elif os.path.isfile(item):
                iteminfo['thumbid'] = remove_chars(itemname, ' ')
                iteminfo['sizeinfo'] = format_size(os.path.getsize(item))
                iteminfo['dateinfo'] = date_info(os.path.getmtime(item))
                iteminfo['date'] = int(os.path.getmtime(item))
                files.append(iteminfo)
        except PermissionError:
            print('Access Denied:', item)
            continue

    files.sort(key=lambda x: x[sortby], reverse=reverse)
    folders.sort(key=lambda x: x[sortby], reverse=reverse)

    return files, folders
