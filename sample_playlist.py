import os


def path(*a):
    return os.path.join('/Users', 'mkelly', 'Music', *a)


def playlist():
    yield path('Misc', 'item-loop.mp3')
    yield path('Misc', '01_Kirby\'s Adventure.mp3')
