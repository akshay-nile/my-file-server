import os
from datetime import datetime


def remove_chars(string, *chars):
    for char in chars:
        string = string.replace(char, '')
    return string


def item_size(itempath):
    if os.path.isfile(itempath):
        return os.path.getsize(itempath)
    size = 0
    for path, folders, files in os.walk(itempath):
        files = map(lambda file: os.path.join(path, file), files)
        size += sum(map(os.path.getsize, files))
    return size


def deep_search(query, root):
    app_root = os.getcwd()
    for path, folders, files in os.walk(root):
        if path.startswith(app_root):
            continue
        for item in folders + files:
            if query in item.lower():
                yield os.path.join(path, item)


def size_info(itempath):
    foldercount = len([f for f in os.listdir(itempath) if os.path.isdir(os.path.join(itempath, f))])
    filecount = len([f for f in os.listdir(itempath) if os.path.isfile(os.path.join(itempath, f))])
    return f'{foldercount} Folders {filecount} Files'


def date_info(dt):
    return datetime.fromtimestamp(dt).strftime('%d-%m-%y %I:%M:%S %p')


def format_size(b):
    if b > 1024*1024*1024:
        return f'{round(b/1024/1024/1024,2)} GB'
    elif b > 1024*1024:
        return f'{round(b/1024/1024,1)} MB'
    elif b > 1024:
        return f'{round(b/1024)} KB'
    else:
        return f'{b} B'


def format_url(path, is_url=False):
    for c in ('&', '?', '=', "'", '"', '+', '-'):
        path = path.replace(*((c, hex(ord(c)).replace('0x', '%'))[::-1 if is_url else 1]))
    return path


def files_and_folders(path, sortby='name', reverse=False, showhidden=False, search=None):
    files, folders = [], []

    if search is None:
        items = map(lambda p: os.path.join(path, p), os.listdir(path))
    else:
        items = deep_search(search, path)

    for item in items:
        itemname = item.split('/')[-1]

        if itemname[0] == '.' and not showhidden:
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

