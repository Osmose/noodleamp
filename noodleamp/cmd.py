import argparse
import gobject
import imp

from noodleamp import NoodleAmp, Playlist


def server(args):
    from noodleamp.server import app
    app.run(debug=True, port=8000)


def play(args):
    filename = args[0]

    noodleamp = NoodleAmp()
    main_loop = gobject.MainLoop()

    # Try importing the file as a module first.
    module = None
    try:
        module = imp.load_source('playlist', filename)
    except:
        pass

    if module:
        playlist = Playlist(module.playlist())
        filename = playlist.next()
        def on_end(noodleamp):
            try:
                noodleamp.play(playlist.next())
            except StopIteration:
                main_loop.quit()
    else:
        def on_end(noodleamp):
            main_loop.quit()

    noodleamp.on_end(on_end)
    noodleamp.play(filename)
    try:
        main_loop.run()
    except KeyboardInterrupt:
        main_loop.quit()


commands = {
    'server': server,
    'play': play,
}


parser = argparse.ArgumentParser(description=globals()['__doc__'],
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('command', choices=commands.keys(), default='play')
parser.add_argument('command_args', nargs='*')


def main():
    args = parser.parse_args()
    return commands[args.command](args.command_args)


if __name__ == '__main__':
    main()
