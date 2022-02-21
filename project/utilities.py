import os
from threading import Thread
from shutil import disk_usage
from datetime import datetime
from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6
from requests import post


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

    def get_details(dev, path):
        total, used, free = map(format_size, disk_usage(path))
        return {'name': dev, 'path': path, 'icon': 'driveicon.jpg', 'sizeinfo': {'total': total, 'used': used, 'free': free}}

    drives.append(get_details('System', '/'))

    for dev in os.listdir('/mnt'):
        drives.append(get_details(dev, f'/mnt/{dev}'))

    for dev in os.listdir(f'/media/{os.getenv("USERNAME")}'):
        drives.append(get_details(dev, f'/media/{os.getenv("USERNAME")}/{dev}'))

    return drives


def shortcuts_info():
    libs, extras = [], []

    try:
        user = os.getenv('USERNAME')
        userpath = "/home/" + user
        extras.append({'name': user, 'path': userpath, 'icon': 'user.jpg'})

        for lib in 'Documents Pictures Music Videos'.split():
            libpath = os.path.join(userpath, lib)
            if os.path.exists(libpath):
                libs.append({'name': lib, 'path': format_url(libpath), 'icon': lib.lower() + '.jpg'})

        downpath = os.path.join(userpath, 'Downloads')
        if os.path.exists(downpath):
            extras.append({'name': 'Downloads', 'path': format_url(downpath), 'icon': 'downloads.jpg'})
    except Exception:
        print('\nWarning: Unable to find libraries\n')

    return libs, extras


def files_and_folders(path, sortby='name', reverse=False, showhidden=False, search=None):
    files, folders = [], []

    if search is None:
        items = map(lambda p: os.path.join(path, p), os.listdir(path))
    else:
        items = deep_search(search, path)

    for item in items:
        itemname = item.split('/')[-1]

        if itemname[0] in '.$' and not showhidden:
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


def get_ip_addresses(intf='*', iptype='*', ignore='lo'):
    if intf not in '* all'.split():
        addrs = ifaddresses(intf)
        if iptype.endswith('4'):
            return addrs.get(AF_INET)[0]['addr']
        if iptype.endswith('6'):
            return addrs.get(AF_INET6)[0]['addr']
        return addrs.get(AF_INET)[0]['addr'], addrs.get(AF_INET6)[0]['addr']

    intfs = []
    for intf in interfaces():
        if intf in ignore.split():
            continue
        if ifaddresses(intf).get(AF_INET):
            addrs = ifaddresses(intf)
            intfs.append((intf, addrs.get(AF_INET)[0]['addr'], addrs.get(AF_INET6)[0]['addr']))

    return intfs


def ip_v4():
    try:
        ipv4 = get_ip_addresses()[0][1]
    except IndexError:
        print('\nWi-LAN interface is not available!')
        if input('Run server on localhost? Yes/No: ').strip().lower().startswith('y'):
            return '127.0.0.1'
        exit()

    return ipv4


def ip_v6():
    try:
        ipv6 = get_ip_addresses()[0][2]
    except IndexError:
        print('\nUnable to extract IPv6 Address for this device!')
        input('Press ENTER key to exit.')
        exit()

    return ipv6 if '%' not in ipv6 else ipv6[:ipv6.index('%')]


def publish_socket(sock):
    def mysocket():
        try:
            res = post(f'https://akshaynile.pythonanywhere.com/mysocket?socket={sock}')
            if res.text == 'success':
                print(' * Socket publication was successful ✔️\n')
        except Exception:
            print(' * Socket publication attempt failed ❌\n')

    Thread(target=mysocket).start()
