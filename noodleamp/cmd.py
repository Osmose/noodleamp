import argparse
import gobject

from noodleamp import NoodleAmp


def server(args):
    from noodleamp.server import app
    app.run(debug=True, port=8000)


def play(args):
    filename = args[0]

    noodleamp = NoodleAmp()
    main_loop = gobject.MainLoop()

    @noodleamp.on_end
    def on_end(noodleamp):
        main_loop.quit()

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
