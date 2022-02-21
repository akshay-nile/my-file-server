import os


def install(module):
    print(f'\nInstalling "{module}" ...\n')
    os.system(f'pip install {module}')
    print('\nDone.\n')


try:
    import flask
except ImportError:
    install('flask')

try:
    import mutagen.id3
except ImportError:
    install('mutagen')

try:
    import PIL.Image
except ImportError:
    install('pillow')

try:
    import netifaces
except ImportError:
    install('netifaces')

try:
    import requests
except ImportError:
    install('requests')
